from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser
    """

    class UserRole(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        CLIENTE = 'cliente', 'Cliente'
        EMPLEADO = 'empleado', 'Empleado del Banco'

    # Campos adicionales
    email = models.EmailField('Email', unique=True)
    role = models.CharField(
        'Rol',
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CLIENTE
    )

    # Información personal
    telefono_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Formato: '+999999999'. Hasta 15 dígitos."
    )
    telefono = models.CharField(
        'Teléfono',
        validators=[telefono_validator],
        max_length=17,
        blank=True
    )

    fecha_nacimiento = models.DateField('Fecha de Nacimiento', null=True, blank=True)
    direccion = models.TextField('Dirección', blank=True)

    # Campos de control
    is_active = models.BooleanField('Activo', default=True)
    fecha_registro = models.DateTimeField('Fecha de Registro', default=timezone.now)
    ultimo_acceso = models.DateTimeField('Último Acceso', null=True, blank=True)

    # Campo para hacer email obligatorio en registro
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.first_name} {self.last_name}".strip()

    def get_role_display_badge(self):
        """Retorna el rol con estilo para templates"""
        role_styles = {
            'admin': 'bg-danger',
            'empleado': 'bg-primary',
            'cliente': 'bg-success'
        }
        return role_styles.get(self.role, 'bg-secondary')

    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.role == self.UserRole.ADMIN

    def is_cliente(self):
        """Verifica si el usuario es cliente"""
        return self.role == self.UserRole.CLIENTE

    def is_empleado(self):
        """Verifica si el usuario es empleado del banco"""
        return self.role == self.UserRole.EMPLEADO

    def save(self, *args, **kwargs):
        # Si es la primera vez que se guarda, establecer fecha de registro
        if not self.pk:
            self.fecha_registro = timezone.now()

        # Si es admin, asegurar que tenga permisos de staff
        if self.role == self.UserRole.ADMIN:
            self.is_staff = True
            self.is_superuser = True
        else:
            self.is_staff = False
            self.is_superuser = False

        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """
    Perfil extendido del usuario para información adicional
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # Información bancaria
    numero_cliente = models.CharField(
        'Número de Cliente',
        max_length=20,
        unique=True,
        blank=True
    )

    # Información adicional
    cedula = models.CharField(
        'Cédula de Identidad',
        max_length=20,
        blank=True,
        unique=True
    )

    profesion = models.CharField('Profesión', max_length=100, blank=True)
    ingresos_mensuales = models.DecimalField(
        'Ingresos Mensuales',
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Configuraciones de usuario
    notificaciones_email = models.BooleanField(
        'Recibir notificaciones por email',
        default=True
    )
    notificaciones_sms = models.BooleanField(
        'Recibir notificaciones por SMS',
        default=False
    )

    # Metadatos
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        return f"Perfil de {self.user.get_full_name()}"

    def generate_numero_cliente(self):
        """Genera un número de cliente único"""
        if not self.numero_cliente:
            import random
            import string
            while True:
                numero = ''.join(random.choices(string.digits, k=10))
                if not UserProfile.objects.filter(numero_cliente=numero).exists():
                    self.numero_cliente = numero
                    break

    def save(self, *args, **kwargs):
        if not self.numero_cliente and self.user.is_cliente():
            self.generate_numero_cliente()
        super().save(*args, **kwargs)


# Signals para crear automáticamente el perfil
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Crear perfil automáticamente cuando se crea un usuario"""
    if created:
        UserProfile.objects.create(user=instance)