from flask import Flask, request, jsonify
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
from datetimerange import DateTimeRange
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime, timedelta
import os
from faker import Faker
import random
from sqlalchemy.exc import SQLAlchemyError


# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'employees.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

app.app_context().push()

# Employee Class/Model
class Employee(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
  department = db.Column(db.String(50))
  salary = db.Column(db.Float, db.CheckConstraint('salary > 0 AND salary < 1000000'))
#   current_datetime = db.Column(db.DateTime(timezone=True), default=func.now())
#   hire_date = db.Column(db.DateTime, db.CheckConstraint(
#     'hire_date >= "2020-01-01 00:00:00" AND hire_date <= current_datetime'
#   )
# )
  hire_date = db.Column(db.DateTime)
  
  
  def __init__(self, name, department, salary, hire_date):
    self.name = name
    self.department = department
    self.salary = salary
    self.hire_date = hire_date

# Employee Schema
class EmployeeSchema(ma.Schema):
  class Meta:
    fields = ('id', 'name', 'department', 'salary', 'hire_date')

  hire_date = ma.DateTime('%Y-%m-%d %H:%M:%S', required=True, validate=lambda d: datetime(2020, 1, 1) <= d <= datetime.now())
  salary = ma.Float(required=True, validate=lambda s: 0 <= s <= 1000000)

# Init schema
employees_schema = EmployeeSchema(many=True, strict = True)


#get all employees
@app.route('/employees', methods=['GET'])
def get_all_employees():
    all_employees = Employee.query.all()
    result = employees_schema.dump(all_employees)
    return jsonify(result)

#get an employee with a specific ID
@app.route('/employees/<int:id>', methods=['GET'])
def get_employee_with_id(id):
    employee = Employee.query.get(id)
    if employee:
        result = EmployeeSchema().dump(employee)
        return jsonify(result)
    else:
        return jsonify({'error': 'Employee not found'}), 404


#adds a new employee, returns the ID as response
@app.route('/employees',methods=['POST'])
def add_employee():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    try:
        name = data.get('name')
        department = data.get('department')
        salary = data.get('salary')
        hire_date_str = data.get('hire_date')
        hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d %H:%M:%S')

        new_employee = Employee(name, department, salary, hire_date)

        db.session.add(new_employee)
        db.session.commit()

        return jsonify({'id': new_employee.id}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    
#update employee info with given ID
@app.route('/employees/<int:id>',methods=['PUT'])
def update_employee(id):
    employee = Employee.query.get(id)
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    if 'name' in data:
        employee.name = data['name']
    if 'department' in data:
        employee.department = data['department']
    if 'salary' in data:
        employee.salary = data['salary']
    if 'hire_date' in data:
        employee.hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d %H:%M:%S')

    try:
        db.session.commit()
        return jsonify({'id': employee.id, 'message': 'Employee information updated'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


#delete employee with specific id
@app.route('/employees/<int:id>',methods=['DELETE'])
def delete_employee(id):
    employee = Employee.query.get(id)
    if employee:
        db.session.delete(employee)
        db.session.commit()
        return jsonify({'id': employee.id, 'message': 'Employee information deleted'})
    else:
        return jsonify({'error': 'Employee not found'}), 404

#return a list with all unique departments  
@app.route('/departments',methods=['GET'])
def get_unique_departments():
    departments = Employee.query.distinct(Employee.department)
    result = [department.department for department in departments]
    return jsonify(result)

#Returns a list of all employees in the specified department
@app.route('/departments/<string:name>',methods=['GET'])
def get_employees_from_specified_department(name):
    employees = Employee.query.filter_by(department=name).all()
    if employees:
        result = EmployeeSchema(many=True).dump(employees)
        return jsonify(result)
    else:
        return jsonify({'error': 'Department not found'}), 404
    
#Returns the average salary of employees in the specified department.
@app.route('/average_salary/<string:department>',methods=['GET'])
def get_average_salary(department):
    employees = Employee.query.filter_by(department=department).all()
    if not employees:
        return jsonify({'error': 'No employees found in this department.'}), 404
    
    total_salary = sum(employee.salary for employee in employees)
    avg_salary = total_salary / len(employees)
    
    return jsonify({'department': department, 'average_salary': avg_salary})

#top 10 salary people
@app.route('/top_earners',methods=['GET'])
def get_top_earners():
    employees = Employee.query.order_by(Employee.salary.desc()).limit(10).all()
    if not employees:
        return jsonify({'error': 'No employees found.'}), 404
    
    result = [{'name': employee.name, 'salary': employee.salary} for employee in employees]
    
    return jsonify(result)

#10 latest hires
@app.route('/most_recent_hires',methods=['GET'])
def get_most_recent_hires():
    employees = Employee.query.order_by(Employee.hire_date.desc()).limit(10).all()
    if not employees:
        return jsonify({'error': 'No employees found.'}), 404
    
    result = [{'name': employee.name, 'hire_date': employee.hire_date} for employee in employees]
    
    return jsonify(result)



fake = Faker()

for i in range(1000):
    employee = Employee(
        name=fake.name(),
        department=fake.job(),
        salary=random.uniform(0, 1000000),
        hire_date=fake.date_time_between_dates(datetime(2020, 1, 1), datetime.now())
    )
    db.session.add(employee)
db.session.commit()


if __name__ == '__main__':
  app.run(debug=True)