from django.contrib import admin
from django.db.models import Sum, Count
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime, timedelta
from .models import Productos, Venta, DetalleVenta

@admin.register(Productos)
class ProductosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'precio', 'stock', 'estado_stock')
    list_filter = ('precio', 'stock')
    search_fields = ('nombre', 'codigo')
    ordering = ('nombre',)
    
    def estado_stock(self, obj):
        if obj.stock == 0:
            return format_html('<span style="color: red; font-weight: bold;">Sin Stock</span>')
        elif obj.stock < 10:
            return format_html('<span style="color: orange; font-weight: bold;">Stock Bajo</span>')
        else:
            return format_html('<span style="color: green;">Stock OK</span>')
    estado_stock.short_description = 'Estado'

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    readonly_fields = ('subtotal',)
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    
    def subtotal(self, obj):
        if obj.id:
            return f"${ obj.subtotal:,.2f}"
        return "-"
    subtotal.short_description = 'Subtotal'

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fecha', 'rut_cliente', 'total_formateado', 'cantidad_items')
    list_filter = ('fecha',)
    search_fields = ('numero', 'rut_cliente__rut', 'rut_cliente__nombre', 'rut_cliente__apellido')
    ordering = ('-fecha', '-id')
    readonly_fields = ('numero', 'fecha', 'total', 'calcular_total_detalles')
    inlines = [DetalleVentaInline]
    
    def total_formateado(self, obj):
        return f"${obj.total:,.2f}"
    total_formateado.short_description = 'Total'
    total_formateado.admin_order_field = 'total'
    
    def cantidad_items(self, obj):
        cantidad = obj.detalles.aggregate(total=Sum('cantidad'))['total'] or 0
        return cantidad
    cantidad_items.short_description = 'Items'
    
    def calcular_total_detalles(self, obj):
        if obj.id:
            total = sum(detalle.subtotal for detalle in obj.detalles.all())
            return format_html('<strong>${:,.2f}</strong>', total)
        return "-"
    calcular_total_detalles.short_description = 'Total Calculado'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('reporte-ventas/', self.admin_site.admin_view(self.reporte_ventas), name='reporte-ventas'),
        ]
        return custom_urls + urls
    
    def reporte_ventas(self, request):
        '''Vista para generar reporte de ventas por rango de fechas'''
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        
        ventas = Venta.objects.all().order_by('-fecha')
        
        # Aplicar filtros si existen
        if fecha_inicio:
            ventas = ventas.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            ventas = ventas.filter(fecha__lte=fecha_fin)
        
        # Estadísticas
        total_ventas = ventas.aggregate(
            total=Sum('total'),
            cantidad=Count('id')
        )
        
        context = {
            'ventas': ventas,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'total_ventas': total_ventas['total'] or 0,
            'cantidad_ventas': total_ventas['cantidad'] or 0,
            'title': 'Reporte de Ventas',
            'site_header': 'Administración',
            'has_permission': True,
        }
        
        return render(request, 'admin/reporte_ventas.html', context)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_reporte_link'] = True
        return super().changelist_view(request, extra_context)
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    
    def has_add_permission(self, request):
        # Evitar que se puedan crear ventas desde el admin
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Evitar que se puedan eliminar ventas desde el admin
        return False
