from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash,check_password_hash
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
    region_state=db.Column(db.String(120))
    municipality=db.Column(db.String(120))
    hashed_password=db.Column(db.String(120),unique=False, nullable=False)
    salt=db.Column(db.String(120), nullable=False)#Esto es un numero aleatorio que sera agregado al password
    url=db.Column(db.String(500), unique=True)
    url_image=db.Column(db.String(500))
    user_registered=db.Column(db.String(50))

#estoo es para crear el usuario
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
        self.region_state=body['region_state']
        self.municipality=body['municipality']
        self.hashed_password=self.set_password(body['password'])
        self.salt=b64encode(os.urandom(4)).decode("utf-8")
        self.url=body['url']
        self.url_image=body['url_image']
        self.user_registered=body['user_registered']       

    def set_password(self, password):
        return generate_password_hash(
            f"{password}{self.salt}"
        )

    def check_password(self, password):
        return check_password_hash(
            self.hashed_password,
            f"{password}{self.salt}"
        )

    def __repr__(self):
         return '<User %r>' % self.username

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
            "region_state":self.region_state,
            "municipality":self.municipality
        }