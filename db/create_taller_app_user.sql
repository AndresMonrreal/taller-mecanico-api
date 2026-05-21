-- =============================================================
-- Crear usuario taller_app con privilegios mínimos
-- usando ROLES DE APLICACIÓN (no grants directos)
-- =============================================================
-- Ejecutar como SYS o ADMIN de la BD
-- =============================================================

-- 1. Crear rol de aplicación
CREATE ROLE taller_app_rol IDENTIFIED BY "TallerApp2026!";

-- 2. Privilegios básicos al rol
GRANT CONNECT TO taller_app_rol;
GRANT CREATE SESSION TO taller_app_rol;

-- 3. DML sobre tablas de negocio (sin DDL)
GRANT SELECT, INSERT, UPDATE, DELETE ON Clients TO taller_app_rol;
GRANT SELECT, INSERT, UPDATE, DELETE ON Vehicles TO taller_app_rol;
GRANT SELECT, INSERT, UPDATE, DELETE ON Orders TO taller_app_rol;
GRANT SELECT, INSERT, UPDATE, DELETE ON ServiceOrders TO taller_app_rol;
GRANT SELECT, INSERT, UPDATE, DELETE ON Service TO taller_app_rol;
GRANT SELECT, INSERT, UPDATE, DELETE ON Sessions TO taller_app_rol;
GRANT SELECT, INSERT, UPDATE, DELETE ON users TO taller_app_rol;
GRANT SELECT, INSERT, UPDATE, DELETE ON permisos_rol TO taller_app_rol;

-- 4. Ejecución de PL/SQL (sin modificación)
GRANT EXECUTE ON fn_tiene_permiso TO taller_app_rol;
GRANT EXECUTE ON fn_calcular_total_orden TO taller_app_rol;
GRANT EXECUTE ON sp_cerrar_orden TO taller_app_rol;
GRANT EXECUTE ON sp_transferir_servicio TO taller_app_rol;
GRANT EXECUTE ON sp_log_transferencia TO taller_app_rol;

-- 5. Consulta de vistas
GRANT SELECT ON vw_resumen_clientes TO taller_app_rol;
GRANT SELECT ON vw_ordenes_activas TO taller_app_rol;
GRANT SELECT ON vm_metricas_taller TO taller_app_rol;

-- 6. Crear usuario y asignarle el rol
CREATE USER taller_app IDENTIFIED BY "TallerApp2026!";
GRANT taller_app_rol TO taller_app;

-- 7. Cuota de almacenamiento
ALTER USER taller_app QUOTA 100M ON USERS;
