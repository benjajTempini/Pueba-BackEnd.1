from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.db import transaction
from datetime import date, datetime
from ventasbasico import forms
from .models import Productos, Venta, DetalleVenta
from clientes.models import Cliente
import logging
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.decorators import login_required
# Importa los serializadores locales de ventas
from .serializers import ProductosSerializer, VentaSerializer, DetalleVentaSerializer

# Importa los serializadores de usuarios y grupos desde la app 'clientes'
from clientes.serializers import GroupSerializer, UserSerializer

# Importar servicio de GroqCloud para IA
from .groq_service import GroqService

class ProductosViewSet(viewsets.ModelViewSet):
    """
    ViewSet para productos:
    - Listar y ver: Público (clientes pueden ver productos sin login)
    - Crear/Editar/Eliminar: Solo admin autenticado
    """
    queryset = Productos.objects.all().order_by("nombre")
    serializer_class = ProductosSerializer
    lookup_field = 'codigo'  # Usar código en lugar de id para búsquedas
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # Permitir ver productos sin autenticación
            permission_classes = [AllowAny]
        else:
            # Crear, actualizar, eliminar requiere autenticación
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

class VentaViewsSet(viewsets.ModelViewSet):
    """
    ViewSet para ventas:
    - Crear: Público (clientes pueden comprar sin login)
    - Ver/Editar/Eliminar: Solo admin autenticado
    """
    queryset = Venta.objects.all().order_by("numero")
    serializer_class = VentaSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            # Permitir crear ventas sin autenticación (compras de clientes)
            permission_classes = [AllowAny]
        else:
            # Ver historial, editar, eliminar requiere autenticación
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

class DetalleVentaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para detalles de venta:
    - Ver detalles: Público (para que clientes vean sus compras)
    - Crear/Editar/Eliminar: Solo admin autenticado
    """
    queryset = DetalleVenta.objects.all().order_by("venta")
    serializer_class = DetalleVentaSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # Permitir ver detalles sin autenticación
            permission_classes = [AllowAny]
        else:
            # Crear, editar, eliminar requiere autenticación
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filtrar por venta si se proporciona el parámetro"""
        queryset = super().get_queryset()
        venta_numero = self.request.query_params.get('venta', None)
        if venta_numero:
            # Filtrar por el número de venta (campo de texto en el modelo Venta)
            queryset = queryset.filter(venta__numero=venta_numero)
        return queryset



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


# ============================================
# ENDPOINTS CON IA - GROQ CLOUD
# ============================================



@api_view(['POST'])
@permission_classes([AllowAny])
def recomendar_productos_ia(request):
    """
    Endpoint: POST /api/ia/productos/recomendar/
    
    Recomienda productos usando IA basándose en el historial de compras del cliente
    
    Body:
    {
        "rut_cliente": "12345678-9",
        "limite": 3  // Opcional, default 3
    }
    
    Response:
    {
        "recomendaciones": [
            {
                "producto_id": 1,
                "nombre": "Producto X",
                "precio": 25000,
                "stock": 50,
                "razon": "Basado en tus compras anteriores de productos similares",
                "confianza": "alta"
            }
        ],
        "mensaje": "Estos productos podrían interesarte basado en tus compras anteriores"
    }
    """
    try:
        rut_cliente = request.data.get('rut_cliente')
        limite = request.data.get('limite', 3)
        
        if not rut_cliente:
            return Response(
                {'error': 'El campo rut_cliente es obligatorio'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que el cliente existe
        try:
            cliente = Cliente.objects.get(rut=rut_cliente)
        except Cliente.DoesNotExist:
            return Response(
                {'error': f'Cliente con RUT {rut_cliente} no existe'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener historial de compras del cliente
        ventas = Venta.objects.filter(rut_cliente=cliente).prefetch_related('detalles__producto')
        
        historial = []
        for venta in ventas:
            for detalle in venta.detalles.all():
                historial.append({
                    'producto': detalle.producto.nombre,
                    'cantidad': detalle.cantidad,
                    'fecha': venta.fecha.strftime('%Y-%m-%d')
                })
        
        # Obtener TODOS los productos disponibles (no solo una muestra)
        productos_disponibles = []
        todos_los_productos = Productos.objects.filter(stock__gt=0).order_by('-id')
        
        logger.info(f"Total de productos disponibles en BD: {todos_los_productos.count()}")
        
        for producto in todos_los_productos:
            productos_disponibles.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'codigo': producto.codigo,
                'precio': float(producto.precio),
                'stock': producto.stock
            })
        
        if not productos_disponibles:
            return Response(
                {'error': 'No hay productos disponibles en stock'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        logger.info(f"Enviando {len(productos_disponibles)} productos a la IA para recomendación")
        
        # Llamar a GroqCloud para obtener recomendaciones
        groq = GroqService()
        resultado = groq.recomendar_productos(
            historial_cliente={
                'cliente': f"{cliente.nombre} {cliente.apellido}",
                'compras': historial
            },
            productos_disponibles=productos_disponibles,
            limite=limite
        )
        
        # Enriquecer recomendaciones con datos completos del producto
        recomendaciones_enriquecidas = []
        for rec in resultado.get('recomendaciones', []):
            try:
                producto = Productos.objects.get(id=rec['producto_id'])
                recomendaciones_enriquecidas.append({
                    'producto_id': producto.id,
                    'nombre': producto.nombre,
                    'codigo': producto.codigo,
                    'precio': float(producto.precio),
                    'stock': producto.stock,
                    'razon': rec.get('razon', ''),
                    'confianza': rec.get('confianza', 'media')
                })
            except Productos.DoesNotExist:
                continue
        
        return Response({
            'cliente': {
                'rut': cliente.rut,
                'nombre': f"{cliente.nombre} {cliente.apellido}"
            },
            'recomendaciones': recomendaciones_enriquecidas,
            'mensaje': resultado.get('mensaje', 'Productos recomendados para ti')
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error en recomendar_productos_ia: {str(e)}")
        return Response(
            {'error': f'Error al generar recomendaciones: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generar_descripcion_ia(request, producto_id):
    """
    Endpoint: POST /api/ia/productos/{producto_id}/generar-descripcion/
    
    Genera una descripción atractiva para un producto usando IA
    Requiere autenticación (solo admin)
    
    Response:
    {
        "producto": {
            "id": 1,
            "nombre": "Producto X",
            "codigo": "ABC123"
        },
        "descripcion_corta": "Descripción breve y atractiva",
        "descripcion_larga": "Descripción detallada completa...",
        "palabras_clave": ["keyword1", "keyword2", ...],
        "beneficios": ["Beneficio 1", "Beneficio 2", ...]
    }
    """
    try:
        # Buscar el producto
        try:
            producto = Productos.objects.get(id=producto_id)
        except Productos.DoesNotExist:
            return Response(
                {'error': f'Producto con ID {producto_id} no existe'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Preparar características del producto
        caracteristicas = {
            'codigo': producto.codigo,
            'precio': float(producto.precio),
            'stock': producto.stock
        }
        
        # Llamar a GroqCloud para generar descripción
        groq = GroqService()
        resultado = groq.generar_descripcion_producto(
            nombre_producto=producto.nombre,
            caracteristicas=caracteristicas
        )
        
        # GUARDAR la descripción generada en la base de datos
        import json
        from django.utils import timezone
        
        producto.descripcion_corta = resultado.get('descripcion_corta', '')
        producto.descripcion_larga = resultado.get('descripcion_larga', '')
        producto.palabras_clave = ', '.join(resultado.get('palabras_clave', []))
        producto.beneficios = json.dumps(resultado.get('beneficios', []), ensure_ascii=False)
        producto.descripcion_generada_fecha = timezone.now()
        producto.save()
        
        logger.info(f"Descripción IA guardada para producto {producto.id}: {producto.nombre}")
        
        return Response({
            'producto': {
                'id': producto.id,
                'nombre': producto.nombre,
                'codigo': producto.codigo,
                'precio': float(producto.precio)
            },
            'descripcion_corta': resultado.get('descripcion_corta', ''),
            'descripcion_larga': resultado.get('descripcion_larga', ''),
            'palabras_clave': resultado.get('palabras_clave', []),
            'beneficios': resultado.get('beneficios', []),
            'guardado': True,
            'fecha_generacion': producto.descripcion_generada_fecha.isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error en generar_descripcion_ia: {str(e)}")
        return Response(
            {'error': f'Error al generar descripción: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def stats_ia(request):
    """
    Endpoint: GET /api/ia/stats/
    
    Muestra estadísticas de la IA y productos disponibles
    Útil para debugging y verificar que la IA tiene acceso a todos los productos
    """
    try:
        total_productos = Productos.objects.count()
        productos_con_stock = Productos.objects.filter(stock__gt=0).count()
        productos_sin_stock = Productos.objects.filter(stock=0).count()
        
        total_clientes = Cliente.objects.count()
        total_ventas = Venta.objects.count()
        
        # Muestra de productos disponibles
        productos_muestra = []
        for p in Productos.objects.filter(stock__gt=0).order_by('nombre')[:10]:
            productos_muestra.append({
                'id': p.id,
                'nombre': p.nombre,
                'precio': float(p.precio),
                'stock': p.stock
            })
        
        return Response({
            'productos': {
                'total': total_productos,
                'con_stock': productos_con_stock,
                'sin_stock': productos_sin_stock
            },
            'clientes': total_clientes,
            'ventas': total_ventas,
            'muestra_productos': productos_muestra,
            'mensaje': f'La IA tiene acceso a {productos_con_stock} productos con stock disponible'
        })
    except Exception as e:
        logger.error(f"Error en stats_ia: {str(e)}")
        return Response(
            {'error': f'Error al obtener estadísticas: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def chatbot_atencion(request):
    """
    Endpoint: POST /api/ia/chat/
    
    Chatbot de atención al cliente usando IA
    Responde preguntas sobre productos, ventas, políticas, etc.
    
    Body:
    {
        "mensaje": "¿Cuál es el horario de atención?",
        "contexto": {  // Opcional
            "venta_numero": "20241128-0001",  // Para consultar sobre una venta específica
            "producto_id": 5  // Para consultar sobre un producto específico
        }
    }
    
    Response:
    {
        "respuesta": "Nuestro horario de atención es...",
        "tipo": "informacion",
        "requiere_humano": false,
        "sugerencias": [
            "¿Cuáles son los métodos de pago?",
            "¿Cuánto demora el despacho?"
        ]
    }
    """
    try:
        mensaje = request.data.get('mensaje')
        contexto_extra = request.data.get('contexto', {})
        
        if not mensaje:
            return Response(
                {'error': 'El campo mensaje es obligatorio'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Preparar contexto adicional si se proporciona
        contexto = {}
        
        # Si se consulta sobre una venta específica
        if 'venta_numero' in contexto_extra:
            try:
                venta = Venta.objects.get(numero=contexto_extra['venta_numero'])
                detalles = DetalleVenta.objects.filter(venta=venta)
                
                contexto['venta'] = {
                    'numero': venta.numero,
                    'fecha': venta.fecha.strftime('%Y-%m-%d'),
                    'total': float(venta.total),
                    'cliente': f"{venta.rut_cliente.nombre} {venta.rut_cliente.apellido}",
                    'productos': [
                        {
                            'nombre': d.producto.nombre,
                            'cantidad': d.cantidad,
                            'precio': float(d.precio_unitario)
                        }
                        for d in detalles
                    ]
                }
            except Venta.DoesNotExist:
                pass
        
        # Si se consulta sobre un producto específico
        if 'producto_id' in contexto_extra:
            try:
                producto = Productos.objects.get(id=contexto_extra['producto_id'])
                contexto['producto'] = {
                    'nombre': producto.nombre,
                    'codigo': producto.codigo,
                    'precio': float(producto.precio),
                    'stock': producto.stock,
                    'disponible': producto.stock > 0
                }
            except Productos.DoesNotExist:
                pass
        
        # Agregar lista COMPLETA de productos disponibles si no hay contexto específico
        if not contexto:
            # Enviar TODOS los productos disponibles (no solo 5)
            todos_los_productos = Productos.objects.filter(stock__gt=0).order_by('nombre')
            
            logger.info(f"Chatbot - Enviando {todos_los_productos.count()} productos a la IA")
            
            contexto['productos_disponibles'] = [
                {
                    'id': p.id,
                    'nombre': p.nombre,
                    'codigo': p.codigo,
                    'precio': float(p.precio),
                    'stock': p.stock
                }
                for p in todos_los_productos
            ]
            
            contexto['total_productos'] = todos_los_productos.count()
        
        # Llamar a GroqCloud para obtener respuesta del chatbot
        groq = GroqService()
        resultado = groq.chatbot_atencion(
            mensaje_usuario=mensaje,
            contexto=contexto if contexto else None
        )
        
        return Response({
            'respuesta': resultado.get('respuesta', ''),
            'tipo': resultado.get('tipo', 'otro'),
            'requiere_humano': resultado.get('requiere_humano', False),
            'sugerencias': resultado.get('sugerencias', [])
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error en chatbot_atencion: {str(e)}")
        return Response(
            {'error': f'Error en el chatbot: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
