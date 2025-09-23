from django.contrib import admin
from django.urls import include, path
from clientes import views as clientes_views
from ventasbasico import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    
    path('registro/', views.registro, name='registro'),
    path('registro/editar/<int:pk>/', views.registro, name='registro_editar'),
    path('editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),

    path('ventas/', views.ventas, name='ventas'),
    path('clientes/', include('clientes.urls')),

]
