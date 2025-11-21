from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.db import transaction
from datetime import date, datetime
from ventasbasico import forms
from .models import Productos, Venta, DetalleVenta
from clientes.models import Cliente
import logging
from rest_framework import permissions, viewsets

# Importa los serializadores locales de ventas
from .serializers import ProductosSerializer, VentaSerializer, DetalleVentaSerializer

# Importa los serializadores de usuarios y grupos desde la app 'clientes'
from clientes.serializers import GroupSerializer, UserSerializer

class ProductosViewSet(viewsets.ModelViewSet):
    queryset = Productos.objects.all().order_by("nombre")
    serializer_class = ProductosSerializer
    permission_classes = []

class VentaViewsSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all().order_by("numero")
    serializer_class = VentaSerializer
    permission_classes = [permissions.IsAuthenticated]

class DetalleVentaViewSet(viewsets.ModelViewSet):
    queryset = DetalleVenta.objects.all().order_by("venta")
    serializer_class = DetalleVentaSerializer
    permission_classes = [permissions.IsAuthenticated]



logger = logging.getLogger(__name__)

def generar_numero_venta():
    """Genera un número único para la venta"""
    # Obtener fecha actual
    fecha_actual = datetime.now()
    prefijo = fecha_actual.strftime("%Y%m%d")
    
    # Contar ventas del día actual
    ventas_hoy = Venta.objects.filter(fecha=date.today()).count()
    
    # Generar número consecutivo (máximo 10 intentos para evitar loops infinitos)
    max_intentos = 10
    for i in range(max_intentos):
        numero = f"{prefijo}-{ventas_hoy + i + 1:04d}"
        if not Venta.objects.filter(numero=numero).exists():
            return numero
    
    # Si después de 10 intentos no se encontró número, usar timestamp
    return f"{prefijo}-{int(datetime.now().timestamp())}"

def historial_ventas(request):
    """Vista para mostrar el historial de ventas"""
    try:
        ventas = Venta.objects.all().order_by('-fecha', '-id')
        
        # Filtro por fecha si se proporciona
        fecha_filtro = request.GET.get('fecha')
        if fecha_filtro:
            try:
                from datetime import datetime
                # Parsear la fecha del formulario (formato YYYY-MM-DD)
                fecha_obj = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
                ventas = ventas.filter(fecha=fecha_obj)
                logger.info(f"Filtrando por fecha: {fecha_obj}, ventas encontradas: {ventas.count()}")
            except ValueError:
                # Si hay error en el formato, ignorar el filtro
                logger.warning(f"Formato de fecha inválido: {fecha_filtro}")
        
        # Filtro por cliente si se proporciona
        cliente_filtro = request.GET.get('cliente')
        if cliente_filtro:
            ventas = ventas.filter(rut_cliente__rut__icontains=cliente_filtro)
        
        # Calcular el monto total de todas las ventas
        from django.db.models import Sum
        monto_total = ventas.aggregate(Sum('total'))['total__sum'] or 0
        
        return render(request, 'venta/historial.html', {
            'ventas': ventas,
            'fecha_filtro': fecha_filtro,
            'cliente_filtro': cliente_filtro,
            'monto_total': monto_total
        })
    except Exception as e:
        logger.error(f"Error en historial_ventas: {str(e)}")
        messages.error(request, "Error al cargar el historial de ventas")
        return redirect('home')

def detalle_venta(request, venta_id):
    """Vista para mostrar el detalle de una venta específica"""
    try:
        venta = get_object_or_404(Venta, id=venta_id)
        detalles = DetalleVenta.objects.filter(venta=venta)
        
        return render(request, 'venta/detalle_venta.html', {
            'venta': venta,
            'detalles': detalles
        })
    except Exception as e:
        logger.error(f"Error en detalle_venta: {str(e)}")
        messages.error(request, "Error al cargar el detalle de la venta")
        return redirect('historial_ventas')

def home(request):
    """Página principal con lista de productos"""
    try:
        # Consulta todos los productos de la base de datos
        productos = Productos.objects.all()
        return render(request, 'venta/home.html', {'productos': productos})
    except Exception as e:
        logger.error(f"Error en home: {str(e)}")
        # Si hay error con la BD, mostrar página sin productos
        messages.error(request, "Error al cargar productos")
        return render(request, 'venta/home.html', {'productos': []})

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
    producto = get_object_or_404(Productos,pk=pk)

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
    producto = get_object_or_404(Productos,pk=pk)
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
            producto = Productos.objects.get(id=producto_id)
            
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
            
        except Productos.DoesNotExist:
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
            
            # Usar transacción para garantizar consistencia de datos
            with transaction.atomic():
                cliente_obj = None
                
                # Si es cliente habitual, verificar que existe
                if es_cliente_habitual:
                    try:
                        cliente_obj = Cliente.objects.get(rut=rut_cliente)
                        messages.info(request, f"Cliente habitual: {cliente_obj.nombre} {cliente_obj.apellido}")
                    except Cliente.DoesNotExist:
                        messages.error(request, f"El RUT {rut_cliente} no está registrado como cliente habitual")
                        return render(request, 'venta/venta.html', {
                            'carrito': carrito, 
                            'total': total, 
                            'clientes': clientes
                        })
                else:
                    # Para clientes no habituales, crear o buscar cliente temporal
                    cliente_obj, created = Cliente.objects.get_or_create(
                        rut=rut_cliente,
                        defaults={
                            'nombre': 'Cliente',
                            'apellido': 'Temporal',
                            'comuna': 'No especificada'
                        }
                    )
                
                # Verificar stock antes de procesar
                for producto_id, item in carrito.items():
                    producto = Productos.objects.get(id=producto_id)
                    if producto.stock < item['cantidad']:
                        messages.error(request, f"Stock insuficiente para {producto.nombre}")
                        return render(request, 'venta/venta.html', {
                            'carrito': carrito, 
                            'total': total, 
                            'clientes': clientes
                        })
                
                # Crear la venta
                numero_venta = generar_numero_venta()
                venta = Venta.objects.create(
                    numero=numero_venta,
                    rut_cliente=cliente_obj,
                    total=total
                )
                
                # Crear los detalles de venta y actualizar stock
                for producto_id, item in carrito.items():
                    producto = Productos.objects.get(id=producto_id)
                    
                    # Crear detalle de venta
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=item['cantidad'],
                        precio_unitario=item['precio']
                    )
                    
                    # Reducir stock
                    producto.stock -= item['cantidad']
                    producto.save()
                
                # Limpiar carrito
                request.session['carrito'] = {}
                request.session.modified = True
                
                if es_cliente_habitual:
                    messages.success(request, f"Venta #{numero_venta} realizada exitosamente al cliente habitual: {cliente_obj.nombre} {cliente_obj.apellido}")
                else:
                    messages.success(request, f"Venta #{numero_venta} realizada exitosamente al cliente RUT: {rut_cliente}")
                
                return redirect('home')
            
        except Exception as e:
            messages.error(request, f"Error al procesar la venta: {str(e)}")
    
    return render(request, 'venta/venta.html', {
        'carrito': carrito,
        'total': total,
        'clientes': clientes
    })
