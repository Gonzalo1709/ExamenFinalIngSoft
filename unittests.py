import requests

ip = 'http://127.0.0.1:5000'
def unitTest1():
    # Test para probar una transferencia en la cual la cuenta no tiene saldo suficiente
    # Necesitamos crear las cuentas 
    requests.post(ip + '/billetera/crear', json={'numero': '123'})
    requests.post(ip + '/billetera/crear', json={'numero': '456'})
    # Agregamos un saldo a la cuenta 1
    requests.post(ip + '/billetera/admin/agregarSaldo', json={'minumero': '123', 'valor': 100})
    # Intentamos transferir un monto mayor al saldo
    response = requests.post(ip + '/billetera/pagar', json={'minumero': '123', 'numerodestino': '456', 'valor': 200})
    assert response.text == 'Saldo insuficiente'
    print('Test 1 passed')

def unitTest2():
    # Test para probar una transferencia exitosa
    # Necesitamos crear las cuentas
    requests.post(ip + '/billetera/crear', json={'numero': '111'})
    requests.post(ip + '/billetera/crear', json={'numero': '222'})
    # Agregamos un saldo a la cuenta 1
    requests.post(ip + '/billetera/admin/agregarSaldo', json={'minumero': '111', 'valor': 100})
    # Transferimos un monto menor al saldo
    response = requests.post(ip + '/billetera/pagar', json={'minumero': '111', 'numerodestino': '222', 'valor': 50})
    assert response.text == 'Transferencia exitosa'
    print('Test 2 passed')

def unitTest3():
    # Test para probar comprobar los contactos de una cuenta que no existe
    response = requests.get(ip + '/billetera/contactos?minumero=333')
    assert response.text == 'Cuenta no encontrada'
    print('Test 3 passed')

def unitTest4():
    # Test para ver el historial de operaciones de una cuenta
    # Necesitamos crear las cuentas
    requests.post(ip + '/billetera/crear', json={'numero': '444'})
    requests.post(ip + '/billetera/crear', json={'numero': '555'})
    # Agregamos un saldo a la cuenta 1
    requests.post(ip + '/billetera/admin/agregarSaldo', json={'minumero': '444', 'valor': 100})
    # Transferimos un monto menor al saldo
    requests.post(ip + '/billetera/pagar', json={'minumero': '444', 'numerodestino': '555', 'valor': 50})
    # Transeferimos un monto de vuelta menor al saldo
    requests.post(ip + '/billetera/pagar', json={'minumero': '555', 'numerodestino': '444', 'valor': 25})
    response = requests.get(ip + '/billetera/historial?minumero=444')
    assert len(response.json()) == 2
    print('Test 4 passed')

def unitTest5():
    # Test para probar ver el historial de operaciones de una cuenta que no existe
    response = requests.get(ip + '/billetera/historial?minumero=777')
    assert response.text == 'Cuenta no encontrada'
    print('Test 5 passed')

unitTest1()
unitTest2()
unitTest3()
unitTest4()
unitTest5()
print('All tests passed')