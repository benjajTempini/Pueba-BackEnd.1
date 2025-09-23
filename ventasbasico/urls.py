from django.contrib import admin
from django.urls import include, path
from clientes import views
from ventasbasico import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('clientes/', include('clientes.urls')),
]
