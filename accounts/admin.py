from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, UserProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Administrador personalizado para el modelo CustomUser
    """
    list_display = (
        'email', 'get_full_name', 'role_badge', 'is_active',
        'fecha_registro', 'ultimo_acceso'
    )
    list_filter = ('role', 'is_active', 'fecha_registro', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name', 'username')
    ordering = ('-fecha_registro',)

    # Organizar los fieldsets
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'telefono', 'fecha_nacimiento', 'direccion')
        }),
        ('Permisos y Rol', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas importantes', {
            'fields': ('last_login', 'date_joined', 'fecha_registro', 'ultimo_acceso')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('fecha_registro', 'ultimo_acceso', 'last_login', 'date_joined')

    def role_badge(self, obj):
        """Mostrar el rol con color"""
        color_map = {
            'admin': '#dc3545',  # Rojo
            'empleado': '#0d6efd',  # Azul
            'cliente': '#198754'  # Verde
        }
        color = color_map.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 12px; font-weight: bold;">{}</span>',
            color,
            obj.get_role_display()
        )

    role_badge.short_description = 'Rol'

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    get_full_name.short_description = 'Nombre Completo'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Administrador para el perfil de usuario
    """
    list_display = (
        'user', 'numero_cliente', 'cedula', 'profesion',
        'ingresos_mensuales', 'created_at'
    )
    list_filter = (
        'user__role', 'notificaciones_email', 'notificaciones_sms', 'created_at'
    )
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'numero_cliente', 'cedula'
    )
    ordering = ('-created_at',)

    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información Bancaria', {
            'fields': ('numero_cliente', 'cedula')
        }),
        ('Información Personal', {
            'fields': ('profesion', 'ingresos_mensuales')
        }),
        ('Configuraciones', {
            'fields': ('notificaciones_email', 'notificaciones_sms')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).select_related('user')