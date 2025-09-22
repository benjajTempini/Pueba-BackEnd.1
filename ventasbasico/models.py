from django.db import models

class Venta(models.Model):
    Nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50)
    cantidad = models.IntegerField()
    precio = models.FloatField()