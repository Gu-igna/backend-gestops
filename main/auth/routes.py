from flask import request, jsonify, Blueprint
from .. import db
from main.models import UsuarioModel
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from main.mail.functions import sendMail
from datetime import datetime, timedelta
import secrets

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login', methods=['POST']) 
def login():
    data = request.get_json()

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email y contraseña son obligatorios"}), 400

    usuario = db.session.query(UsuarioModel).filter_by(email=data["email"]).first_or_404(description="El usuario no existe")

    if usuario.validate_pass(data.get("password")):
        access_token = create_access_token(identity=usuario)
        return jsonify({"access_token": access_token, "usuario": usuario.to_json_short()}), 200
    else:
        return jsonify({"error": "Contraseña incorrecta"}), 401

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    required_fields = ['nombre', 'apellido', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    usuario = UsuarioModel.from_json(data)

    if db.session.query(UsuarioModel.id).filter(UsuarioModel.email == usuario.email).scalar():
        return jsonify({"error": "Email duplicado"}), 409

    try:
        new_password = secrets.token_urlsafe(10)
        usuario.plain_password = new_password

        db.session.add(usuario)
        db.session.commit()

        sendMail([usuario.email], "Bienvenido!", 'register', new_password=new_password, usuario=usuario)

    except Exception as error:
        db.session.rollback()
        return jsonify({"error": "Error al registrar el usuario"}), 500

    return usuario.to_json(), 201

@auth.route('/reset-password', methods=['POST'])
def reset_password():
    mail = request.get_json().get("email")

    try:
        usuario = db.session.query(UsuarioModel).filter_by(email=mail).first()

        usuario.reset_token = secrets.token_urlsafe(32)
        usuario.token_expiration = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()

        sendMail([mail], 'Restablecer Contraseña', 'resetpassword', reset_token=usuario.reset_token, usuario=usuario)

        return {'message': 'Si el correo está registrado, recibirás un enlace para restablecer la contraseña.'}, 200
    
    except Exception as error:
        print(f"Error en recuperación de contraseña: {error}")
        return jsonify({'error': 'Ocurrió un error al procesar la solicitud'}), 500


@auth.route('/update-password', methods=['POST'])
@jwt_required(optional=True)
def update_password():
    data = request.get_json()
    reset_token = data.get("reset_token")
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not new_password:
        return jsonify({'message': 'La nueva contraseña es obligatoria'}), 400

    usuario = None

    if reset_token:
        usuario = db.session.query(UsuarioModel).filter_by(reset_token=reset_token).first()
        if not usuario:
            return jsonify({'error': 'Token inválido'}), 400
        if usuario.token_expiration < datetime.utcnow():
            return jsonify({'error': 'Token expirado'}), 400
        
    else:
        usuario_id = get_jwt_identity()
        usuario = db.session.query(UsuarioModel).get(usuario_id)
        if not usuario or not current_password or not usuario.validate_pass(current_password):
            return jsonify({'error': 'Credenciales inválidas'}), 400

    try:
        usuario.plain_password = new_password
        usuario.reset_token = None
        usuario.token_expiration = None
        db.session.commit()

        return jsonify({'message': 'Contraseña actualizada correctamente'}), 200
    
    except Exception as error:
        db.session.rollback()
        print(f"Error al actualizar la contraseña: {error}")
        return jsonify({'error': 'Error interno del servidor'}), 500