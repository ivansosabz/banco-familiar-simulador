from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import SystemUser, Role, Permission, RolePermission


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'count_users', 'count_permissions')
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)

    def count_users(self, obj):
        count = obj.users.count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)

    count_users.short_description = 'Usuarios'

    def count_permissions(self, obj):
        count = obj.role_permissions.count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)

    count_permissions.short_description = 'Permisos'


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'count_roles')
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)

    def count_roles(self, obj):
        count = obj.role_permissions.count()
        return format_html('<span style="font-weight: bold;">{}</span>', count)

    count_roles.short_description = 'Roles'


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'permission')
    list_filter = ('role',)
    search_fields = ('role__nombre', 'permission__nombre')


@admin.register(SystemUser)
class SystemUserAdmin(BaseUserAdmin):
    list_display = (
        'username', 'role_badge', 'estado_badge',
        'intentos_fallidos', 'fecha_ultimo_acceso', 'fecha_creacion'
    )
    list_filter = ('role', 'estado', 'fecha_creacion')
    search_fields = ('username', 'cliente__nombres', 'cliente__apellidos')
    ordering = ('-fecha_creacion',)

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Información de Rol', {
            'fields': ('role', 'cliente')
        }),
        ('Estado y Seguridad', {
            'fields': ('estado', 'intentos_fallidos', 'fecha_ultimo_cambio_password')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_ultimo_acceso'),
            'classes': ('collapse',)
        }),
        ('Permisos de Django', {
            'fields': ('is_staff', 'is_active', 'is_superuser'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'role', 'password1', 'password2', 'estado'),
        }),
    )

    readonly_fields = ('fecha_creacion', 'fecha_ultimo_acceso', 'is_staff', 'is_superuser')

    def role_badge(self, obj):
        color_map = {
            'administrador': '#dc3545',
            'cajero': '#0d6efd',
            'ejecutivo_cuentas': '#6f42c1',
            'auditor': '#fd7e14',
            'cliente': '#198754'
        }
        color = color_map.get(obj.role.nombre, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.role.get_nombre_display()
        )

    role_badge.short_description = 'Rol'

    def estado_badge(self, obj):
        color_map = {
            'activo': '#198754',
            'inactivo': '#6c757d',
            'bloqueado': '#dc3545'
        }
        color = color_map.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_estado_display()
        )

    estado_badge.short_description = 'Estado'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('role', 'cliente')