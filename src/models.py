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

class login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(10), nullable=False)
    
    # we could add a Username.
    # podríamos agregar un Username.
    def serialize(self): 
        return {
            "id": self.id,
            "name": self.name,
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    hashed_password = db.Column(db.String(120), nullable=False)
    salt = db.Column(db.String(120), nullable=False)
    def __init__(self, data):
        self.email = data['email']
        self.salt = b64encode(os.urandom(4)).decode("utf-8")
        self.hashed_password = self.set_password(
            data['password']
        )
    @classmethod
    def create(cls, data):
        user = cls(data)
        db.session.add(user)
        db.session.commit()
        return user
    def set_password(self, password):
        return generate_password_hash(
            f"{password}{self.salt}"
        )
    def check_password(self, password):
        return check_password_hash(
            self.hashed_password,
            f"{password}{self.salt}"
        )
    def serialize(self):
        return {
            "id": self.id,
            "email": self.email
            # do not serialize the password, its a security breach.
            # No serialice la contraseña, es una violación de seguridad.
        }

    def __repr__(self):
        return '<User %r>' % self.username
