from .. import db

class Subcategoria(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String, nullable=False)

    id_categoria = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False)
    categoria = db.relationship("Categoria", back_populates="subcategorias")

    operaciones = db.relationship("Operacion", back_populates="subcategoria")
    
    def __repr__(self):
        return '<Subcategoria: %r %r %r>' % (self.id, self.nombre, self.id_categoria)
    
    def to_json(self):
        subcategoria_json = {
            'id': self.id,
            'nombre': self.nombre,
            'categoria': self.categoria.to_json()
        }
        return subcategoria_json

    @staticmethod
    def from_json(subcategoria_json):
        id = subcategoria_json.get('id')
        nombre = subcategoria_json.get('nombre')
        id_categoria = subcategoria_json.get('id_categoria')
        return Subcategoria(
            id=id,
            nombre=nombre,
            id_categoria=id_categoria
        )
