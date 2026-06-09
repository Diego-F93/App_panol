from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class CustomUser(AbstractUser):
    # Definición de Roles del Sistema
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        PANOL = 'PANOL', 'Personal de Pañol'
        DOCENTE = 'DOCENTE', 'Docente'

    # Campos transversales e institucionales
    rol = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.DOCENTE,
        help_text="Rol asignado para los permisos dentro del sistema de Pañol"
    )
    
    # Rut o Identificador chileno (ej: 12345678-9)
    rut = models.CharField(
        max_length=12, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="RUT del usuario (formato con guión y dígito verificador)"
    )

    # Código único para atención presencial rápida en el mesón de Pañol
    codigo_unico = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        help_text="Código único/QR para atención presencial o identificación rápida"
    )

    # Modificamos el email para que sea obligatorio dado el contexto institucional
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': "Ya existe un usuario registrado con este correo electrónico.",
        }
    )

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.get_full_name()} ({self.rol})"

    def save(self, *args, **kwargs):
        # Lógica de negocio automática: Si es un Docente y no tiene código único, se genera uno automáticamente
        if self.rol == self.Roles.DOCENTE and not self.codigo_unico:
            # Usamos un hash corto o UUID truncado para facilitar la lectura digital/teclado
            self.codigo_unico = str(uuid.uuid4()).split('-')[0].upper()
        super().save(*args, **kwargs)