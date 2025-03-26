from .. import db

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String, nullable=False)

    id_concepto = db.Column(db.Integer, db.ForeignKey("concepto.id"), nullable=False) 
    concepto = db.relationship("Concepto", back_populates="categorias", uselist=False, single_parent=True)

    subcategorias = db.relationship("Subcategoria", back_populates="categoria")

    def __repr__(self):
        return '<Categoria: %r %r %r>'% (self.id, self.nombre, self.id_concepto)
    
    def to_json(self):
        categoria_json = {
            'id': self.id,
            'nombre': self.nombre,
            'concepto': self.concepto.to_json()
        }
        return categoria_json

    @staticmethod
    def from_json(categoria_json):
        id = categoria_json.get('id')
        nombre = categoria_json.get('nombre')
        id_concepto = categoria_json.get('id_concepto')
        return Categoria(
                    id=id,
                    nombre=nombre,
                    id_concepto=id_concepto
                    )