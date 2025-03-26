from .. import db

class Concepto(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String, nullable=False, unique=True)
    
    categorias = db.relationship("Categoria", back_populates="concepto")


    def __repr__(self):
        return '<Concepto: %r %r>'% (self.id, self.nombre)
    
    def to_json(self):
        concepto_json = {
            'id': self.id,
            'nombre': self.nombre,
        }
        return concepto_json

    @staticmethod
    def from_json(concepto_json):
        id = concepto_json.get('id')
        nombre = concepto_json.get('nombre')
        return Concepto(
                    id=id,
                    nombre=nombre,
                    )