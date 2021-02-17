#From this line start de OptiTask Project Backend.
#Desde esta linea comienza el proyecto de OptiTask Backend.

"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints.
Este módulo se encarga de crear la clase User, cargar la base de datos y agregar los puntos finales.
"""

from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash
from base64 import b64encode
db = SQLAlchemy()

class User(db.Model):

    id=db.Column(db.Integer,primary_key=True)
    email= db.Column(db.String(120),unique=True, nullable=False)
    name= db.Column(db.String (20))
    last_name=db.Column(db.String(20))
    user_name=db.Column(db.String(20), unique=True, nullable=False)
    cedula_rif=db.Column(db.String(20))
    country=db.Column(db.String(120))
    country_code=db.Column(db.String(3), nullable=False)
    region_state=db.Column(db.String(120))
    municipality=db.Column(db.String(120))
    hashed_password=db.Column(db.String(120),unique=False, nullable=False)
    salt=db.Column(db.String(120), nullable=False)#Esto es un numero aleatorio que sera agregado al password
    url=db.Column(db.String(500), unique=True)
    url_image=db.Column(db.String(500))
    user_registered=db.Column(db.String(50))
    groups=db.relationship("User_group",backref="user")

#Esto es para crear el usuario
    @classmethod
    def create(cls,**kwargs):
        new_user=cls(kwargs)
        db.session.add(new_user)
        db.session.commit()
        return new_user
    
    def __init__(self,body):
        self.email=body ['email']
        self.name=body['name'] 
        self.last_name=body['last_name']
        self.user_name=body['user_name']
        self.cedula_rif=body['cedula_rif']
        self.country=body['country']
        self.country_code['country_code']
        self.region_state=body['region_state']
        self.municipality=body['municipality']
        self.salt=b64encode(os.urandom(4)).decode("utf-8")
        self.hashed_password=self.set_password(body['password'])
        self.url=body['url']
        self.url_image=body['url_image']
        self.user_registered=body['user_registered']       

    def set_password(self, password):
        return generate_password_hash(
            f"{password}{self.salt}"
        )

    def check_password(self, password):
        print(f"este es el password:{password}")
        return check_password_hash(
            self.hashed_password,
            f"{password}{self.salt}"
        )

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
            "name":self.name,
            "last_name":self.last_name,
            "user_name":self.user_name,
            "cedula_rif":self.cedula_rif,
            "country":self.country,
            "country_code":self.country_code,
            "region_state":self.region_state,
            "municipality":self.municipality
        }

class Group(db.Model):

    id=db.Column(db.Integer,primary_key=True)
    group_name= db.Column(db.String(120), nullable=False)
    descripcion= db.Column(db.String(250))
    target_time=db.Column(db.String(120))
    group_url=db.Column(db.String(500),nullable=False, unique=True)
    url_image=db.Column(db.String(500))
    users=db.relationship("User_group",backref="group")

    def __init__(self,body):
        self.group_name=body['group_name']
        self.description=body['description']
        self.target_time=body['target_time']
        self.group_url=body['group_url']
        self.url_image=body['url_image']
        

    def serialize(self):
        return {
            "id":self.id,
            "group_name":self.group_name,
            "description":self.description,
            "target_time":self.target_time,
            "group_url":self.group_url,
            "url_image":self.url_image
        }


class User_group:
    id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id=db.Column(db.Integer,db.ForeignKey('group.id'))


class Sale:
    id=db.Column(db.Integer, primary_key=True)
    date=db.Column(db.String(120),nullable=False)
    description=db.Column(db.String(300),nullable=False)
    method_payment=db.Column(db.String(120),nullable=False)
    amount=db.Column(db.String(120),nullable=False)
    bank=db.Column(db.String(120),nullable=False)
    usd_amount=db.Column(db.Float,nullable=False)

    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id=db.Column(db.Integer,db.ForeignKey('group.id'))

    def __init__(self,body):
        self.date=body['date']
        self.description=body['description']
        self.method_payment=body['method_payment']
        self.amount=body['amount']
        self.bank=body['bank']
        self.usd_amount=body['usd_amount']
        

    def serialize(self):
        return {
            "id":self.id,
            "date":self.date,
            "description":self.description,
            "method_payment":self.method_payment,
            "amount":self.amount,
            "bank":self.bank,
            "usd_amount":self.usd_amount
        }
    
class Expense:
    id=db.Column(db.Integer, primary_key=True)
    date=db.Column(db.String(120),nullable=False)
    description=db.Column(db.String(300),nullable=False)
    method_payment=db.Column(db.String(120),nullable=False)
    usd_amount=db.Column(db.Float,nullable=False)
    coin=db.Column(db.String(120),nullable=False)
    category=db.Column(db.String(120),nullable=False)
    provider=db.Column(db.String(120),nullable=False)
    
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id=db.Column(db.Integer,db.ForeignKey('group.id'))

    def __init__(self,body):
        self.date=body['date']
        self.description=body['description']
        self.method_payment=body['method_payment']
        self.coin=body['coin']
        self.category=body['category']
        self.provider=body['provider']
        self.usd_amount=body['usd_amount']
        

    def serialize(self):
        return {
            "id":self.id,
            "date":self.date,
            "description":self.description,
            "method_payment":self.method_payment,
            "coin":self.coin,
            "category":self.category,
            "provider":self.provider,
            "usd_amount":self.usd_amount
        }
    
class Task:
    id=db.Column(db.Integer, primary_key=True)
    label_task=db.Column(db.String(120),nullable=False)
    status_text=db.Column(db.String(300),nullable=False)
    status_task=db.Column(db.Boolean,nullable=False)
    top_date=db.Column(db.String,nullable=False)
    init_date=db.Column(db.String(120),nullable=False)
    
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id=db.Column(db.Integer,db.ForeignKey('group.id'))

    def __init__(self,body):
        self.label_task=body['label_task']
        self.status_text=body['status_text']
        self.status_task=body['status_task']
        self.top_date=body['top_date']
        self.init_date=body['init_date']

        

    def serialize(self):
        return {
            "id":self.id,
            "label_task":self.label_task,
            "status_text":self.status_text,
            "status_task":self.status_task,
            "top_date":self.top_date,
            "init_date":self.init_date,

        }