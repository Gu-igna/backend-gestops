from flask_restful import Resource
from flask import request
from .. import db
from sqlalchemy import and_, or_
from main.models import SubcategoriaModel
from main.auth.decorators import role_required

class Subcategoria(Resource):
    @role_required(roles=["admin", "supervisor"])
    def get(self, id):
        """Obtiene una subcategoria por su ID"""
        try:
            subcategoria  = db.session.query(SubcategoriaModel).get_or_404(id)
            return subcategoria.to_json(), 200
        except Exception as e:
            return {'message': str(e)}, 500

    @role_required(roles=["admin", "supervisor"])
    def delete(self, id):
        """Elimina una subcategoria por su ID"""
        try:
            subcategoria  = db.session.query(SubcategoriaModel).get_or_404(id)
            db.session.delete(subcategoria)
            db.session.commit()
            return {'message': 'Subcategoria eliminada'}, 204
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error al eliminar subcategoria: {str(e)}'}, 500
    
    @role_required(roles=["admin", "supervisor"])
    def put(self, id):
        """Actualiza una subcategoria por su ID"""
        try:
            subcategoria = db.session.query(SubcategoriaModel).get_or_404(id)
            data = request.get_json()

            for key, value in data.items():
                setattr(subcategoria, key, value)

            db.session.add(subcategoria)
            db.session.commit()
            return subcategoria.to_json(), 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error al actualizar subcategoria: {str(e)}'}, 500
    
class Subcategorias(Resource):
    @role_required(roles=["admin", "supervisor"])
    def get(self):
        """Obtiene lista paginada de subcategorias con opción de búsqueda"""
        try:
            page = request.args.get('page', default=1, type=int)
            per_page = request.args.get('per_page', default=10, type=int)

            query = db.session.query(SubcategoriaModel)

            query = self._aplicar_filtros_busqueda(query)

            subcategorias = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )

            return {
                'subcategorias': [subcategoria.to_json() for subcategoria in subcategorias.items],
                'total': subcategorias.total,
                'pages': subcategorias.pages,
                'page': subcategorias.page,
            }, 200
        except Exception as e:
            return {'message': str(e)}, 500

    def _aplicar_busqueda_general(self, query):
        """Aplica búsqueda global sobre varios campos."""
        search = request.args.get('busqueda')

        if search:
            conditions = [
                SubcategoriaModel.nombre.ilike(f'%{search}%'),
                SubcategoriaModel.categoria.has(
                    or_(
                        SubcategoriaModel.categoria.nombre.ilike(f'%{search}%'),
                        SubcategoriaModel.categoria.concepto.has(
                            SubcategoriaModel.categoria.concepto.property.mapper.class_.nombre.ilike(f'%{search}%')
                        )
                    )
                )
            ]

            return query.filter(or_(*conditions))
        
        return query
    
    def _aplicar_filtros_busqueda(self, query):
        """Aplica filtros específicos por campo."""
        filtros = []
        campos_busqueda = {
            'concepto': SubcategoriaModel.categoria.concepto.nombre,
            'categoria': SubcategoriaModel.categoria.nombre,
            'subcategoria': SubcategoriaModel.nombre,
        }
        for campo, valor in request.args.items():
            if campo in campos_busqueda:
                filtros.append(campos_busqueda[campo].like(f"%{valor}%"))
        return query.filter(and_(*filtros)) if filtros else query
    
    @role_required(roles=["admin", "supervisor"])
    def post(self):
        """Crea una nueva subcategoria"""
        try:
            data = request.get_json()
            if not data:
                return {'message': 'No se recibieron datos'}, 400
            
            if 'nombre' not in data:
                return {'message': 'Falta el nombre de la categoria'}, 400
            
            if 'id_categoria' not in data:
                return {'message': 'Falta el ID del categoria'}, 400
            
            new_subcategoria = SubcategoriaModel.from_json(data)
            db.session.add(new_subcategoria)
            db.session.commit()

            return new_subcategoria.to_json(), 201
        
        except ValueError as ve:
            return {'message': str(ve)}, 400
        
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error al crear la subcategoria', 'error': str(e)}, 500