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
        cur.execute("""
                    SELECT f.film_id, f.title, f.description, f.release_year, f.language_id, f.original_language_id,
                        f.rental_duration, f.rental_rate, f.length, f.replacement_cost, f.rating, f.special_features, f.last_update,
                        i.inventory_id, s.store_id
                    FROM film f
                    INNER JOIN inventory i ON f.film_id = i.film_id
                    INNER JOIN store s ON i.store_id = s.store_id
                    WHERE f.title = %s;
                    """, (title,))
        data = cur.fetchall()
        cur.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})
    
@app.route('/top_five_actors', methods=['GET'])
def fetchTopFiveActors():
    try:
        #data = request.json
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT first_name, last_name, num_rentals
            FROM (
                SELECT a.actor_id, a.first_name, a.last_name, COUNT(r.rental_id) AS num_rentals
                FROM actor a
                JOIN film_actor fa ON a.actor_id = fa.actor_id
                JOIN film f ON fa.film_id = f.film_id
                JOIN inventory i ON f.film_id = i.film_id
                JOIN rental r ON i.inventory_id = r.inventory_id
                GROUP BY a.actor_id, a.first_name, a.last_name
            ) AS rental_counts -- Add alias here
            ORDER BY num_rentals DESC
            LIMIT 5;
        """)
        data = cur.fetchall()
        print(data)
        cur.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})
    
@app.route('/actor_details', methods=['GET'])
def displayActorDetails():
    try:
        #data = request.json
        first_name = request.args.get('f_name')
        last_name = request.args.get('l_name')
        cur = mysql.connection.cursor()
        cur.execute("""SELECT 
                        a.first_name,
                        a.last_name,
                        AVG(f.rating) AS average_rating,
                        GROUP_CONCAT(f.title ORDER BY f.title ASC SEPARATOR ', ') AS movies,
                        GROUP_CONCAT(fr.title ORDER BY fr.rental_count DESC SEPARATOR ', ') AS top_5_rented_films
                    FROM 
                        actor a
                    JOIN 
                        film_actor fa ON a.actor_id = fa.actor_id
                    JOIN 
                        film f ON fa.film_id = f.film_id
                    JOIN 
                        film_category fc ON f.film_id = fc.film_id
                    JOIN 
                        category c ON fc.category_id = c.category_id
                    LEFT JOIN 
                        (SELECT 
                            f2.title, 
                            COUNT(r.inventory_id) AS rental_count
                        FROM 
                            film f2
                        JOIN 
                            inventory i ON f2.film_id = i.film_id
                        JOIN 
                            rental r ON i.inventory_id = r.inventory_id
                        GROUP BY 
                            f2.title
                        ORDER BY 
                            rental_count DESC LIMIT 5) AS fr ON f.title = fr.title
                    GROUP BY 
                        a.first_name, a.last_name
                        HAVING 
                            a.first_name = %s AND a.last_name = %s;""", (first_name, last_name,))
        data = cur.fetchall()
        cur.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/film_search_default', methods=['GET'])
def displayBaseSearchResults():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""SELECT DISTINCT f.title
                        FROM film f
                        INNER JOIN inventory i ON f.film_id = i.film_id
                        WHERE i.inventory_id NOT IN (
                        SELECT inventory_id
                        FROM rental r
                        WHERE r.return_date IS NULL
                        );""")
        data = cur.fetchall()
        cur.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/film_search/<filter>', methods=['GET'])
def displaySearchResults(filter):
    try:
        search_term = request.args.get('q')
        cur = mysql.connection.cursor()
        print(filter)
        if filter == "film":
            query = """
                SELECT title, film_id
                FROM film
                WHERE title LIKE (%s)
            """
            cur.execute(query, ("%" + search_term + "%",))
        elif filter == "actor":
            query = """
                SELECT f.title, f.film_id
                FROM film f
                INNER JOIN film_actor fa ON f.film_id = fa.film_id
                INNER JOIN actor a ON fa.actor_id = a.actor_id
                WHERE (a.first_name LIKE (%s) OR a.last_name LIKE (%s) OR CONCAT(a.first_name, ' ', a.last_name) LIKE (%s))
            """
            cur.execute(query, ("%" + search_term + "%",) * 3)
        elif filter == "genre":
            query = """
                SELECT f.title, g.name AS genre
                FROM film f
                INNER JOIN film_category fc ON f.film_id = fc.film_id
                INNER JOIN category g ON fc.category_id = g.category_id
                WHERE g.name LIKE (%s);
            """
            cur.execute(query, ("%" + search_term + "%",))
        data = cur.fetchall()
        cur.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/check_availability', methods=['POST'])
def check_availability():
    try:
        title = request.args.get('title')
        cur = mysql.connection.cursor()
        cur.execute("""
        SELECT count(*) as available 
        FROM film f
        JOIN inventory i ON f.film_id = i.film_id
        WHERE f.title = (%s) AND i.inventory_id NOT IN (
        SELECT inventory_id FROM rental r
        WHERE r.return_date IS NULL);""", (title,))
        available = cur.fetchone()
        print("hi")
        message = "Film is available" if available[0] > 0 else "Film is not available"
        return jsonify({'available': available[0], 'message': message})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/customers')
def get_customers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT first_name, last_name FROM customer")
    customers = cur.fetchall()
    return jsonify([{'value': f"{first_name} {last_name}", 'text': f"{first_name} {last_name}"} for first_name, last_name in customers])

'''
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

@app.route('/api/message')
def index():
    return jsonify(message="Hello from Flask!")
'''

if __name__ == '__main__':
    app.run(debug=True)