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

@app.route('/top_five', methods=['GET'])
def displayTopFive():
    try:
        #data = request.json
        cur = mysql.connection.cursor()
        cur.execute("SELECT actor.actor_id, actor.first_name, actor.last_name, COUNT(film_actor.film_id) AS film_count FROM actor JOIN film_actor ON actor.actor_id = film_actor.actor_id GROUP BY actor.actor_id ORDER BY film_count DESC LIMIT 5;")
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