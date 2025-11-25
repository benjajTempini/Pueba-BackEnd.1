from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cliente
# filepath: /c:/Users/sistemas/Documents/GitHub/Pueba-BackEnd.1/clientes/views.py
from rest_framework import viewsets, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Cliente
from .serializers import ClienteSerializer, GroupSerializer, UserSerializer
import logging
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para usuarios:
    - Solo admin autenticado puede acceder
    """
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet para grupos:
    - Solo admin autenticado puede acceder
    """
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]


class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para clientes:
    - Crear/Editar: Público (cualquiera puede registrarse y actualizar sus datos)
    - Ver/Eliminar: Solo admin autenticado
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            # Permitir crear y editar sin autenticación
            permission_classes = [AllowAny]
        else:
            # Ver lista, eliminar requiere autenticación
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

logger = logging.getLogger(__name__)


# Create your views here.
def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'clientes/lista_clientes.html', {'clientes': clientes})

def registrar_cliente(request):
    if request.method == 'POST':
        rut = request.POST.get('rut')
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        comuna = request.POST.get('comuna')
        
        if not rut or not nombre or not apellido or not comuna:
            messages.error(request, "RUT, nombre, apellido y comuna son obligatorios")
            return render(request, 'clientes/registrar_cliente.html')
        
        try:
            # Verificar si el cliente ya existe
            if Cliente.objects.filter(rut=rut).exists():
                messages.error(request, f"El cliente con RUT {rut} ya está registrado")
                return render(request, 'clientes/registrar_cliente.html')
            
            # Crear el cliente
            cliente = Cliente.objects.create(
                rut=rut,
                nombre=nombre,
                apellido=apellido,
                email=email,
                comuna=comuna
            )
            
            messages.success(request, f"Cliente {nombre} {apellido} registrado exitosamente")
            return redirect('lista_clientes')
            
        except Exception as e:
            messages.error(request, f"Error al registrar cliente: {str(e)}")
    
    return render(request, 'clientes/registrar_cliente.html')

def editar_cliente(request, rut):
    cliente = get_object_or_404(Cliente, rut=rut)
    
    if request.method == 'POST':
        cliente.nombre = request.POST.get('nombre')
        cliente.apellido = request.POST.get('apellido')
        cliente.email = request.POST.get('email')
        cliente.comuna = request.POST.get('comuna')
        
        if not cliente.nombre or not cliente.apellido or not cliente.comuna:
            messages.error(request, "Nombre, apellido y comuna son obligatorios")
            return render(request, 'clientes/editar_cliente.html', {'cliente': cliente})
        
        try:
            cliente.save()
            messages.success(request, f"Cliente {cliente.nombre} {cliente.apellido} actualizado exitosamente")
            return redirect('lista_clientes')
        except Exception as e:
            messages.error(request, f"Error al actualizar cliente: {str(e)}")
    
    return render(request, 'clientes/editar_cliente.html', {'cliente': cliente})

def eliminar_cliente(request, rut):
    cliente = get_object_or_404(Cliente, rut=rut)
    
    if request.method == 'POST':
        try:
            nombre_completo = f"{cliente.nombre} {cliente.apellido}"
            cliente.delete()
            messages.success(request, f"Cliente {nombre_completo} eliminado exitosamente")
            return redirect('lista_clientes')
        except Exception as e:
            messages.error(request, f"Error al eliminar cliente: {str(e)}")
    
    return render(request, 'clientes/eliminar_cliente.html', {'cliente': cliente})
