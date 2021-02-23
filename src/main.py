#From this line start de OptiTask Project Backend.
#Desde esta linea comienza el proyecto de OptiTask Backend.

"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints.
Este módulo se encarga de iniciar el servidor API, cargar la base de datos y agregar los puntos finales.
"""
from datetime import datetime, date, time, timedelta
import os,time
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User,Group,Task,PersonGroup,Income,Expense,Rate
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

#Endpoint para ver los datos de todos los usuarios (Probado con 1-POSTMAN.OK)
@app.route('/users', methods=['GET'])
def handle_user():
    users = User.query.all()
    response_body= []
    for user in users:
        response_body.append(user.serialize())
    return jsonify(response_body),200

#Endpoint para ver los datos de un usuario (Probado con POSTMAN.OK)
@app.route('/users/<int:id_user>', methods=['GET'])
def handle_one_user(id_user):
    user = User.query.get(id_user)
    if user is None:
        return "NO EXISTE", 404
    else:
        return jsonify(user.serialize()), 202

#endpoint User para crear nuevos usuarios (Probado con POSTMAN.OK)
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
    now = datetime.utcnow()
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
        url=BASE_URL+"users/"+body['user_name'],#revisar construcción de url única para cada user
        url_image=None,#Esto debemos cambiarlo luego por una imagen predeterminada
        user_registered=now.strftime('%Y-%m-%d %H:%M:%S'))
    return user1.serialize(), 200

#endpoint para el login de un usuario (Probado con POSTMAN.OK)
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

#endpoint para devolver la identidad de un token de usuario (login recien iniciado, y al probar da ERROR: TOKEN EXPIRADO)--PRUEBA CON REQBIN.OK
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

#Endpoint para ver los datos de un grupo
@app.route('/groups/<int:id_group>', methods=['GET'])
def handle_one_group(id_group):
    group = Group.query.get(id_group)
    if group is None:
        return "NO EXISTE", 404
    else:
        return jsonify(group.serialize()), 202

#Endpoint para crear un grupo (PROBADO CON POSTMAN.OK)
@app.route('/groups', methods=['POST'])
def add_new_group():
    #email = get_jwt_identity()
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

#Endpoint para agregar un usuario en un grupo ya creado
#Despues de crear un grupo se deberia realizar este endpoint que permite colacar el id del
#usuario en el grupo PROBADO OK. CON POSTMAN
@app.route('/persongroup', methods=['POST']) 
def add_new_person_group():
    #email = get_jwt_identity()
    body= request.get_json()
    #validaciones de body para campos obligatorios
    if isinstance (body,dict):
        if body is None:
            raise APIException("Please specify the request body as a json object", status_code=400)
        if 'user_id' not in body:
            raise APIException("You need to specify the id user", status_code=400)
        if 'group_id' not in body:
            raise APIException("You need to specify the id group", status_code=400)

    else: return "error in body, is not a dictionary"
    person_group1 = PersonGroup.create_person_group(
        user_id=body['user_id'],
        group_id=body['group_id']
    )
    return person_group1.serialize(), 200

#Este endpoint permite realizar un cambio en alguna propiedad de un grupo
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

#----------------------------- Utilizando relacion PersonGroup---------------------------

#Este endpoint permite ver los datos de todos los usuarios de un grupo
@app.route('/users/groups/<int:id_group>', methods=['GET'])
def handle_user_group(id_group):
    group = Group.query.get(id_group)
    if group is None:
        return "NO EXISTE", 404
    else:
        relaciones=PersonGroup.query.filter_by(group_id=id_group)
        all_users=[]
        for relacion in relaciones:
            all_users.append(relacion.serialize())
        response_body= []
        for user1 in all_users:
            response_body.append(User.query.get(user1['user_id']).serialize())
            
        return jsonify(response_body),200

#Este endpoint permite ver los datos de todos los grupos de un usuario
@app.route('/users/<int:id_user>/groups', methods=['GET'])
def handle_group_user(id_user):
    user = User.query.get(id_user)
    if user is None:
        return "NO EXISTE", 404
    else:
        relaciones=PersonGroup.query.filter_by(user_id=id_user)
        all_groups=[]
        for relacion in relaciones:
            all_groups.append(relacion.serialize())
        response_body= []
        for group1 in all_groups:
            response_body.append(Group.query.get(group1['group_id']).serialize())
    return jsonify(response_body),200



#----------------------------------------- endpoint Tasks ------------------------------------------------------------

#Funcion para mostrar todas las tareas de un grupo 
@app.route('/groups/<int:id_group>/tasks', methods=['GET'])
def handle_group_tasks(id_group):
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

#Funcion para mostrar todas las tareas de un usuario 
@app.route('/users/<int:id_user>/tasks', methods=['GET'])
def handle_user_tasks(id_user):
    user = User.query.get(id_user)
    if user is None:
        return "NO EXISTE", 404
    if id_user is None:
        raise APIException('You need to specify an existing user', status_code=400)
    tasks = Task.query.filter_by(user_id=id_user)
    response_body= []
    for task in tasks:
        response_body.append(task.serialize())
    return jsonify(response_body),200

#Endpoint para crear una tarea
@app.route('/tasks', methods=['POST'])
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
        if 'user_id' not in body:
            raise APIException("You need to specify the id group", status_code=400)

    else: return "error in body, is not a dictionary"
    now = datetime.utcnow()
    task1 = Task.create_task(
        group_id=body['group_id'],
        user_id=body['user_id'],
        label_task=body['label_task'],
        status_text=body['status_text'] if 'status_text' in body else None,
        status_task=body['status_task'] if 'status_task' in body else False,
        top_date=body['top_date'] if 'top_date' in body else None,
        init_date=now.strftime('%Y-%m-%d %H:%M:%S'))
    return task1.serialize(), 200

#Funcion para actualizar una propiedad de una tarea
@app.route('/tasks/<int:id_task>', methods=['PATCH'])
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
@app.route('/tasks/<int:id_task>', methods=['DELETE'])
def delete_task(id_task): 
    db.session.delete(Task.query.get_or_404(id_task) )
    db.session.commit() 
    return '', 204


#---------------------------------- endpoint Income --------------------------------

#Funcion para mostrar todas las ventas de un grupo 
@app.route('/groups/<int:id_group>/incomes', methods=['GET'])
def handle_group_income(id_group):
    group = Group.query.get(id_group)
    if group is None:
        return "NO EXISTE", 404
    if id_group is None:
        raise APIException('You need to specify an existing group', status_code=400)
    incomes = Income.query.filter_by(group_id=id_group)
    response_body= []
    for income in incomes:
        response_body.append(income.serialize())
    return jsonify(response_body),200

#Funcion para mostrar todas las ventas de un usuario 
@app.route('/users/<int:id_user>/incomes', methods=['GET'])
def handle_user_incomes(id_user):
    user = User.query.get(id_user)
    if user is None:
        return "NO EXISTE", 404
    if id_user is None:
        raise APIException('You need to specify an existing user', status_code=400)
    incomes = Income.query.filter_by(user_id=id_user)
    response_body= []
    for income in incomes:
        response_body.append(income.serialize())
    return jsonify(response_body),200

#Endpoint para crear una venta
@app.route('/incomes', methods=['POST'])
def add_new_income():
    body= request.get_json()
    #validaciones de body para campos obligatorios
    if isinstance (body,dict):
        if body is None:
            raise APIException("Please specify the request body as a json object", status_code=400)
        if 'date' not in body:
            raise APIException("You need to specify date", status_code=400)
        if 'coin' not in body:
            raise APIException("You need to specify coin", status_code=400)
        if 'payment' not in body:
            raise APIException("You need to specify payment", status_code=400)
        if 'method_payment' not in body:
            raise APIException("You need to specify the method_payment", status_code=400)     
        if 'amount' not in body:
            raise APIException("You need to specify amount", status_code=400)
        if 'usd_amount' not in body:
            raise APIException("You need to specify usd_amount", status_code=400)
        if 'rate_to_dolar' not in body:
            raise APIException("You need to specify usd_amount", status_code=400)
        if 'group_id' not in body:
            raise APIException("You need to specify the id group", status_code=400)
        if 'user_id' not in body:
            raise APIException("You need to specify the id user", status_code=400)

    else: return "error in body, is not a dictionary"
    now = datetime.utcnow()
    income1 = Income.create_income(
        group_id=body['group_id'],
        user_id=body['user_id'],
        date=body['date'] if 'date' in body else now.strftime('%Y-%m-%d %H:%M:%S'),
        coin=body['coin'],
        payment=body['payment'],
        method_payment=body['method_payment'],
        amount=body['amount'],
        usd_amount=body['usd_amount'],
        rate_to_dolar=body['rate_to_dolar'],
        bank=body['bank'] if 'bank' in body else None,
        description=body['description'],
    ) 
    return income1.serialize(), 200


#funcion para borrar una venta
@app.route('/incomes/<int:id_income>', methods=['DELETE'])
def delete_income(id_income): 
    db.session.delete(Income.query.get_or_404(id_income) )
    db.session.commit() 
    return '', 204

#---------------------------------- endpoint Expense --------------------------------

#Endpoint para mostrar todos los gastos de un grupo 
@app.route('/groups/<int:id_group>/expenses', methods=['GET'])
def handle_group_expenses(id_group):
    group = Group.query.get(id_group)
    if group is None:
        return "NO EXISTE", 404
    if id_group is None:
        raise APIException('You need to specify an existing group', status_code=400)
    expenses = Expense.query.filter_by(group_id=id_group)
    response_body= []
    for expense in expenses:
        response_body.append(expense.serialize())
    return jsonify(response_body),200

#Endpoint para mostrar todos los gastos de un usuario 
@app.route('/users/<int:id_user>/expenses', methods=['GET'])
def handle_user_expenses(id_user):
    user = User.query.get(id_user)
    if user is None:
        return "NO EXISTE", 404
    if id_user is None:
        raise APIException('You need to specify an existing user', status_code=400)
    expenses = Expense.query.filter_by(user_id=id_user)
    response_body= []
    for expense in expenses:
        response_body.append(expense.serialize())
    return jsonify(response_body),200

#Endpoint para crear un gasto
@app.route('/expenses', methods=['POST'])
def add_new_expense():
    body= request.get_json()
    #validaciones de body para campos obligatorios
    if isinstance (body,dict):
        if body is None:
            raise APIException("Please specify the request body as a json object", status_code=400)
        if 'date' not in body:
            raise APIException("You need to specify date", status_code=400)
        if 'coin' not in body:
            raise APIException("You need to specify coin", status_code=400)
        if 'payment' not in body:
            raise APIException("You need to specify payment", status_code=400)
        if 'method_payment' not in body:
            raise APIException("You need to specify the method_payment", status_code=400)
        if 'amount' not in body:
            raise APIException("You need to specify amount", status_code=400)
        if 'usd_amount' not in body:
            raise APIException("You need to specify usd_amount", status_code=400)
        if 'rate_to_dolar' not in body:
            raise APIException("You need to specify rate_to_dolar", status_code=400)
        if 'category' not in body:
            raise APIException("You need to specify the category", status_code=400)
        if 'group_id' not in body:
            raise APIException("You need to specify the id group", status_code=400)
        if 'user_id' not in body:
            raise APIException("You need to specify the id user", status_code=400)

    else: return "error in body, is not a dictionary"
    now = datetime.utcnow()
    expense1 = Expense.create_expense(
        group_id=body['group_id'],
        user_id=body['user_id'],
        date=body['date'] if 'date' in body else now.strftime('%Y-%m-%d %H:%M:%S'),
        coin=body['coin'],
        payment=body['payment'],
        method_payment=body['method_payment'],
        amount=body['amount'],
        usd_amount=body['usd_amount'],
        rate_to_dolar=body['rate_to_dolar'],
        category=body['category'],
        bank=body['bank'],
        provider=body['provider'],
        description=body['description'] if 'description' in body else None,
    ) 
    return expense1.serialize(), 200


#funcion para borrar un gasto
@app.route('/expenses/<int:id_expense>', methods=['DELETE'])
def delete_expense(id_expense): 
    db.session.delete(Expense.query.get_or_404(id_expense) )
    db.session.commit() 
    return '', 204

#Endpoint para registrar tipos de cambio (para usuario administrador de la app}/ no es para cliente)
@app.route('/rates', methods=['POST'])
def add_exchange_rate():
    body= request.get_json()
    #validaciones de body para campos obligatorios
    if isinstance (body,dict):
        if body is None:
            raise APIException("Please specify the request body as a json object", status_code=400)
        if 'coin' not in body:
            raise APIException("You need to specify the coin", status_code=400)
        if 'symbol' not in body:
            raise APIException("You need to specify the symbol", status_code=400)
        if 'rate_to_dolar' not in body:
            raise APIException("You need to specify the rate_to_dolar", status_code=400)
    else: return "error in body, is not a dictionary"
    now = datetime.utcnow()
    rate1 = Rate.create_rate(
        coin=body['coin'],
        symbol=body['symbol'],
        rate_to_dolar=body['rate_to_dolar'],
        last_update= now.strftime('%Y-%m-%d %H:%M:%S')
        )
    return rate1.serialize(), 200

#Endpoint para consultar todos los registros de tipos de cambio
@app.route('/rates', methods=['GET'])
def handle_rates():
    exchanges_rates = Rate.query.all()
    response_body= []
    for rate in exchanges_rates:
        response_body.append(rate.serialize())
    return jsonify(response_body),200



#this only runs if `$ python src/main.py` is executed.
#Esto solo se ejecuta si se ejecuta `$ python src / main.py`.
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)


