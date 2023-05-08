# Flask-RESTAPI-recruitment-task-Muvid
A backend recruitment task based on Flask, SQLAlchemy &amp; Sqlite DB, given by Muvid.

Requirements 1,2,3 are fulfilled. 
For requiremet 5, I kept getting this error in the postman request:


<img width="638" alt="error" src="https://user-images.githubusercontent.com/11318378/236849093-408d2890-c94f-4f64-b0bd-8deaeba17614.png">

My assumption is that feature names in my test data don't match the feature names in my training data. I tried to solve this with adding the one-hot encoding for
department in the API code as well, but it didn't work out for me due to my lack of domain knowledge in these concepts.

## Challenges Faced:
1. The model training & implementation
2. In task 1, handing the range of datetime in the requests. 
