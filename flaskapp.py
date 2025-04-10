from flask import Flask

app = Flask(__name__)
from flask import render_template
import pymysql
import creds 

def get_conn():
    conn = pymysql.connect(
        host= creds.host,
        user= creds.user, 
        password = creds.password,
        db=creds.database,
        )
    return conn

def execute_query(query, args=()):
    cur = get_conn().cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows


#display the sqlite query in a html table
def display_html(rows):
    html = ""
    html += """<table><tr><th>ArtistID</th><th>Artist</th><th>Track Title</th><th>Price</th><th>Milliseconds</th></tr>"""

    for r in rows:
        html += "<tr><td>" + str(r[0]) + "</td><td>" + str(r[1]) + "</td><td>" + str(r[2]) + "</td><td>" + str(r[3]) + "</td><td>" + str(r[4]) + "</td></tr>"
    html += "</table></body>"
    return html



@app.route("/pricequery/<price>")
def viewprices(price):
    rows = execute_query("""select ArtistId, Artist.Name, Track.Name, UnitPrice, Milliseconds
            from Artist JOIN Album using (ArtistID) JOIN Track using (AlbumID)
            where UnitPrice = %s order by Track.Name 
            Limit 500""", (str(price)))
    return display_html(rows) 

@app. route("/timequery/<time>")
def viewtime(time):
    rows = execute_query("""select ArtistId, Artist.Name, Track.Name, UnitPrice, Milliseconds
            from Artist JOIN Album using (ArtistID) JOIN Track using (AlbumID)
            where Milliseconds >= %s order by Track.Name 
            """, (str(time)))
    return display_html(rows) 

from flask import request


@app.route("/pricequerytextbox", methods = ['GET'])
def price_form():
  return render_template('textbox.html', fieldname = "Price")



@app.route("/pricequerytextbox", methods = ['POST'])
def price_form_post():
  text = request.form['text']
  return viewprices(text)

@app.route("/timequerytextbox", methods = ['GET'])
def time_form():
    return render_template('textbox.html', fieldname = "Time")

@app.route("/timequerytextbox", methods = ['POST'])
def time_form_post():
    text = request.form['text']
    return viewtime(text)

@app. route("/languages")
def get_languages():
    query = "Select Distinct Language From countrylanguage Order By language;"
    results = execute_query(query)
    return [row['Language']for row in results] 

from dbCode import get_list_of_dictionaries
@app.route('/cities')
def home():
    cities = get_cities()
    return render_template('cities.html', cities=cities)

@app.route('/')
def index():
    countries = get_list_of_dictionaries()
    return render_template("index.html", results=countries)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
