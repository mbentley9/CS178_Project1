
import pymysql
import creds

def execute_query(query, args=()):
    cur = get_conn().cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows

def get_conn():
    return pymysql.connect(
        host=creds.host,
        user=creds.user,
        password=creds.password,
        db=creds.database,
        cursorclass=pymysql.cursors.DictCursor  # So we can use column names in results
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

def get_cities():
    query = "SELECT Name, Population FROM City LIMIT 10;"
    return execute_query(query)

def get_languages():
    query = "Select Distinct Language From countrylanguage Order By language;"
    results = execute_query(query)
    return [row['Language']for row in results]

def get_list_of_dictionaries():
    query = "SELECT Name, Population From country LIMIT 10;"
    return execute_query(query)


if __name__ == "__main__":
    cities = get_cities()
    for city in cities:
        print(f"{city['Name']} - {city['Population']}")
