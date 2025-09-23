from django.db import models

from clientes.models import Cliente

class Productos(models.Model):
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=50, unique=True)
    stock = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre
    
class Venta(models.Model):
    numero = models.CharField(max_length=50, unique=True)
    fecha = models.DateField(auto_now_add=True)
    rut_cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Boleta {self.numero} - {self.rut_cliente}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Productos, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"