from django.contrib.auth.models import Group, User
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


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]