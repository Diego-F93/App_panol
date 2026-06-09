from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Indicamos que el campo visible en Swagger/Formularios se llamará 'email'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.EmailField()

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Añadir claims personalizados dentro del token encriptado (opcional)
        token['rol'] = user.rol
        token['email'] = user.email
        return token

    def validate(self, attrs):
        # Almacena la validación estándar de Simple JWT (comprueba contraseña y genera tokens)
        data = super().validate(attrs)
        
        # Inyectamos información complementaria en la respuesta JSON
        data['user'] = {
            'id': self.user.id,
            'nombre_completo': self.user.get_full_name(),
            'email': self.user.email,
            'rol': self.user.rol,
            'rut': self.user.rut,
            'codigo_unico': self.user.codigo_unico if self.user.rol == 'DOCENTE' else None
        }
        return data