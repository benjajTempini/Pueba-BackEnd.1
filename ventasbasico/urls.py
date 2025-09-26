from django.contrib import admin
from django.urls import include, path
from clientes import views as clientes_views
from ventasbasico import views

urlpatterns = [
    #Vista admin y Home
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    
    #Rutas para el CRUD de productos
    path('registro/', views.registro, name='registro'),
    path('editar/<int:pk>', views.editar, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar, name='eliminar'),

    # Rutas para el carrito de compras
    path('agregar-carrito/', views.agregar_carrito, name='agregar_carrito'),
    path('ver-carrito/', views.ver_carrito, name='ver_carrito'),
    path('eliminar-del-carrito/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    
    # URL para realizar ventas
    path('venta/', views.venta, name='venta'),
    
    # URLs para historial de ventas
    path('historial/', views.historial_ventas, name='historial_ventas'),
    path('detalle-venta/<int:venta_id>/', views.detalle_venta, name='detalle_venta'),
    
    # URLs para clientes habituales
    path('clientes/', clientes_views.lista_clientes, name='lista_clientes'),
    path('registrar-cliente/', clientes_views.registrar_cliente, name='registrar_cliente'),

]
