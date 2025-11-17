from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet)


urlpatterns = [
    path('', views.lista_clientes, name='lista_clientes'),
    path('registrar/', views.registrar_cliente, name='registrar_cliente'),
    path('editar/<str:rut>/', views.editar_cliente, name='editar_cliente'),
    path('eliminar/<str:rut>/', views.eliminar_cliente, name='eliminar_cliente'),

    path("auth/", include(router.urls)),
]

