from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

    def __init__(self, body):
        self.email = body['email']
        self.salt= os.urandom(16).hex()
        self.hashed_password=self.set_password(body['password'])

#estoo es para crear el usuario
    @classmethod
    def create(cls,body):
        return new_user=User(body)

    def set_password(self):
        return generate_password_hash(
            self.salt, 
            password
            )
