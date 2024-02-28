from flask import Flask, request, jsonify
#from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:42Drm400$!@localhost/sakila' 
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "42Drm400$!"
app.config['MYSQL_DB'] = "sakila"
#db = SQLAlchemy(app)
mysql = MySQL(app)

@app.route('/top_five_films', methods=['GET'])
def displayTopFiveFilms():
    try:
        #data = request.json
        cur = mysql.connection.cursor()
        cur.execute("SELECT f.film_id, f.title, COUNT(r.rental_id) AS num_rentals FROM film f JOIN inventory i ON f.film_id = i.film_id JOIN rental r ON i.inventory_id = r.inventory_id GROUP BY f.film_id, f.title ORDER BY num_rentals DESC LIMIT 5;")
        data = cur.fetchall()
        cur.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})
    
@app.route('/film_details', methods=['GET'])
def displayFilmDetails():
    try:
        #data = request.json
        title = request.args.get('title')
        cur = mysql.connection.cursor()
        cur.execute("SELECT film_id, title, description, release_year, language_id, original_language_id, rental_duration, rental_rate, length, replacement_cost, rating, special_features, last_update FROM film WHERE title = %s;", (title,))
        data = cur.fetchall()
        cur.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})

'''
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

@app.route('/api/message')
def index():
    return jsonify(message="Hello from Flask!")
'''

if __name__ == '__main__':
    app.run(debug=True)