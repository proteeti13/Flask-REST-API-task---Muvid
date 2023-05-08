import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib


conn = sqlite3.connect('employees.db')


employee_data = pd.read_sql_query("SELECT department, hire_date, salary FROM employee", conn)

employee_data['hire_date'] = pd.to_datetime(employee_data['hire_date'])
employee_data['hire_year'] = employee_data['hire_date'].dt.year
employee_data['hire_month'] = employee_data['hire_date'].dt.month

employee_data.drop('hire_date', axis=1, inplace=True)

employee_data = pd.get_dummies(employee_data, columns=['department'])

X = employee_data.drop('salary', axis=1)
y = employee_data['salary']


model = LinearRegression()
model.fit(X, y)


joblib.dump(model, 'model.joblib')

