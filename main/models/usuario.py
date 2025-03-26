from .. import db
import re
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model):

    ROLES_PERMITIDOS = ['user', 'admin', 'supervisor']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100) ,nullable=False)
    email = db.Column(db.String(150), unique=True, index=True, nullable=False)
    password = db.Column(db.String, nullable=True)
    rol = db.Column(db.String(20), nullable=True)

    reset_token = db.Column(db.String, nullable=True)
    token_expiration = db.Column(db.DateTime, nullable=True)

    operaciones = db.relationship("Operacion", back_populates="usuario")

    @db.validates('email')
    def validate_email(self, key, value):
        email_pattern = re.compile(r'^[a-zA-Z0-9_\-\.~]{2,}@[a-zA-Z0-9_\-\.~]{2,}\.[a-zA-Z]{2,4}$')
        if not email_pattern.match(value):
            raise ValueError("Formato de email inválido.")
        return value
    
    @db.validates('rol')
    def validate_rol(self, key, value):
        if value not in self.ROLES_PERMITIDOS:
            raise ValueError("Rol inválido.")
        return value

    @property
    def plain_password(self):
        raise AttributeError('La contraseña no se puede leer directamente.')
    
    @plain_password.setter
    def plain_password(self, password):
        self.password = generate_password_hash(password)
        
    def validate_pass(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f"<Usuario {self.id}: {self.nombre} {self.apellido}, {self.email}, rol={self.rol}>"
    
    def to_json(self):
        usuario_json = {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'email': self.email,
            'rol': self.rol
        }
        return usuario_json

    def to_json_short(self):
        usuario_json = {
            'id': self.id,
            'email': self.email,
            'rol': self.rol
        }
        return usuario_json

    @staticmethod
    def from_json(usuario_json):
        id = usuario_json.get('id')
        nombre = usuario_json.get('nombre')
        apellido = usuario_json.get('apellido')
        email = usuario_json.get('email')
        password = usuario_json.get('password')
        rol = usuario_json.get('rol')
        return Usuario(
                    id=id,
                    nombre=nombre,
                    apellido=apellido,     
                    email=email,
                    plain_password=password,
                    rol=rol
                    )