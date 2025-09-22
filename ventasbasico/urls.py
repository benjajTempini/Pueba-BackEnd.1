from django.contrib import admin
from django.urls import include, path
from clientes import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('clientes/', include('clientes.urls')),
]
