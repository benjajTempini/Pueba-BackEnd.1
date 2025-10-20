from django.contrib import admin
from .models import Productos, Venta, DetalleVenta
from django.http import HttpResponse
import csv


@admin.register(Productos)
class ProductosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'precio', 'stock')
    list_filter = ('nombre','precio', 'stock')
    search_fields = ('nombre', 'codigo')
    ordering = ('nombre',)

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ('subtotal',)

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fecha', 'rut_cliente', 'total')
    list_filter = ('fecha',)
    search_fields = ('numero', 'rut_cliente__rut', 'rut_cliente__nombre', 'rut_cliente__apellido')
    ordering = ('-fecha', '-id')
    readonly_fields = ('numero', 'fecha')
    inlines = [DetalleVentaInline]
    
    def has_add_permission(self, request):
        # Evitar que se puedan crear ventas desde el admin
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Evitar que se puedan eliminar ventas desde el admin
        return False
    


    
#@admin.action(description="EXPORTAR VENTA DE PRODCUTOS A CSV")
#def exportar_productos_csv(modelAdmin,request,queryset):
#    response = HttpResponse(content_type='text/csv')
#    response['Content-Disposicion'] = 'attachment; filename="productos.csv"'
#    archivo = csv.writer(response)
#    archivo.writerow(['nombre','precio','stock','activo'])
