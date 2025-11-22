from rest_framework import serializers
from .models import *
from clientes.serializers import ClienteSerializer


class ProductosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Productos
        fields = ["nombre","codigo","stock","precio"]

class VentaSerializer(serializers.ModelSerializer):
    rut_cliente = ClienteSerializer(read_only=True)
    
    class Meta:
        model = Venta
        fields = ["numero","fecha","rut_cliente","total"]

class DetalleVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleVenta
        fields = ["venta","producto","cantidad","precio_unitario"]

# Se eliminaron UserSerializer y GroupSerializer de este archivo


