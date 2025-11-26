-- Generado por Oracle SQL Developer Data Modeler 24.3.1.351.0831
--   en:        2025-10-25 12:55:09 CST
--   sitio:      Oracle Database 21c
--   tipo:      Oracle Database 21c



-- predefined type, no DDL - MDSYS.SDO_GEOMETRY

-- predefined type, no DDL - XMLTYPE

CREATE SEQUENCE seq_boleto 
    START WITH 1 
    INCREMENT BY 1 
;

CREATE SEQUENCE seq_butaca 
    START WITH 1 
    INCREMENT BY 1 
;

CREATE SEQUENCE seq_cliente 
    START WITH 1 
    INCREMENT BY 1 
;

CREATE SEQUENCE seq_empleado 
    START WITH 1 
    INCREMENT BY 1 
;

CREATE SEQUENCE seq_funcion 
    START WITH 1 
    INCREMENT BY 1 
;

CREATE SEQUENCE seq_pago 
    START WITH 1 
    INCREMENT BY 1 
;

CREATE SEQUENCE seq_pelicula 
    START WITH 1 
    INCREMENT BY 1 
;

CREATE SEQUENCE seq_sala 
    START WITH 1 
    INCREMENT BY 1 
;

CREATE TABLE Boleto 
    ( 
     id_boleto     NUMBER (6)  NOT NULL , 
     id_butaca     NUMBER (10)  NOT NULL , 
     id_funcion    NUMBER (10)  NOT NULL , 
     id_empleado   NUMBER (10)  NOT NULL , 
     id_pago       NUMBER (10)  NOT NULL , 
     fecha_compra  TIMESTAMP WITH LOCAL TIME ZONE  NOT NULL , 
     precio_pagado NUMBER (10,2)  NOT NULL 
    ) 
    LOGGING 
;

ALTER TABLE Boleto 
    ADD CONSTRAINT Boleto_Precio_CHK 
    CHECK (precio_pagado > 0) 
;

COMMENT ON TABLE Boleto IS 'Boletos vendidos a los clientes'
;

COMMENT ON COLUMN Boleto.precio_pagado IS 'Precio al momento de la compra (puede diferir del precio actual)' 
;

ALTER TABLE Boleto 
    ADD CONSTRAINT Boleto_PK PRIMARY KEY ( id_boleto ) ;

CREATE TABLE Butaca 
    ( 
     id_butaca     NUMBER (10)  NOT NULL , 
     fila          VARCHAR2 (10) , 
     numero_butaca NUMBER (3) , 
     tipo_butaca   VARCHAR2 (20) , 
     id_sala       NUMBER (6)  NOT NULL 
    ) 
    LOGGING 
;

COMMENT ON TABLE Butaca IS 'Butacas disponibles en cada sala'
;

COMMENT ON COLUMN Butaca.tipo_butaca IS 'Ejemplos: normal, VIP, discapacitado' 
;

ALTER TABLE Butaca 
    ADD CONSTRAINT Butaca_PK PRIMARY KEY ( id_butaca ) ;

ALTER TABLE Butaca 
    ADD CONSTRAINT Butaca_id_sala_fila_numero_butaca_UN UNIQUE ( id_sala , fila , numero_butaca ) ;

CREATE TABLE Cliente 
    ( 
     id_cliente NUMBER (12)  NOT NULL , 
     nombre     VARCHAR2 (100 CHAR)  NOT NULL , 
     apellido   VARCHAR2 (100)  NOT NULL , 
     correo     VARCHAR2 (200 CHAR)  NOT NULL , 
     telefono   VARCHAR2 (50 BYTE) 
    ) 
    LOGGING 
;

COMMENT ON TABLE Cliente IS 'Registro de clientes del cine'
;

ALTER TABLE Cliente 
    ADD CONSTRAINT Cliente_PK PRIMARY KEY ( id_cliente ) ;

ALTER TABLE Cliente 
    ADD CONSTRAINT Cliente_correo_UN UNIQUE ( correo ) ;

CREATE TABLE Empleado 
    ( 
     id_empleado NUMBER (10)  NOT NULL , 
     usuario     VARCHAR2 (80 CHAR)  NOT NULL , 
     contrasena  VARCHAR2 (255 CHAR)  NOT NULL , 
     nombre      VARCHAR2 (100 CHAR)  NOT NULL , 
     apellido    VARCHAR2 (100 CHAR)  NOT NULL , 
     rol         VARCHAR2 (50 CHAR)  NOT NULL 
    ) 
    LOGGING 
;

COMMENT ON TABLE Empleado IS 'Personal que trabaja en el cine'
;

COMMENT ON COLUMN Empleado.contrasena IS 'IMPORTANTE: Almacenar como hash (bcrypt, SHA-256), NUNCA texto plano' 
;

COMMENT ON COLUMN Empleado.rol IS 'Ejemplos: vendedor, gerente, admin, operador' 
;

ALTER TABLE Empleado 
    ADD CONSTRAINT Empleado_PK PRIMARY KEY ( id_empleado ) ;

ALTER TABLE Empleado 
    ADD CONSTRAINT Empleado_usuario_UN UNIQUE ( usuario ) ;

CREATE TABLE Funcion 
    ( 
     id_funcion  NUMBER (10)  NOT NULL , 
     hora_inicio TIMESTAMP WITH LOCAL TIME ZONE  NOT NULL , 
     hora_fin    TIMESTAMP WITH LOCAL TIME ZONE  NOT NULL , 
     precio      NUMBER (10,2)  NOT NULL , 
     id_pelicula NUMBER (10)  NOT NULL , 
     id_sala     NUMBER (6)  NOT NULL 
    ) 
    LOGGING 
;

ALTER TABLE Funcion 
    ADD CONSTRAINT Funcion_Precio_CHK 
    CHECK (precio > 0) 
;

COMMENT ON TABLE Funcion IS 'Horarios de proyección de películas'
;

ALTER TABLE Funcion 
    ADD CONSTRAINT Funcion_PK PRIMARY KEY ( id_funcion ) ;

CREATE TABLE Pago 
    ( 
     id_pago     NUMBER (10)  NOT NULL , 
     fecha_pago  TIMESTAMP WITH LOCAL TIME ZONE  NOT NULL , 
     monto       NUMBER (10,2)  NOT NULL , 
     metodo_pago VARCHAR2 (50 CHAR)  NOT NULL , 
     id_cliente  NUMBER (12)  NOT NULL 
    ) 
    LOGGING 
;

ALTER TABLE Pago 
    ADD CONSTRAINT Pago_Monto_CHK 
    CHECK (monto > 0) 
;

COMMENT ON TABLE Pago IS 'Registro de pagos realizados por clientes'
;

COMMENT ON COLUMN Pago.metodo_pago IS 'Ejemplos: efectivo, tarjeta_credito, tarjeta_debito, transferencia' 
;
CREATE INDEX Pago_Cliente_Fecha_IDX ON Pago 
    ( 
     id_cliente ASC , 
     fecha_pago ASC 
    ) 
;

ALTER TABLE Pago 
    ADD CONSTRAINT Pago_PK PRIMARY KEY ( id_pago ) ;

CREATE TABLE Pelicula 
    ( 
     id_pelicula   NUMBER (10)  NOT NULL , 
     titulo        VARCHAR2 (200 CHAR)  NOT NULL , 
     sinopsis      VARCHAR2 (500 CHAR) , 
     duracion_min  NUMBER (3)  NOT NULL , 
     idioma        VARCHAR2 (50 CHAR) , 
     clasificacion VARCHAR2 (10 CHAR) , 
     fecha_estreno DATE 
    ) 
    LOGGING 
;

ALTER TABLE Pelicula 
    ADD CONSTRAINT Pelicula_Duracion_CHK 
    CHECK (duracion_min BETWEEN 1 AND 999) 
;

COMMENT ON TABLE Pelicula IS 'Catálogo de películas disponibles en el cine'
;

COMMENT ON COLUMN Pelicula.duracion_min IS 'Duración en minutos (sin decimales)' 
;

ALTER TABLE Pelicula 
    ADD CONSTRAINT Pelicula_PK PRIMARY KEY ( id_pelicula ) ;

CREATE TABLE Sala 
    ( 
     id_sala               NUMBER (6)  NOT NULL , 
     nombre                VARCHAR2 (100 CHAR)  NOT NULL , 
     descripcion_ubicacion VARCHAR2 (200 CHAR) 
    ) 
    LOGGING 
;

COMMENT ON TABLE Sala IS 'Salas de proyección del cine'
;

ALTER TABLE Sala 
    ADD CONSTRAINT Sala_PK PRIMARY KEY ( id_sala ) ;

ALTER TABLE Boleto 
    ADD CONSTRAINT Boleto_Butaca_FK FOREIGN KEY 
    ( 
     id_butaca
    ) 
    REFERENCES Butaca 
    ( 
     id_butaca
    ) 
    NOT DEFERRABLE 
;

ALTER TABLE Boleto 
    ADD CONSTRAINT Boleto_Empleado_FK FOREIGN KEY 
    ( 
     id_empleado
    ) 
    REFERENCES Empleado 
    ( 
     id_empleado
    ) 
    NOT DEFERRABLE 
;

ALTER TABLE Boleto 
    ADD CONSTRAINT Boleto_Funcion_FK FOREIGN KEY 
    ( 
     id_funcion
    ) 
    REFERENCES Funcion 
    ( 
     id_funcion
    ) 
    NOT DEFERRABLE 
;

ALTER TABLE Boleto 
    ADD CONSTRAINT Boleto_Pago_FK FOREIGN KEY 
    ( 
     id_pago
    ) 
    REFERENCES Pago 
    ( 
     id_pago
    ) 
    NOT DEFERRABLE 
;

ALTER TABLE Butaca 
    ADD CONSTRAINT Butaca_Sala_FK FOREIGN KEY 
    ( 
     id_sala
    ) 
    REFERENCES Sala 
    ( 
     id_sala
    ) 
    NOT DEFERRABLE 
;

ALTER TABLE Funcion 
    ADD CONSTRAINT Funcion_Pelicula_FK FOREIGN KEY 
    ( 
     id_pelicula
    ) 
    REFERENCES Pelicula 
    ( 
     id_pelicula
    ) 
    NOT DEFERRABLE 
;

ALTER TABLE Funcion 
    ADD CONSTRAINT Funcion_Sala_FK FOREIGN KEY 
    ( 
     id_sala
    ) 
    REFERENCES Sala 
    ( 
     id_sala
    ) 
    NOT DEFERRABLE 
;

ALTER TABLE Pago 
    ADD CONSTRAINT Pago_Cliente_FK FOREIGN KEY 
    ( 
     id_cliente
    ) 
    REFERENCES Cliente 
    ( 
     id_cliente
    ) 
    NOT DEFERRABLE 
;

CREATE OR REPLACE TRIGGER trg_pago_id 
BEFORE INSERT ON Pago 
FOR EACH ROW 
WHEN (NEW.id_pago IS NULL) 
BEGIN 
    :NEW.id_pago := seq_pago.NEXTVAL; 
END;
/

-- Trigger para autogenerar el ID de Cliente si no se proporciona
CREATE OR REPLACE TRIGGER trg_cliente_id
BEFORE INSERT ON Cliente
FOR EACH ROW
WHEN (NEW.id_cliente IS NULL)
BEGIN
    :NEW.id_cliente := seq_cliente.NEXTVAL;
END;
/