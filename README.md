<h1>CS178 Project 1</h1>
<h2>Introduction</h2>
<p1>This project is a web application built in AWS. The app allows users to login and select all of the countries they have ever been to. It stores the countries they wantt in a DynamoDB database called ('Login')</p1>
<h2>Purpose</h2>
<p1>It is designed to help users keep track of where they have been and help them figure out where they want to go next! In this project you will see that it taught me how to build an application with flask that connects both relationoal and non-relational database.</p1>
<h2>Instructions</h2>
1. Fork the repository: make sure it is in your current directory 

```
 cd CS178_Project1
```
2. Install the requirements.txt

```
pip install -r requirements.txt
```

3. Make sure you have an active AWS account
   
 ```
aws configure
```

5. Create a creds.py

```
host = "project-one.cn9nbw41gsla.us-east-1.rds.amazonaws.com"

user = 'admin'
password = 'I<3CS178!'

database = 'world'
```

6. Create a dynamoDB Table and lable it 'Login'

7. Run the app

```
python3 flaskapp.py
```




