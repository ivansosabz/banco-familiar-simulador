import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import CustomUser

User = get_user_model()


class Command(BaseCommand):
    help = 'Crear un superusuario administrador con email'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email del administrador')
        parser.add_argument('--username', type=str, help='Username del administrador')
        parser.add_argument('--password', type=str, help='Contraseña del administrador')
        parser.add_argument('--first_name', type=str, help='Nombre del administrador')
        parser.add_argument('--last_name', type=str, help='Apellido del administrador')

    def handle(self, *args, **options):
        email = options.get('email') or input('Email: ')
        username = options.get('username') or input('Username: ')
        password = options.get('password') or input('Password: ')
        first_name = options.get('first_name') or input('Nombre: ')
        last_name = options.get('last_name') or input('Apellido: ')

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'Un usuario con email {email} ya existe.')
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'Un usuario con username {username} ya existe.')
            )
            return

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=CustomUser.UserRole.ADMIN
        )

        user.is_staff = True
        user.is_superuser = True
        user.save()

        self.stdout.write(
            self.style.SUCCESS(f'Administrador {email} creado exitosamente.')
        )