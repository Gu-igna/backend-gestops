from .. import db
import re 

class Persona(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cuit = db.Column(db.Integer, nullable=False, unique=True)
    razon_social = db.Column(db.String(255), nullable=False)

    operaciones = db.relationship("Operacion", back_populates="personas")

    @db.validates('cuit')
    def validate_cuit(self, key, value):
        cuit_pattern = re.compile(r'^\d{11}$')
        if not cuit_pattern.match(str(value)):
            raise ValueError("Invalid CUIT format. It should be in the format 'XXXXXXXXXXX'.")
        return value
    
    def __repr__(self):
        return '<Persona: %r %r %r>'% (self.id, self.cuit, self.razon_social)
    
    def to_json(self):
        persona_json = {
            'id': self.id,
            'cuit': self.cuit,
            'razon_social': self.razon_social
        }
        return persona_json

    @staticmethod
    def from_json(persona_json):
        id = persona_json.get('id')
        cuit = persona_json.get('cuit')
        razon_social = persona_json.get('razon_social')
        return Persona(
                    id = id,
                    cuit = cuit,
                    razon_social = razon_social
                    )