from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre', 'apellido', 'email', 'comuna')
    list_filter = ('comuna',)
    search_fields = ('rut', 'nombre', 'apellido', 'email')
    ordering = ('nombre', 'apellido')
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('rut', 'nombre', 'apellido')
        }),
        ('Información de Contacto', {
            'fields': ('email', 'comuna')
        }),
    )
