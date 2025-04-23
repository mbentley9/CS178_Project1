import pymysql
import creds
import boto3

# MySQL (RDS) Connection
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
            return cursor.fetchall()
    finally:
        conn.close()

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
    return execute_query(query)

# DynamoDB Setup
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
login_table = dynamodb.Table('Login')

def store_login(username, password):
    try:
        username = username.strip().lower()
        item = {
            "Username": username,
            "Password": password,
            "visited": []
        }
        login_table.put_item(Item=item)
    except Exception as e:
        print(f"Error storing login for {username}: {e}")

def authenticate_user(username, password):
    try:
        username = username.strip().lower()
        item = login_table.get_item(Key={'Username': username}).get('Item')
        if item and item['Password'] == password:
            return item
        return None
    except Exception as e:
        print(f"Auth error for {username}: {e}")
        return None

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
    except Exception as e:
        print("Error adding visited country:", e)

def get_visited_countries(username):
    try:
        item = login_table.get_item(Key={'Username': username}).get('Item')
        return item.get('visited', []) if item else []
    except Exception as e:
        print("Error getting visited countries:", e)
        return []

def delete_user_from_dynamodb(username):
    try:
        login_table.delete_item(Key={'Username': username})
    except Exception as e:
        print(f"Error deleting user {username}: {e}")

def update_user_password(username, new_password):
    try:
        login_table.update_item(
            Key={'Username': username},
            UpdateExpression='SET Password = :val1',
            ExpressionAttributeValues={':val1': new_password},
            ReturnValues="UPDATED_NEW"
        )
    except Exception as e:
        print(f"Error updating password for {username}: {e}")
