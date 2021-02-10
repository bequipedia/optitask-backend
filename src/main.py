"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os,time
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity)
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
jwt = JWTManager(app)
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
BASE_URL="http://localhost:3000/"
# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def handle_user():
    users = User.query.all()
    response_body= []
    for user in users:
        response_body.append(user.serialize())
    return jsonify(response_body),200

#endpoint User para crear nuevos usuarios
@app.route('/users', methods=['POST'])
def add_new_user():
    body= request.get_json()
    #validaciones de body para campos obligatorios
    if isinstance (body,dict):
        if body is None:
            raise APIException("Please specify the request body as a json object", status_code=400)
        if 'email' not in body:
            raise APIException("You need to specify the name", status_code=400)
        if 'user_name' not in body:
            raise APIException("You need to specify the name", status_code=400)
        if 'password' not in body:
            raise APIException("You need to specify the name", status_code=400)
    else: return "error in body, is not a dictionary"
    user1 = User(
        email=body['email'],
        name=body['name'] if 'name' in body else None,
        last_name=body['last_name'] if 'last_name' in body else None,
        user_name=body['user_name'],
        password=body['password']
        cedula_rif=None,
        country=body['country'] if 'country' in body else None,
        region_state=body['region_state'] if 'region_state' in body else None,
        municipality=None,
        url=BASE_URL+"/users/"+nickname,#revisar construcción de url única para cada user
        url_image=None,#Esto debemos cambiarlo luego por una imagen predeterminada
        user_registered=time.strftime("%c")
    db.session.add(user1)
    db.session.commit()
    return "ok", 200

def handle_login():
    @app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    user=User.query.filter_by(email=email).one_or_none
    if not user:
        return jsonify()
    if username != 'test' or password != 'test':
        return jsonify({"msg": "Bad username or password"}), 401

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
