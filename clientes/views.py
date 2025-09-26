from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Cliente

# Create your views here.
def clientes(request):
    return render(request, 'clientes/clientes.html')

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