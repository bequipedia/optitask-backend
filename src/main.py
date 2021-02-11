#From this line start de OptiTask Project Backend.
#Desde esta linea comienza el proyecto de OptiTask Backend.

"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints.
Este módulo se encarga de iniciar el servidor API, cargar la base de datos y agregar los puntos finales.
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


# from models import Person.
# Desde models importar Person.
app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['JWT_SECRET_KEY'] = 'OptiTask'
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

# generate sitemap with all your endpoints.
# generar mapa del sitio con todos sus puntos finales.
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
    user1 = User.create(
        email=body['email'],
        name=body['name'] if 'name' in body else None,
        last_name=body['last_name'] if 'last_name' in body else None,
        user_name=body['user_name'],
        password=body['password'],
        cedula_rif=None,
        country=body['country'] if 'country' in body else None,
        region_state=body['region_state'] if 'region_state' in body else None,
        municipality=None,
        url=BASE_URL+"/users/"+body['user_name'],#revisar construcción de url única para cada user
        url_image=None,#Esto debemos cambiarlo luego por una imagen predeterminada
        user_registered=time.strftime("%c"))
    return user1.serialize(), 200

@app.route("/login", methods=["POST"])
def handle_login():
    """ 
        check password for user with email = body['email']
        and return token if match.

        comprobar la contraseña del usuario con email = body ['email']
         y devolver el token si coincide.
    """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request / Falta JSON en la solicitud"}), 400
    params = request.get_json()
    email = params.get('email', None)
    password = params.get('password', None)
    if not email:
        return jsonify({"msg": "Missing email parameter / Falta el parametro de correo electronico"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter / Falta el parametro de contrasena"}), 400
    user = User.query.filter_by(email=email).one_or_none()
    if not user:
        return jsonify({"msg": "User does not exist / El usuario no existe"}), 404
    if user.check_password(password):
        response = {'jwt': create_access_token(identity=user.email)}
        return jsonify(response), 200
    else:
        return jsonify({"msg": "Bad credentials / Credenciales incorrectas"}), 401

@app.route("/seguro")
@jwt_required
def handle_seguro():
    email = get_jwt_identity() 
    # nos devolvera la identidad del token.
    # will return the identity of the token.
    return jsonify({"msg":f"Hello, {email}"})

#For the Logout function, it is not necessary to do it in the backend, 
#because the Logout will be done directly in the frontend.

#Para la funcion Logout, no es necesario hacerla en el backend,
#debido que el Logout se hara directamente en el frontend

#this only runs if `$ python src/main.py` is executed.
#Esto solo se ejecuta si se ejecuta `$ python src / main.py`.
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


