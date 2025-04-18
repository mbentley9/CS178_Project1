from flask import Flask, render_template, request, redirect, url_for
from dbCode import get_list_of_dictionaries, store_login, authenticate_user, update_user_password, delete_user_from_dynamodb, add_visited_country, get_visited_countries
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
    
    # Authenticate user with the provided credentials
    user = authenticate_user(username, password)
    
    if user:
        return redirect(url_for('checkin', username=username))
    else:
        error_message = f"Sorry, {username} is not in our system."
        return render_template('user_not_found.html', error_message=error_message)

@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    if request.method == 'POST':
        username = request.form['username'].strip()  # Strip any unnecessary spaces
        visited = request.form.getlist('visited')  # List of visited countries from the form
        for country in visited:
            add_visited_country(username, country)  # Update the DynamoDB entry
        return render_template("checkedin.html", username=username, countries=visited)

    countries = get_list_of_dictionaries()  # Get countries from MySQL
    return render_template("select_countries.html", results=countries, username=request.args.get('username'))

@app.route('/visited/<username>')
def visited(username):
    visited_countries = get_visited_countries(username)  # Get visited countries from DynamoDB
    return render_template('visited_countries.html', visited_countries=visited_countries, username=username)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username'].strip()  # Ensure no spaces
        password = request.form['password']
        
        # Store user login information in DynamoDB
        store_login(username, password)
        
        return redirect('/')
    return render_template('add_user.html')

@app.route('/update_user', methods=['GET', 'POST'])
def update_user():
    if request.method == 'POST':
        username = request.form['username'].strip()
        new_password = request.form['password']
        
        # Update user password in DynamoDB
        update_user_password(username, new_password)
        
        return redirect('/')
    return render_template('update_user.html')

@app.route('/delete_user', methods=['GET', 'POST'])
def delete_user():
    if request.method == 'POST':
        username = request.form['username'].strip()  # Ensure no spaces
        
        # Delete user from DynamoDB
        delete_user_from_dynamodb(username)
        
        return redirect('/')
    return render_template('delete_user.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
