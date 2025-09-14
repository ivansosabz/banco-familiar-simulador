# Banco Familiar Simulador 🏦

Simulación de plataforma bancaria con Django y Bootstrap.  
Incluye módulos de clientes, cuentas, transacciones, auditoría y seguridad.

---

## 📝 Descripción

Este proyecto simula una plataforma bancaria inspirada en el Banco Familiar Paraguay.  
Permite gestionar clientes, cuentas digitales, préstamos y operaciones básicas,  
con un fuerte enfoque en **seguridad**, **encriptación** y **pistas de auditoría**.

---

## ⚙️ Tecnologías

- **Backend**: Django 5.x
- **Frontend**: Django Templates + Bootstrap 5
- **Formularios**: Django Crispy Forms (bootstrap5)
- **APIs**: Django REST Framework (opcional / futuro)
- **Base de datos**: SQLite (desarrollo) — Migrable a PostgreSQL
- **Control de versiones**: Git + GitHub

---

## 🚀 Instalación y Uso

1. Clonar el repositorio:
    ```bash
    git clone https://github.com/ivansosabz/banco-familiar-simulador.git
    cd banco-familiar-simulador
    ```

2. Crear entorno virtual e instalar dependencias:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate en Windows
    pip install -r requirements.txt
    ```

3. Migrar la base de datos:
    ```bash
    python manage.py migrate
    ```

4. Crear superusuario:
    ```bash
    python manage.py createsuperuser
    ```

5. Iniciar el servidor:
    ```bash
    python manage.py runserver
    ```

---

## 🛠️ Guía de Trabajo

- **Etapa 1**: Configuración inicial (apps `core` y `audits` + templates)
- **Etapa 2**: Autenticación (login, logout, roles admin/cliente)
- **Etapa 3**: Módulo de clientes y cuentas (CRUD)
- **Etapa 4**: Transacciones y préstamos (simulación)
- **Etapa 5**: Auditoría (bitácoras y logs)
- **Etapa 6**: Seguridad y encriptación (contraseñas, datos sensibles)
- **Etapa 7**: Estilizar con Bootstrap y Crispy Forms
- **Etapa 8**: Opcional: API REST para clientes móviles

---

## 🔒 Seguridad y Auditoría

- Uso de Django Authentication y permisos por roles.
- Encriptación de contraseñas y datos sensibles.
- Pistas de auditoría mediante la app `audits`.
- Bitácoras de transacciones con información completa.

---

## 📌 Licencia

Proyecto de aprendizaje con fines educativos.


