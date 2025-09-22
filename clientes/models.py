from django.db import models

# Create your models here.
class Cliente(models.Model):
    Rut = models.CharField(max_length=12, primary_key=True)
    Nombre = models.CharField(max_length=100)
    Apellido = models.CharField(max_length=100)
    Email = models.EmailField(max_length=100)
    Comuna = models.CharField(max_length=100)