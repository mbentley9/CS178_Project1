import pymysql
import creds
import boto3

# MySQL (RDS) Connection Setup
def get_conn():
    return pymysql.connect(
        host=creds.host,
        user=creds.user,
        password=creds.password,
        db=creds.database,
        cursorclass=pymysql.cursors.DictCursor
    )

# Function to execute MySQL queries
def execute_query(query, args=None):
    conn = get_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, args or ())
            result = cursor.fetchall()
        return result
    finally:
        conn.close()

# Function to get a list of countries from MySQL database
def get_list_of_dictionaries():
    query = "SELECT Name, Population FROM country;"
    return execute_query(query)

# Function to join country and language data from MySQL
def get_countries_and_languages():
    query = """
    SELECT country.Name, country.Population, countrylanguage.Language
    FROM country
    JOIN countrylanguage ON country.CountryCode = countrylanguage.CountryCode
    WHERE countrylanguage.Language = 'English';
    """
    results = execute_query(query)
    return results

# DynamoDB (AWS) Connection Setup
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Ensure your region is correct
login_table = dynamodb.Table('Login')  # Your DynamoDB table name

# Store login information in DynamoDB
def store_login(username, password):
    try:
        username = username.strip().lower()  # Normalize username to lowercase
        item = {
            "Username": username,
            "Password": password,
            "visited": []  # Initialize visited countries as an empty list
        }
        
        # Attempt to store the item in DynamoDB
        response = login_table.put_item(Item=item)
        print(f"Stored login for {username}")
    except Exception as e:
        print(f"Error storing login for {username}: {e}")

# Add visited country to DynamoDB
def add_visited_country(username, country):
    try:
        # Retrieve the user from DynamoDB
        user = login_table.get_item(Key={'Username': username}).get('Item')
        visited = user.get('visited', []) if user else []

        if country not in visited:
            visited.append(country)

            # Update the visited countries list
            login_table.update_item(
                Key={'Username': username},
                UpdateExpression='SET visited = :val1',
                ExpressionAttributeValues={':val1': visited}
            )
            print(f"Added {country} to {username}'s visited list.")
    except Exception as e:
        print("Error adding visited country:", e)

# Get the list of visited countries from DynamoDB
def get_visited_countries(username):
    try:
        # Retrieve the user data
        response = login_table.get_item(Key={'Username': username})
        item = response.get('Item')
        return item.get('visited', []) if item else []
    except Exception as e:
        print("Error fetching visited countries:", e)
        return []

# Authenticate the user by checking username and password in DynamoDB
def authenticate_user(username, password):
    try:
        username = username.strip().lower()  # Normalize username to lowercase
        
        # Retrieve the user from DynamoDB
        response = login_table.get_item(Key={'Username': username})
        item = response.get('Item')

        if item and item['Password'] == password:
            return item
        else:
            print("Password mismatch or user not found.")
            return None
    except Exception as e:
        print(f"Error during authentication for {username}: {e}")
        return None

# Insert a new user into DynamoDB
def insert_user_to_dynamodb(username, password, visited=None):
    visited = visited or []
    try:
        login_table.put_item(
            Item={
                'Username': username.strip().lower(),  # Ensure username is lowercase
                'Password': password,
                'visited': visited
            }
        )
        print(f"Inserted new user {username} into DynamoDB.")
    except Exception as e:
        print(f"Error inserting user {username} into DynamoDB: {e}")

# Delete a user from DynamoDB
def delete_user_from_dynamodb(username):
    try:
        response = login_table.delete_item(Key={'Username': username})
        
        if response.get('ConsumedCapacity'):
            print(f"User {username} deleted successfully.")
        else:
            print(f"Failed to delete user {username}.")
    except Exception as e:
        print(f"Error deleting user {username}: {e}")

# Update user password in DynamoDB
def update_user_password(username, new_password):
    try:
        # Update password
        response = login_table.update_item(
            Key={'Username': username},
            UpdateExpression='SET Password = :val1',
            ExpressionAttributeValues={':val1': new_password},
            ReturnValues="UPDATED_NEW"
        )
        
        if response.get('Attributes'):
            print(f"Password updated successfully for user: {username}")
        else:
            print("Failed to update password.")
    except Exception as e:
        print(f"Error updating password for {username}: {e}")
