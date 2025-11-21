from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet

from django.urls import include, path
from rest_framework import routers

from . import views



router = DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"groups", views.GroupViewSet)
router.register(r'clientes', ClienteViewSet)


urlpatterns = [

    path("auth/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),

    path('', views.lista_clientes, name='lista_clientes'),
    path('registrar/', views.registrar_cliente, name='registrar_cliente'),
    path('editar/<str:rut>/', views.editar_cliente, name='editar_cliente'),
    path('eliminar/<str:rut>/', views.eliminar_cliente, name='eliminar_cliente'),

    path("auth/", include(router.urls)),
]

