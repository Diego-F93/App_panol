
import uuid
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.core.mail import send_mail # Configurado previamente en settings.py vía SMTP
from .models import CustomUser
from .serializers import (
    CustomTokenObtainPairSerializer,
    CustomUserCreateSerializer, 
    ResetCodigoUnicoSerializer, 
    PasswordResetRequestSerializer
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

User = get_user_model()

class RegistrarUsuarioView(APIView):
    """
    Endpoint para que el Administrador registre nuevos usuarios.
    Ruta: POST /api/auth/usuarios/nuevo/
    """
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def post(self, request):
        serializer = CustomUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Usuario creado exitosamente."}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegenerarCodigoUnicoView(APIView):
    """
    Endpoint para regenerar el código único (UUID) de atención en mesón de un docente.
    Ruta: POST /api/auth/usuarios/reset-codigo/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ResetCodigoUnicoSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()
            
            try:
                user = User.objects.get(email=email)
                # Seguridad: Un docente solo puede resetear su propio código, el Admin/Pañolero puede resetear cualquiera
                if request.user.rol == 'DOCENTE' and request.user.email != email:
                    return Response(
                        {"error": "No tienes permisos para modificar este usuario."}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                profile = CustomUser.objects.get(user=user)
                profile.codigo_unico = uuid.uuid4() # Asignación de un nuevo identificador rápido
                profile.save()
                
                return Response({
                    "message": "Código único regenerado con éxito.",
                    "nuevo_codigo": str(profile.codigo_unico)
                }, status=status.HTTP_200_OK)
                
            except (User.DoesNotExist, CustomUser.DoesNotExist):
                return Response(
                    {"error": "El usuario no existe o no tiene un perfil de docente asociado."}, 
                    status=status.HTTP_444_NOT_FOUND
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    Endpoint simulado/básico de restablecimiento de contraseña institucional.
    Ruta: POST /api/auth/usuarios/reset-password/
    """
    permission_classes = [permissions.AllowAny] # Público

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()
            user = User.objects.filter(email=email).first()
            
            if user:
                # Generamos una contraseña provisoria aleatoria para este flujo interno simplificado
                password_provisoria = User.objects.make_random_password(length=10)
                user.set_password(password_provisoria)
                user.save()
                
                # Envío de correo electrónico (Utiliza las variables SMTP del entorno .env)
                try:
                    send_mail(
                        subject='Restablecimiento de Contraseña - Pañol Inacap',
                        message=f'Hola {user.first_name}. Tu nueva contraseña provisoria es: {password_provisoria}\nPor favor, cámbiala al iniciar sesión.',
                        from_email='panol@inacap.cl',
                        recipient_list=[email],
                        fail_silently=False,
                    )
                except Exception:
                    # En entorno de desarrollo local, si no hay SMTP real configurado, devolvemos la clave en la respuesta
                    return Response({
                        "message": "Clave generada (Error de envío SMTP).",
                        "password_provisoria_dev": password_provisoria
                    }, status=status.HTTP_200_OK)

            # Por seguridad, siempre respondemos que se envió el correo para evitar enumeración de cuentas
            return Response(
                {"message": "Si el correo existe en nuestros registros, se ha enviado una nueva contraseña provisoria."}, 
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)