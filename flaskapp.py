from flask import Flask, render_template, request, redirect, url_for
from dbCode import get_list_of_dictionaries, store_login, authenticate_user, update_user_password, delete_user_from_dynamodb, add_visited_country, get_visited_countries
import pymysql
import creds
import boto3

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('login.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')


@app.route('/submit_login', methods=['POST'])
def submit_login():
    username = request.form['username']
    password = request.form['password']

    user = authenticate_user(username, password)
    
    if user:
        return redirect(url_for('checkin', username=username))
    else:
        error_message = f"Sorry, {username} is not in our system."
        return render_template('user_not_found.html', error_message=error_message)
    
@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    if request.method == 'POST':
        username = request.form['username'].strip()  
        visited = request.form.getlist('visited')  
        for country in visited:
            add_visited_country(username, country)  
        return render_template("checkedin.html", username=username, countries=visited)
    
    countries = get_list_of_dictionaries()  
    return render_template("select_countries.html", results=countries, username=request.args.get('username'))



@app.route('/visited/<username>')
def visited(username):
    visited_countries = get_visited_countries(username)  
    return render_template('visited_countries.html', visited_countries=visited_countries, username=username)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        store_login(username, password)  
        return redirect('/')
    return render_template('add_user.html')


@app.route('/update_user', methods=['GET', 'POST'])
def update_user():
    if request.method == 'POST':
        username = request.form['username'].strip()
        new_password = request.form['password']
        update_user_password(username, new_password)  
        return redirect('/')
    return render_template('update_user.html')


@app.route('/delete_user', methods=['GET', 'POST'])
def delete_user():
    if request.method == 'POST':
        username = request.form['username'].strip()
        delete_user_from_dynamodb(username)  
        return redirect('/')
    return render_template('delete_user.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
