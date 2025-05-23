from flask_restful import Resource
from flask import request
from .. import db
from sqlalchemy import or_
from main.models import UsuarioModel
from main.auth.decorators import role_required

class Usuario(Resource):
    @role_required(roles=["admin","supervisor"])
    def get(self, id):
        """"Obtiene un usuario por su ID"""
        try:
            usuario = db.session.query(UsuarioModel).get_or_404(id)
            return usuario.to_json(), 200
        except Exception as e:
            return {'message': str(e)}, 500

    @role_required(roles=["admin"])
    def delete(self, id):
        """Elimina un usuario por su ID"""
        try:
            usuario = db.session.query(UsuarioModel).get_or_404(id)
            db.session.delete(usuario)
            db.session.commit()
            return {'message': 'Usuario eliminado correctamente'}, 204
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error al eliminar usuario: {str(e)}'}, 500

    @role_required(roles=["admin"])
    def patch(self, id):
        """Actualiza parcialmente un usuario, excluyendo la contraseña"""
        try:
            usuario = db.session.query(UsuarioModel).get_or_404(id)
            data = request.get_json()

            # Evitar la modificación de la contraseña por este método
            if 'password' in data:
                return {'message': 'No se puede modificar la contraseña usando este endpoint'}, 400

            for key, value in data.items():
                if hasattr(usuario, key):
                    setattr(usuario, key, value)
                    
            db.session.commit()
            return usuario.to_json(), 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error al actualizar usuario: {str(e)}'}, 500
    

class Usuarios(Resource):
    @role_required(roles=["admin","supervisor"])
    def get(self):
        """Obtiene lista paginada de usuarios con opción de búsqueda"""
        try:
            page = request.args.get('page', default=1, type=int)
            per_page = request.args.get('per_page', default=10, type=int)

            query = db.session.query(UsuarioModel)

            query = self._aplicar_busqueda_general(query)

            usuarios = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )

            return {
                'usuarios': [usuario.to_json() for usuario in usuarios.items],
                'total': usuarios.total,
                'pages': usuarios.pages,
                'page': usuarios.page,
            }, 200
        except Exception as e:
            return {'message': str(e)}, 500

    def _aplicar_busqueda_general(self, query):
        """Aplica filtros de búsqueda al query."""
        search = request.args.get('busqueda')

        if search:
            conditions = [
                UsuarioModel.id.ilike(f'%{search}%'),
                UsuarioModel.nombre.ilike(f'%{search}%'),
                UsuarioModel.apellido.ilike(f'%{search}%'),
                UsuarioModel.email.ilike(f'%{search}%'),
                UsuarioModel.rol.ilike(f'%{search}%')
            ]
            
            return query.filter(or_(*conditions))
        
        return query