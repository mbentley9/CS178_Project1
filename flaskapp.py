from flask import Flask, render_template, request, redirect, url_for
from dbCode import get_list_of_dictionaries, store_login, authenticate_user, update_user_password, delete_user_from_dynamodb, add_visited_country, get_visited_countries
import pymysql
import creds
import boto3

app = Flask(__name__)

# This is the homepage route that shows the login form
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

# Route to handle login submission
@app.route('/submit_login', methods=['POST'])
def submit_login():
    username = request.form['username']
    password = request.form['password']

    # Try to authenticate the user
    user = authenticate_user(username, password)
    
    if user:
        # After successful login, redirect user to the country selection page
        return redirect(url_for('checkin', username=username))
    else:
        error_message = f"Sorry, {username} is not in our system."
        return render_template('user_not_found.html', error_message=error_message)
    
# Route to check in and save visited countries
@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    if request.method == 'POST':
        username = request.form['username'].strip()  # Get the username from the form
        visited = request.form.getlist('visited')  # Get the list of selected countries
        for country in visited:
            add_visited_country(username, country)  # Store the visited country in DynamoDB
        return render_template("checkedin.html", username=username, countries=visited)
    
    # Retrieve the list of countries from MySQL and pass it to the template
    countries = get_list_of_dictionaries()  # Get countries from MySQL
    return render_template("select_countries.html", results=countries, username=request.args.get('username'))


# Route to display the list of countries the user has visited
@app.route('/visited/<username>')
def visited(username):
    visited_countries = get_visited_countries(username)  # Get countries the user has visited
    return render_template('visited_countries.html', visited_countries=visited_countries, username=username)

# Add User route (sign-up)
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        store_login(username, password)  # Store the new user's credentials in DynamoDB
        return redirect('/')
    return render_template('add_user.html')

# Update User Password route
@app.route('/update_user', methods=['GET', 'POST'])
def update_user():
    if request.method == 'POST':
        username = request.form['username'].strip()
        new_password = request.form['password']
        update_user_password(username, new_password)  # Update the user's password in DynamoDB
        return redirect('/')
    return render_template('update_user.html')

# Delete User route
@app.route('/delete_user', methods=['GET', 'POST'])
def delete_user():
    if request.method == 'POST':
        username = request.form['username'].strip()
        delete_user_from_dynamodb(username)  # Delete the user from DynamoDB
        return redirect('/')
    return render_template('delete_user.html')

# Other routes for adding, updating, and deleting users remain unchanged...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
