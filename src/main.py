"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from models import db
from models import Todo

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/todos/user/<user_name>', methods=['POST', 'GET', 'PUT', 'DELETE'])
def handle_hello(user_name):

    response_body = None

    if request.method == 'POST':
        body = request.get_json()
        todo = Todo(user_name=body['user_name'], label=body['label'], done='false')
        db.session.add(todo)
        db.session.commit()
        return jsonify("POST accepted"), 200

    if request.method == 'GET':
        all_todos = Todo.query.filter_by(user_name=user_name)
        all_todos = list(map(lambda x: x.serialize(), all_todos))
        response_body = all_todos

    if request.method == 'PUT':
        body = request.get_json()
        todo = Todo.query.get(body['id'])
        todo.user_name = body['user_name']
        todo.label = body['label']
        todo.done = body['done']
        db.session.commit()
        return jsonify("PUT accepted"), 200

    if request.method == 'DELETE':
        response_body = {
            "hello": "world DELETE"
        }

    return jsonify(response_body), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
