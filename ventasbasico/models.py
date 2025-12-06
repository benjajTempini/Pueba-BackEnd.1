from django.db import models

from clientes.models import Cliente

class Productos(models.Model):
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=50, unique=True, editable=False)  # Autoincremental, no editable
    stock = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    foto = models.BinaryField(blank=True, null=True, editable=True)
    
    # Campos para descripciones generadas por IA
    descripcion_corta = models.CharField(
        max_length=500, 
        blank=True, 
        null=True,
        help_text="Descripción breve generada por IA (1-2 líneas)"
    )
    descripcion_larga = models.TextField(
        blank=True, 
        null=True,
        help_text="Descripción detallada generada por IA"
    )
    palabras_clave = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Keywords SEO generadas por IA (separadas por comas)"
    )
    beneficios = models.TextField(
        blank=True,
        null=True,
        help_text="Lista de beneficios generados por IA (formato JSON)"
    )
    descripcion_generada_fecha = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha en que se generó la descripción con IA"
    )

    def save(self, *args, **kwargs):
        # Si no tiene código asignado (nuevo producto), generar uno automático
        if not self.codigo:
            self.codigo = self._generar_codigo_automatico()
        super().save(*args, **kwargs)
    
    def _generar_codigo_automatico(self):
        """
        Genera un código automático siguiendo el orden numérico.
        Si hay huecos en la secuencia (productos eliminados), los llena primero.
        Si no hay huecos, asigna el siguiente número disponible.
        """
        # Obtener todos los códigos existentes que sean numéricos
        codigos_existentes = Productos.objects.exclude(codigo='').values_list('codigo', flat=True)
        
        # Convertir a números (solo los que sean convertibles)
        numeros_usados = []
        for codigo in codigos_existentes:
            try:
                numeros_usados.append(int(codigo))
            except ValueError:
                # Si hay códigos no numéricos (productos viejos), los ignoramos
                pass
        
        # Ordenar los números
        numeros_usados.sort()
        
        # Buscar el primer hueco disponible o el siguiente número
        siguiente_numero = 1
        for numero in numeros_usados:
            if numero == siguiente_numero:
                siguiente_numero += 1
            elif numero > siguiente_numero:
                # Encontramos un hueco
                break
        
        # Retornar el código con formato de 4 dígitos (ej: 0001, 0002, ...)
        return str(siguiente_numero).zfill(4)

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