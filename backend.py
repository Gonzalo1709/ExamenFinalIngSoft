from dataclasses import dataclass
from flask import request, jsonify, request, Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime

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
    # Separate relationships for clarity and to resolve ambiguity
    operacionesEnviadas = db.relationship('Operacion',
                                          foreign_keys='Operacion.CuentaOrigen',
                                          backref=db.backref('cuentaOrigen', lazy=True),
                                          lazy='dynamic')
    operacionesRecibidas = db.relationship('Operacion',
                                           foreign_keys='Operacion.CuentaDestino',
                                           backref=db.backref('cuentaDestino', lazy=True),
                                           lazy='dynamic')

    def transferir(self, cuentaDestino, monto):
        if self.Saldo < monto:
            return "Saldo insuficiente"
        self.Saldo -= monto
        cuentaDestino.Saldo += monto
        operacion = Operacion(CuentaOrigen=self.Numero, CuentaDestino=cuentaDestino.Numero, Monto=monto, Fecha=datetime.now())
        db.session.add(operacion)
        db.session.commit()
        return "Transferencia exitosa"
    
    def historialOperaciones(self):
        return self.operacionesEnviadas.all() + self.operacionesRecibidas.all()
    
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

# Endpoint /billetera/pagar
# Params: minumero, numerodestino, valor
@app.route('/billetera/pagar', methods=['POST'])
def pagar():
    data = request.json
    cuentaOrigen = CuentaUsuario.query.filter_by(Numero=data['minumero']).first()
    cuentaDestino = CuentaUsuario.query.filter_by(Numero=data['numerodestino']).first()
    if cuentaOrigen is None or cuentaDestino is None:
        return "Cuenta no encontrada"
    return cuentaOrigen.transferir(cuentaDestino, data['valor'])

# Endpoint /billetera/historial?minumero
# Params: minumero
@app.route('/billetera/historial', methods=['GET'])
def get_historial():
    numero = request.args.get('minumero')
    cuenta = CuentaUsuario.query.filter_by(Numero=numero).first()
    if cuenta is None:
        return "Cuenta no encontrada"
    return jsonify([str(operacion) for operacion in cuenta.historialOperaciones()])

# Endpoint /billetera/saldo?minumero GET
# Params: minumero
@app.route('/billetera/saldo', methods=['GET'])
def get_saldo():
    numero = request.args.get('minumero')
    cuenta = CuentaUsuario.query.filter_by(Numero=numero).first()
    if cuenta is None:
        return "Cuenta no encontrada"
    return jsonify(cuenta.Saldo)

# Endpoint /billetera/crear POST
# Body: {numero: string}
@app.route('/billetera/crear', methods=['POST'])
def crear_cuenta():
    data = request.json
    cuenta = CuentaUsuario(Numero=data['numero'], Saldo=0, NumerosContacto={})
    db.session.add(cuenta)
    db.session.commit()
    return "Cuenta creada"

# Endpoint /billetera/agregarContacto POST
# Body: {minumero: string, numerodestino: string, nombre: string}
@app.route('/billetera/agregarContacto', methods=['POST'])
def agregar_contacto():
    data = request.json
    cuenta = CuentaUsuario.query.filter_by(Numero=data['minumero']).first()
    if cuenta is None:
        return "Cuenta no encontrada", 404
    if 'NumerosContacto' not in cuenta.__dict__ or not isinstance(cuenta.NumerosContacto, dict):
        cuenta.NumerosContacto = {}  
    cuenta.NumerosContacto[data['numerodestino']] = data['nombre']
    flag_modified(cuenta, 'NumerosContacto')  
    db.session.commit()
    return "Contacto agregado", 200

# Endpoint /billetera/admin/agregarSaldo POST
# Body: {minumero: string, valor: float}
@app.route('/billetera/admin/agregarSaldo', methods=['POST'])
def agregar_saldo():
    data = request.json
    cuenta = CuentaUsuario.query.filter_by(Numero=data['minumero']).first()
    if cuenta is None:
        return "Cuenta no encontrada", 404
    cuenta.Saldo += data['valor']
    db.session.commit()
    return "Saldo agregado", 200

if __name__ == '__main__':
    app.run(debug=True)
    cuenta1 = CuentaUsuario(Numero='123', Saldo=100, NumerosContacto={'456': 'Juan'}, historialOperaciones=[])
    cuenta2 = CuentaUsuario(Numero='456', Saldo=100, NumerosContacto={'123': 'Pedro'}, historialOperaciones=[])
