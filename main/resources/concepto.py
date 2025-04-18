from flask_restful import Resource
from flask import request
from .. import db
from sqlalchemy import or_
from main.models import ConceptoModel
from main.auth.decorators import role_required

class Concepto(Resource):
    @role_required(roles=["admin", "supervisor"])
    def get(self, id):
        """"Obtiene un concepto por su ID"""
        try:
            concepto  = db.session.query(ConceptoModel).get_or_404(id)
            return concepto.to_json(), 200
        except Exception as e:
            return {'message': str(e)}, 500

    @role_required(roles=["admin", "supervisor"])
    def delete(self, id):
        """"Elimina un concepto por su ID"""
        try:
            concepto  = db.session.query(ConceptoModel).get_or_404(id)
            db.session.delete(concepto)
            db.session.commit()
            return {'message': 'Concepto eliminado'}, 204
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error al eliminar concepto: {str(e)}'}, 500

    @role_required(roles=["admin", "supervisor"])
    def put(self, id):
        """"Actualiza un concepto por su ID"""
        try:
            concepto = db.session.query(ConceptoModel).get_or_404(id)
            data = request.get_json()

            for key, value in data.items():
                setattr(concepto, key, value)

            db.session.add(concepto)
            db.session.commit()
            return concepto.to_json(), 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error al actualizar concepto: {str(e)}'}, 500
    
class Conceptos(Resource):
    @role_required(roles=["admin", "supervisor"])
    def get(self):
        """Obtiene lista paginada de conceptos con opción de búsqueda"""
        try:
            page = request.args.get('page', default=1, type=int)
            per_page = request.args.get('per_page', default=10, type=int)

            query = db.session.query(ConceptoModel)
            query = self._aplicar_busqueda_general(query)

            if (page == 0 and per_page == 0):
                conceptos_items = query.all()
                return {
                    'conceptos': [concepto.to_json() for concepto in conceptos_items],
                    'total': len(conceptos_items),
                    'pages': 1,
                    'page': 1,
                }, 200
            else:
                conceptos = query.paginate(
                    page=page, 
                    per_page=per_page,
                    error_out=False
                )

                return {
                    'conceptos': [concepto.to_json() for concepto in conceptos.items],
                    'total': conceptos.total,
                    'pages': conceptos.pages,
                    'page': conceptos.page,
                }, 200
        except Exception as e:
            return {'message': str(e)}, 500
        
    def _aplicar_busqueda_general(self, query):
        """Aplica filtros de búsqueda al query"""
        search = request.args.get('busqueda')

        if search:
            conditions = [
                ConceptoModel.id.ilike(f'%{search}%'),
                ConceptoModel.nombre.ilike(f'%{search}%'),
            ]

            return query.filter(or_(*conditions))
        
        return query

    @role_required(roles=["admin", "supervisor"])
    def post(self):
        """Crea un nuevo concepto"""
        try:
            data = request.get_json()
            if not data:
                return {'message': 'No se recibieron datos'}, 400
            
            if 'nombre' not in data:
                return {'message': 'Falta el nombre del concepto'}, 400
            
            if db.session.query(ConceptoModel).filter(ConceptoModel.nombre == data['nombre']).first():
                return {'message': 'Ya existe un concepto con ese nombre'}, 400

            new_concepto = ConceptoModel.from_json(data)
            db.session.add(new_concepto)
            db.session.commit()

            return new_concepto.to_json(), 201
        
        except ValueError as ve:
            return {'message': str(ve)}, 400
        
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error al crear el concepto', 'error': str(e)}, 500