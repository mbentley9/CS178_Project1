from flask import Flask, render_template
import mysql.connector
import creds  # your credentials file

app = Flask(__name__)

# Function to get DB connection
def get_connection():
    return mysql.connector.connect(
        host=creds.host,
        port=creds.port,
        user=creds.user,
        password=creds.password,
        database=creds.database
    )

# Route to home page
@app.route('/')
def home():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch categories
    cursor.execute("SELECT * FROM Category")
    categories = cursor.fetchall()

    # Fetch inventory
    cursor.execute("SELECT * FROM Inventory")
    inventory = cursor.fetchall()

    cursor.close()
    conn.close()

    # Organize inventory by categoryID
    grouped_inventory = {}
    for cat in categories:
        grouped_inventory[cat['categoryID']] = [
            item for item in inventory if item['categoryID'] == cat['categoryID']
        ]

    return render_template('store.html', categories=categories, inventory=grouped_inventory)

if __name__ == '__main__':
    app.run(debug=True)
