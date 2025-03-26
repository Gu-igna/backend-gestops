from flask_restful import Resource, current_app
from flask import request, send_file
from werkzeug.utils import secure_filename
import os, uuid
from .. import db
from main.models import OperacionModel, UsuarioModel
from flask_jwt_extended import get_jwt_identity
from main.auth.decorators import role_required

class ArchivoOperacion(Resource):
    @role_required(roles=["admin", "supervisor"])
    def get(self, id_operacion, campo_archivo):
        try:
            operacion = OperacionModel.query.get(id_operacion)
            if not operacion:
                return {'message': 'Operación no encontrada'}, 404

            file_path = getattr(operacion, f"{campo_archivo}_path", None)

            if not file_path:
                return {'message': f'El archivo {campo_archivo} no está registrado'}, 404

            full_path = os.path.abspath(file_path)

            if not os.path.exists(full_path):
                return {'message': f'El archivo {campo_archivo} no existe o no es accesible'}, 404

            return send_file(full_path)

        except Exception as e:
            return {'message': 'Error al obtener el archivo', 'error': str(e)}, 500

    @role_required(roles=["admin", "supervisor"])
    def patch(self, id_operacion, campo_archivo):
        """Actualiza un archivo específico de una operación"""
        try:
            operacion = OperacionModel.query.get(id_operacion)
            if not operacion:
                return {'message': 'Operación no encontrada'}, 404

            usuario_actual_id = get_jwt_identity()
            usuario_actual = UsuarioModel.query.get(usuario_actual_id)

            es_creador = int(operacion.id_usuario) == int(usuario_actual_id)
            es_supervisor = "supervisor" == str(usuario_actual.rol)


            if not (es_creador or es_supervisor):
                return {'message': 'No tienes permiso para editar esta operación'}, 403

            if es_supervisor and not es_creador:
                operacion.modificado_por_otro = True

            if es_creador and not es_supervisor :
                operacion.modificado_por_otro = False

            campos_validos = ['comprobante', 'archivo1', 'archivo2', 'archivo3']
            if campo_archivo not in campos_validos:
                return {'message': f'Campo de archivo "{campo_archivo}" no permitido'}, 400

            if campo_archivo not in request.files:
                return {'message': f'No se envió el archivo "{campo_archivo}"'}, 400

            file = request.files[campo_archivo]

            if file and file.filename:
                old_path = getattr(operacion, f"{campo_archivo}_path")
                if old_path and os.path.exists(old_path):
                    os.remove(old_path)

                filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']

                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)

                setattr(operacion, f"{campo_archivo}_path", file_path)
                setattr(operacion, f"{campo_archivo}_tipo", file.content_type)

                db.session.commit()

                return {
                    'message': f'Archivo "{campo_archivo}" actualizado correctamente',
                    'archivo_actualizado': campo_archivo,
                    'modificado_por_otro': operacion.modificado_por_otro
                }, 200

            return {'message': f'El archivo "{campo_archivo}" no es válido'}, 400

        except Exception as e:
            db.session.rollback()
            return {'message': 'Error al actualizar el archivo', 'error': str(e)}, 500

class ArchivosOperaciones(Resource):
    @role_required(roles=["admin"])
    def post(self, id_operacion):
        try:
            operacion = OperacionModel.query.get(id_operacion)
            if not operacion:
                return {'message': 'Operación no encontrada'}, 404
            
            if 'comprobante' in request.files:
                comprobante_path, comprobante_tipo = self._procesar_archivo('comprobante')
                operacion.comprobante_path = comprobante_path
                operacion.comprobante_tipo = comprobante_tipo
            
            if 'archivo1' in request.files:
                archivo1_path, archivo1_tipo = self._procesar_archivo('archivo1')
                operacion.archivo1_path = archivo1_path
                operacion.archivo1_tipo = archivo1_tipo
                
            if 'archivo2' in request.files:
                archivo2_path, archivo2_tipo = self._procesar_archivo('archivo2')
                operacion.archivo2_path = archivo2_path
                operacion.archivo2_tipo = archivo2_tipo
                
            if 'archivo3' in request.files:
                archivo3_path, archivo3_tipo = self._procesar_archivo('archivo3')
                operacion.archivo3_path = archivo3_path
                operacion.archivo3_tipo = archivo3_tipo
            
            db.session.commit()
            
            return {'message': 'Archivos adjuntados correctamente'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error al adjuntar archivos', 'error': str(e)}, 500
    
    def _procesar_archivo(self, file_key):
        if file_key in request.files:
            file = request.files[file_key]
            if file.filename:
                filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']
                        
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                        
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                        
                return file_path, file.content_type
        return None, None