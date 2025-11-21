from rest_framework import serializers
from .models import *


class ProductosSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Productos
        fields = ["nombre","codigo","stock","precio"]

class VentaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Venta
        fields = ["numero","fecha","rut_cliente","total"]

class DetalleVentaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DetalleVenta
        fields = ["venta","producto","cantidad","precio_unitario"]

# Se eliminaron UserSerializer y GroupSerializer de este archivo


