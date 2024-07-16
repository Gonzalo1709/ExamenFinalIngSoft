# Pregunta 2 (5 puntos)
Realizar 5 pruebas unitarias: 2 de caso de éxito y 3 de error. Incluir las pruebas unitarias en el
mismo repositorio Github.

Adicionar comentarios en cada prueba indicando el caso de prueba.
Las pruebas unitarias deben ser sobre los objetos y no sobre los “GET”.

- **El código es autoexplicativo en este aspecto, revisar los comentarios.**

# Pregunta 3 (5 puntos)
Se requiere realizar un cambio en el software para que soporte un valor máximo de 200 soles a transferir por día.
## ¿Qué cambiaría en el código (Clases / Métodos) - No realizar la implementación, sólo descripción.
### Cambios en clase "Cuenta"
  - Añadir campo "CantidadDiaria" float que será un diccionario de 366 elementos (de acuerdo al año), cuyo valor inicial será 200. Cada elemento por si mismo representará el monto disponible para cada día del año que le queda al usuario para poder transferir.
 
### Cambios en clase "Operación"
  - No serán necesarios cambios en nuestra implementación. Se mantiene igual.

### Cambios endpoint "BilleteraPagar"
 - Agregar un método "ChequeoCantidadDiaria" antes de realizar cada transferencia, donde de acuerdo al día se accederá a uno de los 366 elementos del diccionario "CantidadDiaria" en la clase "Cuenta" que representa el dinero disponible para transferencia en ese día, se comparará con el "Monto" de transferencia y si este monto de transferencia es menor o igual al dinero disponible en el día, se rechazará la transferencia, caso contrario se aceptará y se disminuirá el valor diario disponible respecto al monto transferido.

## ¿Qué casos de prueba nuevos serían necesarios?
  - **Caso de éxito 1:** Para una fecha en la que no se haya generado una transferencia, transferir un monto menor a 200 soles.
  - **Caso de éxito 2:** Generar múltiples transferencias en una fecha cuyo monto total sea menor a 200 soles.
  - **Caso de error 1:** Para una fecha en la que no se haya generado una transferencia, transferir un monto mayor a 200.
  - **Caso de error 2:** Generar múltiples transferencias en una fecha cuyo monto total sea mayor a 200 soles.

## ¿Los casos de prueba existentes garantizan que no se introduzcan errores en la funcionalidad existente?
  - Sí. Estamos suponiendo que anualmente se estará haciendo un mantenimiento de la base de datos en donde se reiniciarán los datos del diccionario "CantidadDiaria" de la clase "Cuenta" para todas las cuentas. Nuestras funcionalidades incluso garantizan un uso correcto en caso de año bisiesto. Al no intervenir las funcionalidades actuales con las preexistentes más que denegar transacciones exclusivamente en el caso de que se exceda el monto diario máximo en la misma fecha.
