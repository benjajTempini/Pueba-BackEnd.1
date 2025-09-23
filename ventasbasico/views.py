from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from ventasbasico import forms
from . import models

def home(request):
    # Manejar la búsqueda
    buscar = request.GET.get('buscar', '')
    
    if buscar:
        productos = models.Productos.objects.filter(nombre__icontains=buscar)
        if not productos.exists():
            messages.info(request, f'No se encontraron productos con el nombre "{buscar}".')
    else:
        productos = models.Productos.objects.all()
    
    return render(request, 'venta/home.html', {
        'productos': productos,
        'buscar': buscar
    })

def registro(request, pk=None):
    # Si hay pk, estamos editando; si no, estamos creando
    producto = None
    if pk:
        producto = get_object_or_404(models.Productos, pk=pk)
    
    # Manejar la búsqueda
    buscar = request.GET.get('buscar', '')
    
    if request.method == 'POST':
        form = forms.ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            if producto:
                messages.success(request, 'Producto actualizado con éxito.')
            else:
                messages.success(request, 'Producto registrado con éxito.')
            return redirect('registro')
    else:
        form = forms.ProductoForm(instance=producto)
    
    # Obtener productos filtrados por búsqueda si existe
    if buscar:
        productos = models.Productos.objects.filter(nombre__icontains=buscar)
        if not productos.exists():
            messages.info(request, f'No se encontraron productos con el nombre "{buscar}".')
    else:
        productos = models.Productos.objects.all()
    
    return render(request, 'venta/registro.html', {
        'form': form,
        'productos': productos,
        'producto_editando': producto,
        'buscar': buscar
    })

def editar_producto(request, pk):
    # Redirigir a la vista de registro con el pk para editar
    return redirect('registro_editar', pk=pk)

def eliminar_producto(request, pk):
    producto = get_object_or_404(models.Productos, pk=pk)

    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado con éxito.')
        return redirect('registro')

    # Si es GET, confirmamos la eliminación desde el mismo template de registro
    productos = models.Productos.objects.all()
    form = forms.ProductoForm()
    
    return render(request, 'venta/registro.html', {
        'form': form,
        'productos': productos,
        'producto_a_eliminar': producto
    })

def ventas(request):
    return render(request, 'venta/venta.html')
