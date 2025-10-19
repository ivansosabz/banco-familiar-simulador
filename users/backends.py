from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class SystemUserBackend(ModelBackend):
    """
    Backend de autenticación personalizado para SystemUser
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Buscar usuario por username
            user = User.objects.select_related('role').get(username=username)
        except User.DoesNotExist:
            return None

        # Verificar si está bloqueado
        if user.estado == User.UserStatus.BLOQUEADO:
            return None

        # Verificar contraseña
        if user.check_password(password):
            # Resetear intentos fallidos
            user.reset_failed_attempts()
            return user
        else:
            # Incrementar intentos fallidos
            user.increment_failed_attempts()
            return None

    def get_user(self, user_id):
        try:
            return User.objects.select_related('role').get(pk=user_id)
        except User.DoesNotExist:
            return None

