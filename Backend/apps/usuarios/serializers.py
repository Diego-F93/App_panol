from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import CustomUser

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
    

User = get_user_model()

class CustomUserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para que el Administrador cree nuevos usuarios (Docentes o Pañoleros).
    Maneja la creación del perfil en caso de ser un docente de forma automática.
    """
    rut = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'rol', 'rut', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        """Valida que el correo institucional sea único."""
        normalized_email = value.lower()
        if User.objects.filter(email=normalized_email).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado.")
        return normalized_email

    def create(self, validated_data):
        rut = validated_data.pop('rut', None)
        password = validated_data.pop('password')
        
        # Crear el usuario base usando el manager para hashear la contraseña
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        # Si el rol asignado es DOCENTE, se genera automáticamente su perfil
        if user.rol == 'DOCENTE':
            CustomUser.objects.create(user=user, rut=rut)
            
        return user


class ResetCodigoUnicoSerializer(serializers.Serializer):
    """Serializer para regenerar el código único de un docente mediante su email."""
    email = serializers.EmailField()


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer básico para solicitar cambio de contraseña mediante email."""
    email = serializers.EmailField()