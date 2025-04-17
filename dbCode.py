import pymysql
import creds
import boto3
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

# ---------------- MySQL (RDS) Setup ----------------

# RDS Connection
def get_conn():
    return pymysql.connect(
        host=creds.host,
        user=creds.user,
        password=creds.password,
        db=creds.database,
        cursorclass=pymysql.cursors.DictCursor
    )

def execute_query(query, args=None):
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, args or ())
            result = cursor.fetchall()
        return result
    finally:
        conn.close()

# Fetch the list of countries from the 'country' table
def get_list_of_dictionaries():
    query = "SELECT Name, Population FROM country;"
    return execute_query(query)

def get_countries_and_languages():
    query = """
    SELECT country.Name, country.Population, countrylanguage.Language
    FROM country
    JOIN countrylanguage ON country.CountryCode = countrylanguage.CountryCode
    WHERE countrylanguage.Language = 'English';
    """
    results = execute_query(query)
    return results


# ---------------- DynamoDB Setup ----------------

# DynamoDB Setup
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
login_table = dynamodb.Table('Login')

# Store login credentials in DynamoDB
def store_login(username, password):
    try:
        # Log the data being sent to DynamoDB
        item = {
            "Username": username,
            "Password": password,
            "visited": []  # Empty list for visited countries
        }
        logger.debug(f"Attempting to store the following item: {item}")
        
        response = login_table.put_item(Item=item)
        
        # Log the response from DynamoDB
        logger.debug(f"DynamoDB response: {response}")
        
        print(f"Stored login for {username}")
    except Exception as e:
        logger.error(f"Error storing login for {username}: {e}")
        print(f"Error storing login for {username}: {e}")

# Add a visited country to the user's record
def add_visited_country(username, country):
    try:
        user = login_table.get_item(Key={'Username': username}).get('Item')
        visited = user.get('visited', []) if user else []
        if country not in visited:
            visited.append(country)
            login_table.update_item(
                Key={'Username': username},
                UpdateExpression='SET visited = :val1',
                ExpressionAttributeValues={':val1': visited}
            )
            print(f"Added {country} to {username}'s visited list.")
    except Exception as e:
        print("Error adding visited country:", e)

# Get the list of countries a user has visited
def get_visited_countries(username):
    try:
        response = login_table.get_item(Key={'Username': username})
        item = response.get('Item')
        return item.get('visited', []) if item else []
    except Exception as e:
        print("Error fetching visited countries:", e)
        return []

# ---------------- User Authentication ----------------

# Authenticate user by checking username and password in DynamoDB
def authenticate_user(username, password):
    try:
        # Convert username to lowercase for case-insensitive matching
        username = username.strip().lower()
        
        print(f"Attempting to authenticate user: {username}")  # Debugging line
        
        # Attempt to retrieve the user record from DynamoDB
        response = login_table.get_item(Key={'Username': username})
        print(f"DynamoDB response: {response}")  # Debugging line
        
        item = response.get('Item')
        
        if item:
            print(f"User found: {item}")  # Debugging line
        else:
            print("User not found.")  # Debugging line
        
        # If user is found and passwords match, return the user item
        if item and item['Password'] == password:
            return item
        else:
            print("Password mismatch.")  # Debugging line
            return None  # Return None if username/password don't match
    except Exception as e:
        print("Error during authentication:", e)
        return None

# ---------------- User CRUD Operations ----------------

# Insert a new user into DynamoDB (with visited countries)
def insert_user_to_dynamodb(username, password, visited=None):
    visited = visited or []
    login_table.put_item(
        Item={
            'Username': username,
            'Password': password,
            'visited': visited
        }
    )

# Delete a user from DynamoDB
def delete_user_from_dynamodb(username):
    try:
        print(f"Attempting to delete user: {username}")  # Debugging line
        
        # Delete user from DynamoDB
        response = login_table.delete_item(
            Key={'Username': username}
        )
        
        print(f"Delete response: {response}")  # Debugging line
        
        if response.get('ConsumedCapacity'):
            print(f"User {username} deleted successfully.")  # Debugging line
        else:
            print(f"Failed to delete user {username}.")  # Debugging line
        
    except Exception as e:
        print(f"Error deleting user {username}: {e}")

# Update user password in DynamoDB
def update_user_password(username, new_password):
    try:
        print(f"Attempting to update password for user: {username}")  # Debugging line
        
        # Update user password in DynamoDB
        response = login_table.update_item(
            Key={'Username': username},
            UpdateExpression='SET Password = :val1',
            ExpressionAttributeValues={':val1': new_password},
            ReturnValues="UPDATED_NEW"  # To return the updated values
        )
        
        print(f"Password update response: {response}")  # Debugging line
        
        if response.get('Attributes'):
            print(f"Password updated successfully for user: {username}")  # Debugging line
        else:
            print("Failed to update password.")  # Debugging line
        
    except Exception as e:
        print(f"Error updating password for {username}: {e}")
