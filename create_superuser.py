# create_superuser.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banco.settings')
django.setup()

from users.models import SystemUser, Role

# Crear rol de administrador si no existe
admin_role, created = Role.objects.get_or_create(
    nombre=Role.RoleType.ADMINISTRADOR,
    defaults={'descripcion': 'Administrador del sistema con acceso completo'}
)

if created:
    print("✓ Rol de administrador creado")
else:
    print("✓ Rol de administrador ya existía")

# Verificar si el usuario admin ya existe
if SystemUser.objects.filter(username='admin').exists():
    print("✗ El usuario 'admin' ya existe")
    print("\nSi quieres eliminarlo y crear uno nuevo, ejecuta:")
    print("python manage.py shell")
    print(">>> from users.models import SystemUser")
    print(">>> SystemUser.objects.filter(username='admin').delete()")
    print(">>> exit()")
else:
    # Crear superusuario
    try:
        admin = SystemUser.objects.create_superuser(
            username='admin',
            password='Admin123!'
        )
        print(f"✓ Superusuario creado: {admin.username}")
        print(f"✓ Rol: {admin.role.get_nombre_display()}")
        print(f"✓ Estado: {admin.get_estado_display()}")
        print("\nPuedes hacer login en /admin/ con:")
        print("Username: admin")
        print("Password: Admin123!")
    except Exception as e:
        print(f"✗ Error: {e}")