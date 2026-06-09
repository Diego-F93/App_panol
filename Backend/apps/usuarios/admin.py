from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Extender los campos visibles en la lista del panel
    list_display = ('username', 'email', 'rut', 'rol', 'codigo_unico', 'is_staff')
    list_filter = ('rol', 'is_staff', 'is_active')
    
    # Estructurar los formularios de edición agregando las secciones personalizadas
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Control Institucional (Pañol)', {
            'fields': ('rol', 'rut', 'codigo_unico'),
        }),
    )
    
    # Formularios de creación de usuarios en el Admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Control Institucional (Pañol)', {
            'fields': ('rol', 'rut', 'codigo_unico', 'email'),
        }),
    )
    
    search_fields = ('username', 'email', 'rut', 'codigo_unico')
    ordering = ('username',)