from flask_restful import Resource
from flask import request
from .. import db
from sqlalchemy import and_
from main.models import CategoriaModel
from main.auth.decorators import role_required

class Categoria(Resource):
    @role_required(roles=["admin", "supervisor"])
    def get(self, id):
        """Obtiene una categoria por su ID"""
        try:
            categoria  = db.session.query(CategoriaModel).get_or_404(id)
            return categoria.to_json(), 200
        except Exception as e:
            return {'message': str(e)}, 500

    @role_required(roles=["admin", "supervisor"])
    def delete(self, id):
        """Elimina una categoria por su ID"""
        try:
            categoria  = db.session.query(CategoriaModel).get_or_404(id)
            db.session.delete(categoria)
            db.session.commit()
            return {'message': 'Categoria eliminada'}, 204
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error al eliminar categoria: {str(e)}'}, 500
    
    @role_required(roles=["admin", "supervisor"])
    def put(self, id):
        """Actualiza una categoria por su ID"""
        try:
            categoria = db.session.query(CategoriaModel).get_or_404(id)
            data = request.get_json()
            
            for key, value in data.items():
                setattr(categoria, key, value)

            db.session.add(categoria)
            db.session.commit()
            return categoria.to_json(), 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error al actualizar categoria: {str(e)}'}, 500
    
class Categorias(Resource):
    @role_required(roles=["admin", "supervisor"])
    def get(self):
        """Obtiene lista paginada de categorias con opción de búsqueda"""
        try:
            page = request.args.get('page', default=1, type=int)
            per_page = request.args.get('per_page', default=10, type=int)

            query = db.session.query(CategoriaModel)

            query = self._aplicar_filtros_busqueda(query)

            categorias = query.paginate(
                page=page, 
                per_page=per_page,
                error_out=False
            )

            return {
                'categorias': [categoria.to_json() for categoria in categorias.items],
                'total': categorias.total,
                'pages': categorias.pages,
                'page': categorias.page,
            }, 200
        except Exception as e:
            return {'message': str(e)}, 500
    

    def _aplicar_filtros_busqueda(self, query):
        """Aplica filtros de búsqueda al query"""
        filtros = []

        campos_busqueda = {
            'id': CategoriaModel.id,
            'nombre': CategoriaModel.nombre,
            'id_concepto': CategoriaModel.id_concepto
        }

        for campo, valor in request.args.items():
            if campo in campos_busqueda:
                filtros.append(campos_busqueda[campo].like(f"%{valor}%"))

        return query.filter(and_(*filtros)) if filtros else query

    @role_required(roles=["admin", "supervisor"])
    def post(self):
        """Crea una nueva categoria"""
        try:
            data = request.get_json()
            if not data:
                return {'message': 'No se recibieron datos'}, 400
            
            if 'nombre' not in data:
                return {'message': 'Falta el nombre de la categoria'}, 400
            
            if 'id_concepto' not in data:
                return {'message': 'Falta el ID del concepto'}, 400

            new_categoria = CategoriaModel.from_json(data)
            db.session.add(new_categoria)
            db.session.commit()

            return new_categoria.to_json(), 201
        
        except ValueError as ve:
            return {'message': str(ve)}, 400
        
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error al crear la categoria', 'error': str(e)}, 500