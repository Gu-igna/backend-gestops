from .. import db
from datetime import datetime
import re 

class Operacion(db.Model):

    TIPOS_PERMITIDOS = ['ingreso', 'egreso']
    CARACTERES_PERMITIDOS = ['casa', 'oficina']
    NATURALEZAS_PERMITIDAS = ['societario', 'personal']
    OPTIONS_PERMITIDAS = ['factura', 'boleta']
    METODOS_PAGO_PERMITIDOS = ['efectivo', 'transferencia', 'mixto', 'otro']


    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.String(10), nullable=False)
    caracter = db.Column(db.String(10), nullable=False)
    naturaleza = db.Column(db.String(10), nullable=False)

    id_persona = db.Column(db.Integer, db.ForeignKey("persona.id"), nullable=False)
    personas = db.relationship("Persona", back_populates="operaciones", single_parent=True)

    comprobante_path = db.Column(db.String(255), nullable=True)
    comprobante_tipo = db.Column(db.String(10), nullable=True)

    option = db.Column(db.String(10), nullable=False)
    codigo = db.Column(db.String(10), nullable=False)
    observaciones = db.Column(db.String(255), nullable=True)
    metodo_de_pago = db.Column(db.String(20), nullable=False)
    _monto_total = db.Column('monto_total', db.Numeric(precision=65, scale=5), nullable=False)

    id_subcategoria = db.Column(db.Integer, db.ForeignKey("subcategoria.id"), nullable=False)
    subcategoria = db.relationship("Subcategoria", back_populates="operaciones", single_parent=True)
    
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    usuario = db.relationship("Usuario", back_populates="operaciones", single_parent=True)


    archivo1_path = db.Column(db.String(255), nullable=True)
    archivo1_tipo = db.Column(db.String(10), nullable=True)
    archivo2_path = db.Column(db.String(255), nullable=True)
    archivo2_tipo = db.Column(db.String(10), nullable=True)
    archivo3_path = db.Column(db.String(255), nullable=True)
    archivo3_tipo = db.Column(db.String(10), nullable=True)

    modificado_por_otro = db.Column(db.Boolean, nullable=False, default=False)
    
    @property
    def monto_total(self):
        """Devuelve el monto con el signo correcto según el tipo de operación."""
        return self._monto_total


    @monto_total.setter
    def monto_total(self, value):
        """Convierte el valor a absoluto antes de guardarlo y aplica el signo correcto."""
        monto_abs = abs(value)

        if self.tipo == "egreso":
            self._monto_total = -monto_abs
        else:
            self._monto_total = monto_abs


    def actualizar_tipo_operacion(self, nuevo_tipo_operacion):
        """Método para actualizar el tipo de operación y ajustar el monto en consecuencia."""
        if nuevo_tipo_operacion != self.tipo:
            self.tipo = nuevo_tipo_operacion

            if nuevo_tipo_operacion == "egreso":
                self._monto_total = -abs(self._monto_total)
            else:
                self._monto_total = abs(self._monto_total)

    @db.validates('fecha')
    def validate_fecha(self, key, value):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid FECHA format. It should be in the format 'YYYY-MM-DD'.")

    @db.validates('tipo')
    def validate_tipo(self, key, value):
        if value.lower() not in self.TIPOS_PERMITIDOS:
            raise ValueError(f"Invalid tipo. Must be one of: {', '.join(self.TIPOS_PERMITIDOS)}")
        return value.lower()

    @db.validates('caracter')
    def validate_caracter(self, key, value):
        if value.lower() not in self.CARACTERES_PERMITIDOS:
            raise ValueError(f"Invalid caracter. Must be one of: {', '.join(self.CARACTERES_PERMITIDOS)}")
        return value.lower()
    
    @db.validates('naturaleza')
    def validate_naturaleza(self, key, value):
        if value.lower() not in self.NATURALEZAS_PERMITIDAS:
            raise ValueError(f"Invalid naturaleza. Must be one of: {', '.join(self.NATURALEZAS_PERMITIDAS)}")
        return value.lower()
    
    @db.validates('option')
    def validate_option(self, key, value):
        if value.lower() not in self.OPTIONS_PERMITIDAS:
            raise ValueError(f"Invalid option. Must be one of: {', '.join(self.OPTIONS_PERMITIDAS)}")
        return value.lower()
    
    @db.validates('codigo')
    def validate_codigo(self, key, value):
        if not value:
            raise ValueError("El código no puede estar vacío")
        if self.option == 'factura':
            if not re.match(r'^\d{5}-\d{8}$', value):
                raise ValueError("El código de factura debe tener el formato '#####-########'")
        elif self.option == 'boleta':
            if not value.isdigit():
                raise ValueError("El código de boleta debe ser numérico")
                
        return value

    @db.validates('metodo_de_pago')
    def validate_metodo_de_pago(self, key, value):
        if value.lower() not in self.METODOS_PAGO_PERMITIDOS:
            raise ValueError(f"Invalid metodo_de_pago. Must be one of: {', '.join(self.METODOS_PAGO_PERMITIDOS)}")
        return value.lower()

    def __repr__(self):
        return (f'<Operación: {self.id} - {self.fecha} - {self.tipo} - '
                f'{self.caracter} - {self.naturaleza} - Monto: {self.monto_total}>')

    def to_json(self):

        def get_filename(path):
            if not path:
                return None
            match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}_(.+)$', path)
            if match:
                return match.group(1)
            return path.split('/')[-1]

        operacion_json = {
            "id": self.id,
            "fecha": self.fecha.strftime("%Y-%m-%d"),
            "tipo": self.tipo,
            "caracter": self.caracter,
            "naturaleza": self.naturaleza,
            "persona": self.personas.to_json(),
            "comprobante": get_filename(self.comprobante_path),
            "option": self.option,
            "codigo": self.codigo,
            "observaciones": self.observaciones,
            "metodo_de_pago": self.metodo_de_pago,
            "monto_total": float(self.monto_total),
            "subcategoria":self.subcategoria.to_json(),
            "usuario": self.usuario.nombre,
            "archivo1": get_filename(self.archivo1_path),
            "archivo2": get_filename(self.archivo2_path),
            "archivo3": get_filename(self.archivo3_path),
            "modificado_por_otro": self.modificado_por_otro
        }
        return operacion_json


    def to_excel(self):
        operacion_json = {
            "id": self.id,
            "Fecha": self.fecha.strftime("%Y-%m-%d"),
            "Tipo": self.tipo,
            "Carácter": self.caracter,
            "Naturaleza": self.naturaleza,
            "Cuit": self.personas.cuit,
            "Razón social": self.personas.razon_social,
            "Tipo de comprobante": self.option,
            "Número de comprobante": self.codigo,
            "Observaciones": self.observaciones,
            "Método de pago": self.metodo_de_pago,
            "Monto": float(self.monto_total),
            "Concepto": self.subcategoria.categoria.concepto.nombre,
            "Categoría": self.subcategoria.categoria.nombre,
            "Subcategoría": self.subcategoria.nombre,
            "Usuario": self.usuario.nombre,
            "Modificado por otro": "Sí" if self.modificado_por_otro else "No"
        }
        return operacion_json
    
    @staticmethod
    def from_json(operacion_json):
        id=operacion_json.get("id"),
        fecha=datetime.strptime(operacion_json["fecha"], "%Y-%m-%d").date(),
        tipo=operacion_json.get("tipo"),
        caracter=operacion_json.get("caracter"),
        naturaleza=operacion_json.get("naturaleza"),
        id_persona=operacion_json.get("id_persona"),
        comprobante_path=operacion_json.get("comprobante_path"),
        comprobante_tipo=operacion_json.get("comprobante_tipo"),
        option=operacion_json.get("option"),
        codigo=operacion_json.get("codigo"),
        observaciones=operacion_json.get("observaciones"),
        metodo_de_pago=operacion_json.get("metodo_de_pago"),
        monto_total=operacion_json.get("monto_total"),
        id_subcategoria=operacion_json.get("id_subcategoria"),
        id_usuario=operacion_json.get("id_usuario"),
        archivo1_path=operacion_json.get("archivo1_path"),
        archivo1_tipo=operacion_json.get("archivo1_tipo"),
        archivo2_path=operacion_json.get("archivo2_path"),
        archivo2_tipo=operacion_json.get("archivo2_tipo"),
        archivo3_path=operacion_json.get("archivo3_path"),
        archivo3_tipo=operacion_json.get("archivo3_tipo"),
        modificado_por_otro=operacion_json.get("modificado_por_otro", False),
        return Operacion(
                    id = id,
                    fecha = fecha,
                    tipo = tipo,
                    caracter = caracter,
                    naturaleza = naturaleza,
                    id_persona = id_persona,
                    comprobante_path = comprobante_path,
                    comprobante_tipo = comprobante_tipo,
                    option = option,
                    codigo = codigo,
                    observaciones = observaciones,
                    metodo_de_pago = metodo_de_pago,
                    monto_total = monto_total,
                    id_subcategoria = id_subcategoria,
                    id_usuario = id_usuario,
                    archivo1_path = archivo1_path,
                    archivo1_tipo = archivo1_tipo,
                    archivo2_path = archivo2_path,
                    archivo2_tipo = archivo2_tipo,
                    archivo3_path = archivo3_path,
                    archivo3_tipo = archivo3_tipo,
                    modificado_por_otro = modificado_por_otro
                    )