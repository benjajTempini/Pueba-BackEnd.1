from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet

from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views



router = DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"groups", views.GroupViewSet)
router.register(r'clientes', ClienteViewSet)


urlpatterns = [

    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),

    path('', views.lista_clientes, name='lista_clientes'),
    path('registrar/', views.registrar_cliente, name='registrar_cliente'),
    path('editar/<str:rut>/', views.editar_cliente, name='editar_cliente'),
    path('eliminar/<str:rut>/', views.eliminar_cliente, name='eliminar_cliente'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

