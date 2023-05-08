from flask import Flask, request, jsonify
import joblib
import pandas as pd
import sqlite3

app = Flask(__name__)

model = joblib.load('model.joblib')


@app.route('/predict_salary', methods=['POST'])
def predict_salary():
    department = request.json['department']
    hire_date = request.json['hire_date']

    hire_year = pd.to_datetime(hire_date).year
    hire_month = pd.to_datetime(hire_date).month

    with sqlite3.connect('employees.db') as conn:
        departments = pd.read_sql_query("SELECT DISTINCT department FROM employee", conn)['department']
    
    input_data = pd.DataFrame({
        'department': departments,
        'hire_year': hire_year,
        'hire_month': hire_month
    })
    input_data = pd.get_dummies(input_data, columns=['department'])
    input_data.drop('department_'+department, axis=1, inplace=True)

    column_names = input_data.columns.tolist()
    coef = model.coef_.tolist()

    input_data = pd.DataFrame([[0] * len(column_names)], columns=column_names)
    for c, v in zip(column_names, coef):
        input_data[c] = v

    predicted_salary = model.predict(input_data)[0]

    return jsonify({'predicted_salary': predicted_salary})


if __name__ == '__main__':
    app.run(debug=True)
