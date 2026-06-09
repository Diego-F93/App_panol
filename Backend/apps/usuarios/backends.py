# apps/usuarios/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Simple JWT envía el valor del formulario en el parámetro 'username'
        email = username or kwargs.get('email')
        if email is None:
            return None
            
        try:
            # Buscamos el usuario transformando el input a minúsculas
            user = UserModel.objects.get(email=email.lower())
        except UserModel.DoesNotExist:
            return None
            
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None