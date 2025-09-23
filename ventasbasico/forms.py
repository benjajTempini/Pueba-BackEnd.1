from django import forms
from .models import Productos, Venta, DetalleVenta

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Productos
        fields = ['nombre', 'codigo', 'stock', 'precio']

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['rut_cliente', 'total']

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['venta', 'producto', 'cantidad', 'precio_unitario']