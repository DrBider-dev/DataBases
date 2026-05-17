<div align="center">

# 🏨 Sistema de Gestión Hotelera — Base de Datos

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-DDL%20%7C%20DML%20%7C%20DCL-orange?style=for-the-badge&logo=databricks&logoColor=white)
![Estado](https://img.shields.io/badge/Estado-En%20Desarrollo-yellow?style=for-the-badge)
![Universidad](https://img.shields.io/badge/Universidad-UDFJC-green?style=for-the-badge&logo=academia&logoColor=white)

**Proyecto Universitario · Ingeniería de Sistemas · Bases de Datos**

</div>

---

## 📑 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Equipo de Desarrollo](#-equipo-de-desarrollo)
- [Estructura del Repositorio](#-estructura-del-repositorio)
- [Instrucciones de Despliegue](#-instrucciones-de-despliegue)

---

## 📋 Descripción General

Este repositorio contiene el diseño e implementación completa de una **Base de Datos Relacional** para la gestión integral de las operaciones de un hotel, desarrollado como proyecto académico de la asignatura de **Bases de Datos**.

El sistema modela todos los procesos operativos críticos de un hotel moderno: registro de huéspedes, administración de habitaciones, control de reservas, gestión de personal, oferta de servicios y registro detallado de consumos. Se implementa con un esquema relacional normalizado, control de acceso basado en roles (RBAC) y políticas de integridad referencial estrictas.

---

## 👥 Equipo de Desarrollo

| # | Nombre Completo                           | Código Estudiantil |
|:-:|---|:-:|
| 1 | **Santiago Zamudio Díaz**                 | `20231020128` |
| 2 | **Julian Ernesto Romero Gutiérrez**       | `20231020164` |
| 3 | **Brayan Estiven Aguirre Aristizábal**    | `20231020156` |

---

## 📁 Estructura del Repositorio

```bash
hotel-db/
│
├── 📂 design/                         # Modelos y diagramas de datos
│   ├── diagramaE-R.png                # Diagrama E-R completo
│   └── modelo_relacional.png          # Diagrama del modelo relacional
│
├── 📂 documentation/                  # Documentación técnica del proyecto
│   ├── diccionario_de_datos.docx       # Descripción de tablas, columnas y tipos
│   └── informe_proyecto.docx           # Informe académico completo
│
├── 📂 scripts/                        # Scripts SQL organizados por fase
│   ├── 01_creacion_tablas.sql         # DDL: esquemas, tablas, vistas, constraints
│   ├── 02_roles_permisos.sql          # DCL: creación de roles y asignación de permisos
│   └── 03_carga_datos.sql             # DML: datos de prueba (INSERT statements)
│
├── 📂 data/                           # Archivos de datos de carga
│   ├── clientes.csv
│   ├── habitaciones.csv
│   ├── reservas.csv
│   ├── empleados.csv
│   ├── servicios.csv
│   └── consumos.csv
│
├── 📂 src/                            # Código fuente de la aplicación (si aplica)
│   └── app/                           # Interfaz o scripts de aplicación
│
├── 📂 demo/                           # Recursos del video demostrativo
│   └── README_demo.md                 # Descripción del video y operaciones CRUD
│
└── README.md                          # Este archivo
```

---

## 🚀 Instrucciones de Despliegue

### Prerequisitos

- PostgreSQL instalado y en ejecución.
- Cliente `psql` disponible en el `PATH` del sistema.
- Usuario con permisos `SUPERUSER` o `CREATEDB` para el despliegue inicial.

### Pasos de Instalación

**1. Clonar el repositorio**
```bash
git clone https://github.com/DrBider-dev/DataBases.git
cd DataBases
```

**2. Ejecutar el script de creación de tablas**
```bash
psql -U postgres -f scripts/01_creacion_tablas.sql
```

**3. Crear roles y asignar permisos**
```bash
psql -U postgres -d hotel_db -f scripts/02_roles_permisos.sql
```

**4. Cargar datos de prueba**
```bash
psql -U postgres -d hotel_db -f scripts/03_carga_datos.sql
```

**5. Verificar la instalación**
```sql
-- Conectarse a la base de datos
\c hotel_db

-- Listar tablas creadas
\dt hotel.*

-- Listar roles creados
\du
```

---

<div align="center">

---

*Proyecto académico desarrollado para la asignatura de Bases de Datos.*  
*Universidad Distrital Francisco José de Caldas — 2026*

</div>