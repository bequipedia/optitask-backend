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
from models import db, User,Group,Task
from random import randint
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
BASE_URL="http://localhost:8080/"

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
        country_code=body['country_code'] if 'country_code' in body else None,
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

#----------------------------------------------endpoint groups--------------------------------------------------------

@app.route('/groups/<int:id_group>', methods=['GET'])#endpoint para ver los datos de un grupo
def handle_one_group(id_group):
    group = Group.query.get(id_group)
    if group is None:
        return "NO EXISTE", 404
    else:
        return jsonify(group.serialize()), 202

@app.route('/groups', methods=['POST'])#Endpoint para crear un grupo
@jwt_required
def add_new_group():
    email = get_jwt_identity()
    body= request.get_json()
    #validaciones de body para campos obligatorios
    if isinstance (body,dict):
        if body is None:
            raise APIException("Please specify the request body as a json object", status_code=400)
        if 'group_name' not in body:
            raise APIException("You need to specify the name", status_code=400)
        if 'user_admin_id' not in body:
            raise APIException("You need to specify the id user", status_code=400)

    else: return "error in body, is not a dictionary"
    url_group_random=""
    for i in range(10):
        url_group_random=url_group_random+str(randint(0,10))
    group1 = Group.create_group(
        group_name=body['group_name'],
        user_admin_id=body['user_admin_id'],
        description=body['description'] if 'description' in body else None,
        group_url=BASE_URL+"groups/"+body['group_name']+url_group_random,#revisar construcción de url única para cada user
        url_image=None#Esto debemos cambiarlo luego por una imagen predeterminada
    )
    return group1.serialize(), 200



@app.route('/groups/<int:id_group>', methods=['PATCH'])
def upgrade_group(id_group):
    body = request.get_json()
    group_to_upgrade = Group.query.get(id_group)

    if group_to_upgrade is None:
        raise APIException('You need to specify an existing group', status_code=400)
    if 'group_name' in body  != None:
        new_group_name = body['group_name']
        group_to_upgrade.group_name = new_group_name
    if 'description' in body  != None:
        new_description = body['description']
        group_to_upgrade.description = new_description
    if 'url_image' in body != None:
        new_url_image = body['url_image']
        group_to_upgrade.url_image = new_url_image

    db.session.commit()
    return 'Cambio realizado'



#----------------------------------------- endpoint Tasks ------------------------------------------------------------

#Funcion para mostrar con una solicitud GET todas las tareas que se encuentran en un grupo determinado
@app.route('/groups/<int:id_group>/tasks', methods=['GET'])
def handle_tasks(id_group):
    group = Group.query.get(id_group)
    if group is None:
        return "NO EXISTE", 404
    if id_group is None:
        raise APIException('You need to specify an existing group', status_code=400)
    tasks = Task.query.filter_by(group_id=id_group)
    response_body= []
    for task in tasks:
        response_body.append(task.serialize())
    return jsonify(response_body),200


@app.route('/groups/tasks', methods=['POST'])#Endpoint para crear una tarea
def add_new_task():
    body= request.get_json()
    #validaciones de body para campos obligatorios
    if isinstance (body,dict):
        if body is None:
            raise APIException("Please specify the request body as a json object", status_code=400)
        if 'label_task' not in body:
            raise APIException("You need to specify the name", status_code=400)
        if 'group_id' not in body:
            raise APIException("You need to specify the id group", status_code=400)

    else: return "error in body, is not a dictionary"

    task1 = Task.create_task(
        group_id=body['group_id'],
        label_task=body['label_task'],
        status_text=body['status_text'] if 'status_text' in body else None,
        status_task=body['status_task'] if 'status_task' in body else False,
        top_date=body['top_date'] if 'top_date' in body else None,
        init_date=time.strftime("%c")
    ) 
    return task1.serialize(), 200

#Funcion para actualizar una propiedad de una tarea
@app.route('/groups/tasks/<int:id_task>', methods=['PATCH'])
def upgrade_task(id_task):
    body = request.get_json()
    task_to_upgrade = Task.query.get(id_task)
    if task_to_upgrade is None:
        raise APIException('You need to specify an existing task', status_code=400)
    if 'label_task' in body  != None:
        new_label_task = body['label_task']
        task_to_upgrade.label_task = new_label_task
    if 'status_text' in body  != None:
        new_status_text = body['status_text']
        task_to_upgrade.status_text = new_status_text
    if 'status_task' in body != None:
        new_status_task = body['status_task']
        task_to_upgrade.status_task = new_status_task
    if 'top_date' in body != None:
        new_top_date = body['top_date']
        task_to_upgrade.top_date = new_top_date

    db.session.commit()
    return 'Cambio realizado'

#funcion para borrar una tarea
@app.route('/groups/tasks/<int:id_task>', methods=['DELETE'])
def delete_contact(id_task): 
    db.session.delete(Task.query.get_or_404(id_task) )
    db.session.commit() 
    return '', 204


#---------------------------------- endpoint Sale --------------------------------

#
@app.route('/groups/sale', methods=['GET'])
def handle_sales(id_group):
    sales = Sale.query.filter_by(group_id=id_group)
    response_body= []
    for sale in sales:
        response_body.append(sale.serialize())
    return jsonify(response_body),200
























#this only runs if `$ python src/main.py` is executed.
#Esto solo se ejecuta si se ejecuta `$ python src / main.py`.
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


