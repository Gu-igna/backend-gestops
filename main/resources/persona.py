from flask_restful import Resource
from flask import request
from .. import db
from sqlalchemy import or_
from main.models import PersonaModel
from main.auth.decorators import role_required
import re

class Persona(Resource):
    @role_required(roles=["admin", "supervisor"])
    def get(self, id):
        """Obtiene una persona por su ID"""
        try:
            persona  = db.session.query(PersonaModel).get_or_404(id)
            return persona.to_json(), 200
        except Exception as e:
            return {'message': str(e)}, 500

    @role_required(roles=["admin", "supervisor"])
    def delete(self, id):
        """Elimina una persona por su ID"""
        try:
            persona  = db.session.query(PersonaModel).get_or_404(id)
            db.session.delete(persona)
            db.session.commit()
            return {'message': 'Persona eliminada'}, 204
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error al eliminar persona: {str(e)}'}, 500

    @role_required(roles=["admin", "supervisor"])
    def put(self, id):
        """Actualiza una persona por su ID"""
        try:
            persona = db.session.query(PersonaModel).get_or_404(id)
            data = request.get_json()

            for key, value in data.items():
                setattr(persona, key, value)

            db.session.add(persona)
            db.session.commit()
            return persona.to_json(), 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error al actualizar persona: {str(e)}'}, 500

class Personas(Resource):
    @role_required(roles=["admin", "supervisor"])
    def get(self):
        """Obtiene lista paginada de personas con opción de búsqueda"""
        try:
            page = request.args.get('page', default=1, type=int)
            per_page = request.args.get('per_page', default=10, type=int)

            query = db.session.query(PersonaModel)

            query = self._aplicar_busqueda_general(query)

            personas = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False, 
            )

            return {
                'personas': [persona.to_json() for persona in personas.items],
                'total': personas.total,
                'pages': personas.pages,
                'page': personas.page,
            }, 200
        except Exception as e:
            return {'message': str(e)}, 500

    def _aplicar_busqueda_general(self, query):
        """Aplica filtros de búsqueda al query."""
        search = request.args.get('busqueda')

        if search:
            conditions = [
                PersonaModel.id.ilike(f'%{search}%'),
                PersonaModel.cuit.ilike(f'%{search}%'),
                PersonaModel.razon_social.ilike(f'%{search}%'),
            ]

            return query.filter(or_(*conditions))
        return query


    @role_required(roles=["admin", "supervisor"])
    def post(self):
        """Crea una nueva persona"""
        try:
            data = request.get_json()
            if not data:
                return {'message': 'No se recibieron datos'}, 400
            
            if 'cuit' not in data:
                return {'message': 'Falta el CUIT de la persona'}, 400
            
            if 'razon_social' not in data:
                return {'message': 'Falta la razón social de la persona'}, 400
            
            new_persona = PersonaModel.from_json(data)
            db.session.add(new_persona)
            db.session.commit()

            return new_persona.to_json(), 201
        
        except Exception as ve:
            return {'message': str(ve)}, 400
        
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error al crear persona: {str(e)}'}, 500