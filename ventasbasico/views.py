from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from ventasbasico import forms
from . import models
from clientes.models import Cliente

def home(request):
    #Consulta todos los productos de la base de datos
    productos = models.Productos.objects.all()
    #Redirecciona al home.html y envia la lista de los productos que estan en la base de datos 
    return render(request,'venta/home.html', {'productos': productos})

def registro(request):
    if request.method == 'POST': # seleccionamos el metodo post para poder ingresar datos a la BD
        form = forms.ProductoForm(request.POST) #se crea la variable form y se le pasan los dato senviados por el usuario , llenando el formulario
        if form.is_valid(): #valida si los datos cumplen con las reglas del formulario 
            form.save() #guarda los datos del formulario en la base de datos
            messages.success(request, 'Producto cargado exitosamente :D')
            return redirect('home') #redirige al usuario al home
        else: #si no es valido el dato entra acá
            messages.error(request, "Por favor corrige los errores en el formulario")
    else:
        form = forms.ProductoForm() #si el metodo no es POST muestra el formulario vacio

    return render(request, 'venta/registro.html', {'form': form})

def editar(request, pk):
    producto = get_object_or_404(models.Productos,pk=pk)

    if request.method == 'POST':
        form = forms.ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente 😊')
            return redirect('home')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")

    else:
        form = forms.ProductoForm(instance=producto)  

    return render(request, 'venta/editar.html', {'form':form, 'producto':producto})

def eliminar(request, pk):
    producto = get_object_or_404(models.Productos,pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto Eliminado exitosamente 😊')
        return redirect('home')
    return render(request, 'venta/eliminar.html',{'producto':producto})

def agregar_carrito(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad', 1))
        
        try:
            producto = models.Productos.objects.get(id=producto_id)
            
            # Verificar stock disponible
            if cantidad > producto.stock:
                messages.error(request, f"Stock insuficiente. Solo hay {producto.stock} unidades disponibles")
                return redirect('home')
            
            # Obtener carrito de la sesión
            carrito = request.session.get('carrito', {})
            
            # Si el producto ya está en el carrito, sumar la cantidad
            if producto_id in carrito:
                nueva_cantidad = carrito[producto_id]['cantidad'] + cantidad
                if nueva_cantidad > producto.stock:
                    messages.error(request, f"No puedes agregar más. Stock máximo: {producto.stock}")
                    return redirect('home')
                carrito[producto_id]['cantidad'] = nueva_cantidad
            else:
                # Agregar nuevo producto al carrito
                carrito[producto_id] = {
                    'nombre': producto.nombre,
                    'precio': float(producto.precio),
                    'cantidad': cantidad,
                    'stock_disponible': producto.stock
                }
            
            # Guardar carrito en la sesión
            request.session['carrito'] = carrito
            request.session.modified = True
            
            messages.success(request, f"Se agregaron {cantidad} unidades de {producto.nombre} al carrito")
            
        except models.Productos.DoesNotExist:
            messages.error(request, "El producto no existe")
        except Exception as e:
            messages.error(request, f"Error al agregar al carrito: {str(e)}")
    
    return redirect('home')

def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    total = 0
    
    for item in carrito.values():
        total += item['precio'] * item['cantidad']
    
    return render(request, 'venta/carrito.html', {
        'carrito': carrito,
        'total': total
    })

def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    
    if str(producto_id) in carrito:
        producto_nombre = carrito[str(producto_id)]['nombre']
        del carrito[str(producto_id)]
        request.session['carrito'] = carrito
        request.session.modified = True
        messages.success(request, f"Se eliminó {producto_nombre} del carrito")
    
    return redirect('ver_carrito')

def venta(request):
    carrito = request.session.get('carrito', {})
    
    if not carrito:
        messages.warning(request, "El carrito está vacío")
        return redirect('home')
    
    total = sum(item['precio'] * item['cantidad'] for item in carrito.values())
    
    # Obtener lista de clientes habituales para el dropdown
    clientes = Cliente.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        rut_cliente = request.POST.get('rut_cliente')
        es_cliente_habitual = request.POST.get('es_cliente_habitual') == 'on'
        
        if not rut_cliente:
            messages.error(request, "Debe ingresar el RUT del cliente")
            return render(request, 'venta/venta.html', {
                'carrito': carrito, 
                'total': total, 
                'clientes': clientes
            })
        
        try:
            cliente_info = None
            
            # Si es cliente habitual, verificar que existe
            if es_cliente_habitual:
                try:
                    cliente_info = Cliente.objects.get(rut=rut_cliente)
                    messages.info(request, f"Cliente habitual: {cliente_info.nombre} {cliente_info.apellido}")
                except Cliente.DoesNotExist:
                    messages.error(request, f"El RUT {rut_cliente} no está registrado como cliente habitual")
                    return render(request, 'venta/venta.html', {
                        'carrito': carrito, 
                        'total': total, 
                        'clientes': clientes
                    })
            
            # Procesar cada item del carrito
            for producto_id, item in carrito.items():
                producto = models.Productos.objects.get(id=producto_id)
                
                # Verificar stock nuevamente
                if producto.stock < item['cantidad']:
                    messages.error(request, f"Stock insuficiente para {producto.nombre}")
                    return render(request, 'venta/venta.html', {
                        'carrito': carrito, 
                        'total': total, 
                        'clientes': clientes
                    })
                
                # Reducir stock
                producto.stock -= item['cantidad']
                producto.save()
            
            # Limpiar carrito
            request.session['carrito'] = {}
            request.session.modified = True
            
            if cliente_info:
                messages.success(request, f"Venta realizada exitosamente al cliente habitual: {cliente_info.nombre} {cliente_info.apellido}")
            else:
                messages.success(request, f"Venta realizada exitosamente al cliente RUT: {rut_cliente}")
            
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f"Error al procesar la venta: {str(e)}")
    
    return render(request, 'venta/venta.html', {
        'carrito': carrito,
        'total': total,
        'clientes': clientes
    })
