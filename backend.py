from dataclasses import dataclass
from flask import request, jsonify, request, Flask
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@dataclass
class Operacion(db.Model):
    __tablename__ = 'operaciones'
    id = db.Column(db.Integer, primary_key=True)
    CuentaOrigen = db.Column(db.String, db.ForeignKey('cuenta_usuario.Numero'), nullable=False)
    CuentaDestino = db.Column(db.String, db.ForeignKey('cuenta_usuario.Numero'), nullable=False)
    Monto = db.Column(db.Float, nullable=False)
    Fecha = db.Column(db.DateTime, nullable=False)

    def __init__(self, CuentaOrigen, CuentaDestino, Monto, Fecha):
        self.CuentaOrigen = CuentaOrigen
        self.CuentaDestino = CuentaDestino
        self.Monto = Monto
        self.Fecha = Fecha

    def __repr__(self):
        return f'Operacion: {self.CuentaOrigen} -> {self.CuentaDestino} Monto: {self.Monto} Fecha: {self.Fecha}'

@dataclass
class CuentaUsuario(db.Model):
    __tablename__ = 'cuenta_usuario'
    Numero = db.Column(db.String, primary_key=True)
    Saldo = db.Column(db.Float)
    NumerosContacto = db.Column(db.JSON)
    historialOperaciones = db.relationship('Operacion', foreign_keys=[Operacion.CuentaOrigen, Operacion.CuentaDestino], backref='cuenta_usuario', lazy=True)

    def transferir(self, cuentaDestino, monto):
        if self.Saldo < monto:
            return "Saldo insuficiente"
        self.Saldo -= monto
        cuentaDestino.Saldo += monto
        operacion = Operacion(NumeroOrigen=self.Numero, NumeroDestino=cuentaDestino.Numero, Monto=monto, Fecha=datetime.now())
        db.session.add(operacion)
        db.session.commit()
        return "Transferencia exitosa"
    
    def __repr__(self):
        return f'Cuenta: {self.Numero} Saldo: {self.Saldo} Contactos: {self.NumerosContacto}'
    
with app.app_context():
    db.create_all()
    
# Endpoint /billetera/contactos?minumero
@app.route('/billetera/contactos', methods=['GET'])
def get_contactos():
    numero = request.args.get('minumero')
    cuenta = CuentaUsuario.query.filter_by(Numero=numero).first()
    if cuenta is None:
        return "Cuenta no encontrada"
    return jsonify(cuenta.NumerosContacto)

# Endpoint /billetera/pagar?minumero&numerodestino&valor
@app.route('/billetera/pagar', methods=['POST'])
def pagar():
    data = request.json
    cuentaOrigen = CuentaUsuario.query.filter_by(Numero=data['minumero']).first()
    cuentaDestino = CuentaUsuario.query.filter_by(Numero=data['numerodestino']).first()
    if cuentaOrigen is None or cuentaDestino is None:
        return "Cuenta no encontrada"
    return cuentaOrigen.transferir(cuentaDestino, data['valor'])

# Endpoint /billetera/historial?minumero
@app.route('/billetera/historial', methods=['GET'])
def get_historial():
    numero = request.args.get('minumero')
    cuenta = CuentaUsuario.query.filter_by(Numero=numero).first()
    if cuenta is None:
        return "Cuenta no encontrada"
    return jsonify([str(operacion) for operacion in cuenta.historialOperaciones])

if __name__ == '__main__':
    app.run(debug=True)
    cuenta1 = CuentaUsuario(Numero='123', Saldo=100, NumerosContacto={'456': 'Juan'}, historialOperaciones=[])
    cuenta2 = CuentaUsuario(Numero='456', Saldo=100, NumerosContacto={'123': 'Pedro'}, historialOperaciones=[])
    db.session.add(cuenta1)
    db.session.add(cuenta2)
    db.session.commit()
