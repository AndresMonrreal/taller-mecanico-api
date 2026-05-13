-- Crear usuario taller_app con privilegios mínimos
-- Ejecutar como SYS o ADMIN de la BD

CREATE USER taller_app IDENTIFIED BY "TallerApp2026!";

GRANT CONNECT TO taller_app;
GRANT CREATE SESSION TO taller_app;

-- Privilegios DML sobre tablas
GRANT SELECT, INSERT, UPDATE, DELETE ON Clients TO taller_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON Vehicles TO taller_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON Orders TO taller_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ServiceOrders TO taller_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON Service TO taller_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON Sessions TO taller_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON users TO taller_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON permisos_rol TO taller_app;

-- Ejecución de funciones y procedimientos
GRANT EXECUTE ON fn_tiene_permiso TO taller_app;
GRANT EXECUTE ON fn_calcular_total_orden TO taller_app;
GRANT EXECUTE ON sp_cerrar_orden TO taller_app;

-- Vistas
GRANT SELECT ON vw_resumen_clientes TO taller_app;
GRANT SELECT ON vw_ordenes_activas TO taller_app;
GRANT SELECT ON vm_metricas_taller TO taller_app;

-- Cuota de almacenamiento
ALTER USER taller_app QUOTA 100M ON USERS;
