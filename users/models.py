import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class Role(models.Model):
    """
    Modelo de Roles del sistema
    """

    class RoleType(models.TextChoices):
        ADMINISTRADOR = 'administrador', 'Administrador'
        CAJERO = 'cajero', 'Cajero'
        EJECUTIVO_CUENTAS = 'ejecutivo_cuentas', 'Ejecutivo de Cuentas'
        AUDITOR = 'auditor', 'Auditor'
        CLIENTE = 'cliente', 'Cliente'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(
        max_length=50,
        choices=RoleType.choices,
        unique=True,
        verbose_name='Nombre del Rol'
    )
    descripcion = models.TextField(verbose_name='Descripción', blank=True)

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        db_table = 'roles'

    def __str__(self):
        return self.get_nombre_display()


class Permission(models.Model):
    """
    Modelo de Permisos del sistema
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre del Permiso',
        help_text='Ej: crear_cliente, autorizar_transaccion, ver_reportes'
    )
    descripcion = models.TextField(verbose_name='Descripción', blank=True)

    class Meta:
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
        db_table = 'permisos'

    def __str__(self):
        return self.nombre


class RolePermission(models.Model):
    """
    Tabla intermedia para relación Many-to-Many entre Roles y Permisos
    """
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role_permissions',
        verbose_name='Rol'
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='role_permissions',
        verbose_name='Permiso'
    )

    class Meta:
        verbose_name = 'Rol-Permiso'
        verbose_name_plural = 'Roles-Permisos'
        db_table = 'roles_permisos'
        unique_together = ('role', 'permission')

    def __str__(self):
        return f"{self.role.nombre} - {self.permission.nombre}"


class SystemUserManager(BaseUserManager):
    """
    Manager personalizado para SystemUser
    """

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('El usuario debe tener un username')

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('estado', SystemUser.UserStatus.ACTIVO)

        # Asegurarse de que el rol de administrador existe
        admin_role, created = Role.objects.get_or_create(
            nombre=Role.RoleType.ADMINISTRADOR,
            defaults={'descripcion': 'Administrador del sistema con acceso completo'}
        )

        # Asignar el rol antes de crear el usuario
        extra_fields['role'] = admin_role

        user = self.create_user(username, password, **extra_fields)

        return user


class SystemUser(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de Usuarios del Sistema (Usuarios_Sistema en el esquema)
    """

    class UserStatus(models.TextChoices):
        ACTIVO = 'activo', 'Activo'
        INACTIVO = 'inactivo', 'Inactivo'
        BLOQUEADO = 'bloqueado', 'Bloqueado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relación con Cliente (nullable porque empleados no son clientes)
    cliente = models.ForeignKey(
        'clients.Client',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Cliente'
    )

    # Credenciales
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Usuario',
        db_index=True
    )
    # password viene de AbstractBaseUser

    # Rol
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='users',
        verbose_name='Rol'
    )

    # Control de acceso
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Creación'
    )
    fecha_ultimo_acceso = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Último Acceso'
    )
    estado = models.CharField(
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.ACTIVO,
        verbose_name='Estado'
    )
    intentos_fallidos = models.IntegerField(
        default=0,
        verbose_name='Intentos Fallidos de Login'
    )
    fecha_ultimo_cambio_password = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha Último Cambio de Contraseña'
    )

    # Campos requeridos por Django
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = SystemUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Usuario del Sistema'
        verbose_name_plural = 'Usuarios del Sistema'
        db_table = 'usuarios_sistema'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.username} ({self.role.get_nombre_display()})"

    def has_permission(self, permission_name):
        """
        Verifica si el usuario tiene un permiso específico
        """
        return RolePermission.objects.filter(
            role=self.role,
            permission__nombre=permission_name
        ).exists()

    def get_permissions(self):
        """
        Retorna todos los permisos del usuario
        """
        return Permission.objects.filter(
            role_permissions__role=self.role
        )

    def increment_failed_attempts(self):
        """
        Incrementa los intentos fallidos y bloquea si es necesario
        """
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= 3:
            self.estado = self.UserStatus.BLOQUEADO
        self.save()

    def reset_failed_attempts(self):
        """
        Resetea los intentos fallidos después de login exitoso
        """
        self.intentos_fallidos = 0
        self.fecha_ultimo_acceso = timezone.now()
        self.save()

    def is_admin(self):
        """Verifica si es administrador"""
        return self.role.nombre == Role.RoleType.ADMINISTRADOR

    def is_cliente(self):
        """Verifica si es cliente"""
        return self.role.nombre == Role.RoleType.CLIENTE

    def is_cajero(self):
        """Verifica si es cajero"""
        return self.role.nombre == Role.RoleType.CAJERO

    def is_ejecutivo(self):
        """Verifica si es ejecutivo de cuentas"""
        return self.role.nombre == Role.RoleType.EJECUTIVO_CUENTAS

    def is_auditor(self):
        """Verifica si es auditor"""
        return self.role.nombre == Role.RoleType.AUDITOR

    def save(self, *args, **kwargs):
        # Si es nuevo usuario, establecer fecha de creación
        if not self.pk:
            self.fecha_creacion = timezone.now()

        # Si es administrador, darle acceso al admin de Django
        if self.role and self.role.nombre == Role.RoleType.ADMINISTRADOR:
            self.is_staff = True
            self.is_superuser = True
        else:
            self.is_staff = False
            self.is_superuser = False

        super().save(*args, **kwargs)