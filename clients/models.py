import uuid
from django.db import models


class Client(models.Model):
    """
    Modelo temporal básico de Cliente
    Lo completaremos en el siguiente paso
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombres = models.CharField(max_length=200, verbose_name='Nombres')
    apellidos = models.CharField(max_length=200, verbose_name='Apellidos')

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        db_table = 'clientes'

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"