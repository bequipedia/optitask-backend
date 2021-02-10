#From this line start de OptiTask Project Backend.
#Desde esta linea comienza el proyecto de OptiTask Backend.

"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints.
Este módulo se encarga de iniciar el servidor API, cargar la base de datos y agregar los puntos finales.
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

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

# Handle/serialize errors like a JSON object.
# Manejar / serializar errores como un objeto JSON.
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints.
# generar mapa del sitio con todos sus puntos finales.
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def handle_hello():
    humans = Human.query.all()
    response_body = []
    for human in humans:
        response_body.append(human.serialize())
    return jsonify(response_body), 200


@app.route("/signup", methods=["POST"])
def handle_signup():
    """ creates an user and returns it./ Crea un usuario y lo devuelve. """
    data = request.json
    new_user = User.create(data)
    if new_user:
        return new_user.serialize(), 201

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
        return jsonify({"msg": "Missing email parameter / Falta el parámetro de correo electrónico"}), 400

    if not password:
        return jsonify({"msg": "Missing password parameter / Falta el parámetro de contraseña"}), 400
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

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

