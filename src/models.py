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
    name= db.Column(db.String (120))
    last_name=db.Column(db.String(120))
    user_name=db.Column(db.String(120), unique=True, nullable=False)
    cedula_rif=db.Column(db.String(120))
    country=db.Column(db.String(120))
    country_code=db.Column(db.String(3), nullable=False)
    region_state=db.Column(db.String(120))
    municipality=db.Column(db.String(120))
    hashed_password=db.Column(db.String(120),unique=False, nullable=False)
    salt=db.Column(db.String(120), nullable=False)#Esto es un numero aleatorio que sera agregado al password
    url=db.Column(db.String(500), unique=True)
    url_image=db.Column(db.String(500))
    user_registered=db.Column(db.String(120))

    create_groups=db.relationship("Group",backref="user")
    groups=db.relationship("PersonGroup",backref="user")
    tasks=db.relationship("Task",backref="user")
    incomes=db.relationship("Income",backref="user")
    expenses=db.relationship("Expense",backref="user")

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
        self.country_code=body['country_code']
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
            "municipality":self.municipality,
            "url":self.url,
            "url_image":self.url_image,
            "user_registered":self.user_registered
        }

class Group(db.Model):

    id=db.Column(db.Integer,primary_key=True)
    user_admin_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    group_name= db.Column(db.String(120), nullable=False)
    description= db.Column(db.String(250))
    group_url=db.Column(db.String(500),nullable=False, unique=True)
    url_image=db.Column(db.String(500))

    users=db.relationship("PersonGroup",backref="group")
    expenses=db.relationship("Expense",backref="group")
    incomes=db.relationship("Income",backref="group")
    tasks=db.relationship("Task",backref="group")

    def __init__(self,body):
        self.group_name=body['group_name']
        self.user_admin_id=body['user_admin_id']
        self.description=body['description']
        self.group_url=body['group_url']
        self.url_image=body['url_image']
       

    @classmethod
    def create_group(cls,**kwargs):
        new_group=cls(kwargs)
        db.session.add(new_group)
        db.session.commit()
        return new_group
         

    def serialize(self):
        return {
            "id":self.id,
            "user_admin_id":self.user_admin_id,
            "group_name":self.group_name,
            "description":self.description,
            "group_url":self.group_url,
            "url_image":self.url_image
        }


class PersonGroup(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id=db.Column(db.Integer,db.ForeignKey('group.id'))

    def __init__(self,body):
        self.user_id=body['user_id']
        self.group_id=body['group_id']


    @classmethod
    def create_person_group(cls,**kwargs):
        new_person_group=cls(kwargs)
        db.session.add(new_person_group)
        db.session.commit()
        return new_person_group
    
    def serialize(self):
        return {
            "id":self.id,
            "user_id":self.user_id,
            "group_id":self.group_id
        }



class Income(db.Model): #es el equivalente a income del front
    id=db.Column(db.Integer, primary_key=True)
    date=db.Column(db.String(120),nullable=False)
    coin=db.Column(db.String(100),nullable=False)
    payment=db.Column(db.String(300),nullable=False)
    method_payment=db.Column(db.String(120),nullable=False)
    amount=db.Column(db.Float,nullable=False)
    usd_amount=db.Column(db.Float,nullable=False)
    rate_to_dolar=db.Column(db.Float,nullable=False)
    bank=db.Column(db.String(120))
    description=db.Column(db.String(100))

    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id=db.Column(db.Integer,db.ForeignKey('group.id'))

    def __init__(self,body):
        self.date=body['date']
        self.coin=body['coin']
        self.payment=body['payment']
        self.method_payment=body['method_payment']
        self.amount=body['amount']
        self.usd_amount=body['usd_amount']
        self.rate_to_dolar=body['rate_to_dolar']
        self.bank=body['bank']
        self.description=body['description']

        self.group_id=body['group_id']
        self.user_id=body['user_id']

    @classmethod
    def create_income(cls,**kwargs):
        new_income=cls(kwargs)
        db.session.add(new_income)
        db.session.commit()
        return new_income
        

    def serialize(self):
        return {
            "id":self.id,
            "date":self.date,
            "coin":self.coin,
            "payment": self.payment,
            "method_payment":self.method_payment,
            "amount":self.amount,
            "usd_amount":self.usd_amount, 
            "rate_to_dolar": self.rate_to_dolar, 
            "bank":self.bank,
            "description":self.description,
            "group_id":self.group_id
        }
    
class Expense(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    date=db.Column(db.String(120),nullable=False)
    coin=db.Column(db.String(120),nullable=False)
    payment=db.Column(db.String(300),nullable=False)
    method_payment=db.Column(db.String(120),nullable=False)
    amount=db.Column(db.Float,nullable=False)
    usd_amount=db.Column(db.Float,nullable=False)
    rate_to_dolar=db.Column(db.Float,nullable=False)
    category=db.Column(db.String(120),nullable=False)
    bank=db.Column(db.String(120))
    provider=db.Column(db.String(120),nullable=False)
    description=db.Column(db.String(300))
    
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id=db.Column(db.Integer,db.ForeignKey('group.id'))

    def __init__(self,body):
        self.date=body['date']
        self.coin=body['coin']
        self.payment=body['payment']
        self.method_payment=body['method_payment']
        self.amount=body['amount']
        self.usd_amount=body['usd_amount']
        self.rate_to_dolar=body['rate_to_dolar']
        self.category=body['category']
        self.provider=body['provider']
        self.bank=body['bank']
        self.description=body['description']
        self.group_id=body['group_id']
        self.user_id=body['user_id']

    @classmethod
    def create_expense(cls,**kwargs):
        new_expense=cls(kwargs)
        db.session.add(new_expense)
        db.session.commit()
        return new_expense
        
    def serialize(self):
        return {
            "id":self.id,
            "date":self.date,
            "coin":self.coin,
            "payment": self.payment,
            "method_payment":self.method_payment,
            "amount": self.amount,
            "usd_amount":self.usd_amount,
            "rate_to_dolar":self.rate_to_dolar,
            "category":self.category,
            "provider":self.provider,
            "bank": self.bank,
            "description":self.description,
            "group_id":self.group_id,
            "user_id":self.user_id
        }
    
class Task(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    label_task=db.Column(db.String(120),nullable=False)
    status_text=db.Column(db.String(300))
    status_task=db.Column(db.Boolean)
    top_date=db.Column(db.String(120))
    init_date=db.Column(db.String(120),nullable=False)
    
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id=db.Column(db.Integer,db.ForeignKey('group.id'))

    def __init__(self,body):
        self.label_task=body['label_task']
        self.status_text=body['status_text']
        self.status_task=body['status_task']
        self.top_date=body['top_date']
        self.init_date=body['init_date']
        self.group_id=body['group_id']
        self.user_id=body['user_id']
        
    @classmethod
    def create_task(cls,**kwargs):
        new_task=cls(kwargs)
        db.session.add(new_task)
        db.session.commit()
        return new_task      

    def serialize(self):
        return {
            "id":self.id,
            "group_id":self.group_id,
            "user_id":self.user_id,
            "label_task":self.label_task,
            "status_text":self.status_text,
            "status_task":self.status_task,
            "top_date":self.top_date,
            "init_date":self.init_date
        }

class Rate(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    coin=db.Column(db.String(120),nullable=False)
    symbol=db.Column(db.String(6),nullable=False)
    rate_to_dolar=db.Column(db.Float,nullable=False)
    last_update=db.Column(db.String(120),nullable=False)

    def __init__(self,body):
        self.coin=body['coin']
        self.symbol=body['symbol']
        self.rate_to_dolar=body['rate_to_dolar']
        self.last_update=body['last_update']

    @classmethod
    def create_rate(cls,**kwargs):
        new_rate=cls(kwargs)
        db.session.add(new_rate)
        db.session.commit()
        return new_rate 

    def serialize(self):
        return {
            "id":self.id,
            "coin":self.coin,
            "symbol":self.symbol,
            "rate_to_dolar":self.rate_to_dolar,
            "last_update":self.last_update
        }