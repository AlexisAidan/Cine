# Manual de Usuario - Sistema de Gestión de Cine

Bienvenido al manual de usuario del Sistema de Gestión de Cine. Este documento detalla todas las funcionalidades disponibles en la aplicación, organizadas por los menús principales: Archivo, Ventas, Catálogo, Gestión y Reportes.

## 1. Primeros Pasos

Para comenzar a utilizar el sistema y acceder a las funciones de lectura, ingreso, edición o eliminación de datos, es necesario establecer una conexión con la base de datos.

### Conexión al Sistema
1.  Haz clic en el menú **Archivo** ubicado en la barra superior de la ventana principal.
2.  Selecciona la opción **Conectar**.
3.  Si la conexión es exitosa, verás:
    *   Un mensaje en la barra de estado inferior indicando "Conectado a [Nombre del Servicio]".
    *   Una ventana emergente confirmando "Conectado a la base de datos".

---

## 2. Menú Archivo

Este menú gestiona la conexión con el sistema y la salida de la aplicación.

*   **Conectar**: Inicia la conexión con la base de datos Oracle. Es necesario realizar este paso antes de intentar cualquier otra operación.
*   **Desconectar**: Cierra la conexión activa con la base de datos.
*   **Salir**: Cierra la aplicación completamente.

---

## 3. Menú Ventas

En este menú se realizan las operaciones relacionadas con la venta de boletos y la visualización del historial de ventas.

### Vender Boleto
Esta opción abre una ventana para procesar una nueva venta.

**Requisitos previos:**
*   Deben existir **Clientes** registrados.
*   Deben existir **Empleados** registrados.
*   Deben existir **Funciones** programadas con fecha futura.
*   La sala de la función debe tener **Butacas** registradas.

**Pasos para vender un boleto:**
1.  **Cliente**: Selecciona el cliente que realiza la compra desde la lista desplegable (puedes escribir para buscar).
2.  **Empleado**: Selecciona el empleado que realiza la venta.
3.  **Función**: Selecciona la función deseada. La lista muestra el título de la película, la fecha/hora y el precio.
4.  **Butacas**:
    *   Al seleccionar una función, aparecerá la lista de butacas disponibles en el recuadro "Disponibles".
    *   Puedes usar el campo "Butacas" para filtrar por fila o número.
    *   Selecciona una o varias butacas de la lista (haz clic manteniendo presionada la tecla Ctrl para selección múltiple).
5.  **Monto**: Este campo se calcula automáticamente sumando el precio de las butacas seleccionadas.
6.  **Método de pago**: Elige el método de pago (efectivo, tarjeta de crédito, tarjeta de débito, transferencia).
7.  Haz clic en el botón **Vender** para finalizar la transacción.

### Ver Boletos
Esta opción muestra una tabla con el historial de todos los boletos vendidos.

*   **Columnas visibles**: ID Boleto, Fecha Compra, Precio, Película, Función Inicio, Sala, Butaca, Cliente, Empleado, ID Pago.
*   **Refrescar**: Actualiza la lista para ver las ventas más recientes.

---

## 4. Menú Catálogo

Este menú permite administrar los elementos fundamentales del cine: Películas, Funciones, Salas y Butacas.

### 4.1. Películas

#### Agregar Película
1.  Haz clic en el botón **Agregar**.
2.  Llena el formulario con los siguientes datos:
    *   **Título**: Nombre de la película (Obligatorio).
    *   **Sinopsis**: Breve descripción de la trama.
    *   **Duración (min)**: Duración en minutos (número entero).
    *   **Idioma**: Idioma o idiomas de la película.
    *   **Clasificación**: Clasificación (ej. A, B, C).
    *   **Fecha estreno**: Selecciona la fecha en el calendario desplegable.
3.  Haz clic en **Guardar**.

#### Editar Película
1.  Selecciona una película de la lista haciendo clic sobre ella.
2.  Haz clic en el botón **Editar**.
3.  Modifica los campos necesarios en el formulario (Título, Sinopsis, Duración, etc.) como se muestra en el apartado **Agregar Película**.
4.  Haz clic en **Guardar** para aplicar los cambios.

#### Eliminar Película
1.  Selecciona la película que deseas eliminar.
2.  Haz clic en el botón **Eliminar**.
3.  Confirma la acción en el mensaje emergente.

---

### 4.2. Funciones

#### Agregar Función
1.  Haz clic en el botón **Agregar**.
2.  Llena el formulario:
    *   **Hora inicio**: Fecha y hora de inicio de la función.
    *   **Hora fin**: Fecha y hora de finalización. *Nota: Debe ser posterior a la hora de inicio.*
    *   **Precio**: Costo del boleto para esta función.
    *   **ID Película**: ID numérico de la película a proyectar.
    *   **ID Sala**: ID numérico de la sala donde se proyectará.
3.  Haz clic en **Guardar**.

#### Editar Función
1.  Selecciona una función de la lista.
2.  Haz clic en el botón **Editar**.
3.  Modifica los horarios, precio o IDs de película/sala como se muestra en el apartado **Agregar Función**.
4.  Haz clic en **Guardar**.

#### Eliminar Función
1.  Selecciona la función a eliminar.
2.  Haz clic en el botón **Eliminar** y confirma.

---

### 4.3. Salas

#### Agregar Sala
1.  Haz clic en el botón **Agregar**.
2.  Llena el formulario:
    *   **Nombre**: Nombre o identificador de la sala (Obligatorio).
    *   **Descripción ubicación**: Detalles sobre dónde se encuentra la sala.
3.  Haz clic en **Guardar**.

#### Editar Sala
1.  Selecciona una sala de la lista.
2.  Haz clic en el botón **Editar**.
3.  Modifica el nombre o la descripción como se muestra en el apartado **Agregar Sala**.
4.  Haz clic en **Guardar**.

#### Eliminar Sala
1.  Selecciona la sala a eliminar.
2.  Haz clic en el botón **Eliminar** y confirma.

---

### 4.4. Butacas

**Requisitos previos:**
*   Debe existir la **Sala** a la que se asignará la butaca.
*   Es necesario conocer el ID de dicha sala.

#### Agregar Butaca
1.  Haz clic en el botón **Agregar**.
2.  Llena el formulario:
    *   **Fila**: Identificador de la fila (ej. A, B, 1, 2).
    *   **Número**: Número de la butaca en la fila (ej. 1, 2, 3).
    *   **Tipo**: Tipo de asiento (ej. normal, VIP, discapacitado).
    *   **ID Sala**: ID de la sala a la que pertenece.
3.  Haz clic en **Guardar**.

#### Editar Butaca
1.  Selecciona una butaca de la lista.
2.  Haz clic en el botón **Editar**.
3.  Modifica la fila, número, tipo o sala asignada como se muestra en el apartado **Agregar Butaca**.
4.  Haz clic en **Guardar**.

#### Eliminar Butaca
1.  Selecciona la butaca a eliminar.
2.  Haz clic en el botón **Eliminar** y confirma.

---

## 5. Menú Gestión

Este menú está destinado a la administración de personas (Clientes, Empleados) y la visualización de Pagos.

### 5.1. Clientes

#### Agregar Cliente
1.  Haz clic en el botón **Agregar**.
2.  Llena el formulario:
    *   **Nombre**: Nombre del cliente (Obligatorio).
    *   **Apellido**: Apellido del cliente (Obligatorio).
    *   **Correo**: Dirección de correo electrónico (Obligatorio).
    *   **Teléfono**: Número de contacto.
3.  Haz clic en **Guardar**.

#### Editar Cliente
1.  Selecciona un cliente de la lista.
2.  Haz clic en el botón **Editar**.
3.  Modifica los datos personales como se muestra en el apartado **Agregar Cliente**.
4.  Haz clic en **Guardar**.

#### Eliminar Cliente
1.  Selecciona el cliente a eliminar.
2.  Haz clic en el botón **Eliminar** y confirma.

---

### 5.2. Empleados

#### Agregar Empleado
1.  Haz clic en el botón **Agregar**.
2.  Llena el formulario:
    *   **Usuario**: Nombre de usuario para el sistema (Obligatorio).
    *   **Contraseña**: Clave de acceso (Obligatoria para nuevos empleados).
    *   **Nombre**: Nombre del empleado (Obligatorio).
    *   **Apellido**: Apellido del empleado.
    *   **Rol**: Cargo o función (ej. vendedor, gerente) (Obligatorio).
3.  Haz clic en **Guardar**.

#### Editar Empleado
1.  Selecciona un empleado de la lista.
2.  Haz clic en el botón **Editar**.
3.  Modifica los datos como se muestra en el apartado **Agregar Empleado**.
    *   *Nota: Si dejas el campo "Contraseña" vacío, se mantendrá la contraseña actual.*
4.  Haz clic en **Guardar**.

#### Eliminar Empleado
1.  Selecciona el empleado a eliminar.
2.  Haz clic en el botón **Eliminar** y confirma.

---

### 5.3. Pagos

Esta sección es de **solo lectura** y permite visualizar el historial de transacciones financieras.

*   **Visualización**: Muestra una tabla con ID Pago, Fecha, Monto, Método de Pago y Cliente asociado.
*   **Refrescar**: Actualiza la tabla para mostrar los últimos pagos registrados.

---

## 6. Menú Reportes

### Ventas del día
Esta opción genera un reporte rápido del total de ingresos del día actual.

1.  Haz clic en el menú **Reportes**.
2.  Selecciona **Ventas del día**.
3.  Aparecerá una ventana emergente mostrando el **Total vendido hoy** (suma de los montos de los pagos registrados con fecha de hoy).
