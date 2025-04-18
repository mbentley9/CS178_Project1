import pymysql
import creds
import boto3
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()



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

# gets the list of countries from the database 
def get_list_of_dictionaries():
    query = "SELECT Name, Population FROM country;"
    return execute_query(query)
#my JOIN function 
def get_countries_and_languages():
    query = """
    SELECT country.Name, country.Population, countrylanguage.Language
    FROM country
    JOIN countrylanguage ON country.CountryCode = countrylanguage.CountryCode
    WHERE countrylanguage.Language = 'English';
    """
    results = execute_query(query)
    return results



# DynamoDB Setup
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
login_table = dynamodb.Table('Login')

def store_login(username, password):
    try:
        item = {
            "Username": username,
            "Password": password,
            "visited": []  
        }
        logger.debug(f"Attempting to store the following item: {item}")
        
        response = login_table.put_item(Item=item)
        
        # Log the response from DynamoDB
        logger.debug(f"DynamoDB response: {response}")
        
        print(f"Stored login for {username}")
    except Exception as e:
        logger.error(f"Error storing login for {username}: {e}")
        print(f"Error storing login for {username}: {e}")


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


def get_visited_countries(username):
    try:
        response = login_table.get_item(Key={'Username': username})
        item = response.get('Item')
        return item.get('visited', []) if item else []
    except Exception as e:
        print("Error fetching visited countries:", e)
        return []


# Authenticate user by checking to make sure the username and password are in DynamoDB
def authenticate_user(username, password):
    try:
        
        username = username.strip().lower()
    
        response = login_table.get_item(Key={'Username': username})
        
        item = response.get('Item')
        
        if item:
            print(f"User found: {item}")  
        else:
            print("User not found.")  
        
        
        if item and item['Password'] == password:
            return item
        else:
            print("Password mismatch.")  
            return None 
    except Exception as e:
        print("Error during authentication:", e)
        return None

#CRUD
# Insert a new user into DynamoDB 
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
        print(f"Attempting to delete user: {username}") 
        response = login_table.delete_item(
            Key={'Username': username}
        )
            
        if response.get('ConsumedCapacity'):
            print(f"User {username} deleted successfully.")  
        else:
            print(f"Failed to delete user {username}.")  
        
    except Exception as e:
        print(f"Error deleting user {username}: {e}")

# Update user password in DynamoDB #I had a lot of troubles getting this one to work. I had the help of chatgpt to debug and figure out to allow the user to change their password 
def update_user_password(username, new_password):
    try:
        print(f"Attempting to update password for user: {username}")  
        

        response = login_table.update_item(
            Key={'Username': username},
            UpdateExpression='SET Password = :val1',
            ExpressionAttributeValues={':val1': new_password},
            ReturnValues="UPDATED_NEW"  
        )
        
    
        
        if response.get('Attributes'):
            print(f"Password updated successfully for user: {username}") 
        else:
            print("Failed to update password.")  # Debugging line
        
    except Exception as e:
        print(f"Error updating password for {username}: {e}")
