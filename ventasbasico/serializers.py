from rest_framework import serializers
from .models import *
from clientes.models import Cliente
from clientes.serializers import ClienteSerializer
from django.db import transaction
from datetime import datetime, date
import base64
from io import BytesIO
from PIL import Image


class ProductosSerializer(serializers.ModelSerializer):
    """Serializer para productos con soporte de imágenes en base64"""
    foto = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    foto_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Productos
        fields = [
            "id", "nombre", "codigo", "stock", "precio", "foto", "foto_url",
            "descripcion_corta", "descripcion_larga", 
            "palabras_clave", "beneficios", "descripcion_generada_fecha"
        ]
    
    def _detect_image_type(self, image_data):
        """Detecta el tipo de imagen usando Pillow (reemplazo de imghdr para Python 3.13+)"""
        try:
            img = Image.open(BytesIO(image_data))
            format_map = {
                'JPEG': 'jpeg',
                'PNG': 'png',
                'GIF': 'gif',
                'WEBP': 'webp',
                'BMP': 'bmp'
            }
            return format_map.get(img.format, 'jpeg')
        except Exception:
            return 'jpeg'  # Default
    
    def get_foto_url(self, obj):
        """Convierte el BLOB a base64 para enviar al frontend"""
        if obj.foto:
            try:
                # Convertir bytes a base64
                base64_image = base64.b64encode(obj.foto).decode('utf-8')
                # Detectar tipo de imagen usando Pillow
                image_type = self._detect_image_type(obj.foto)
                return f"data:image/{image_type};base64,{base64_image}"
            except Exception:
                return None
        return None
    
    def validate_foto(self, value):
        """Valida y convierte imagen base64 a bytes"""
        if not value:
            return None
        
        try:
            # Si viene como base64 con prefijo data:image
            if isinstance(value, str) and value.startswith('data:image'):
                # Extraer el base64 puro
                header, base64_data = value.split(',', 1)
                image_data = base64.b64decode(base64_data)
            elif isinstance(value, str):
                # Si viene solo el base64
                image_data = base64.b64decode(value)
            elif isinstance(value, bytes):
                # Si ya viene como bytes
                image_data = value
            else:
                raise serializers.ValidationError("Formato de imagen inválido")
            
            # Validar que sea una imagen válida usando Pillow
            try:
                img = Image.open(BytesIO(image_data))
                img.verify()  # Verifica que sea una imagen válida
                
                # Validar formato
                allowed_formats = ['JPEG', 'JPG', 'PNG', 'GIF', 'WEBP', 'BMP']
                if img.format.upper() not in allowed_formats:
                    raise serializers.ValidationError(
                        f"Formato {img.format} no permitido. Usa: {', '.join(allowed_formats)}"
                    )
                
                # Validar tamaño (max 5MB)
                max_size = 5 * 1024 * 1024  # 5MB en bytes
                if len(image_data) > max_size:
                    raise serializers.ValidationError(
                        f"Imagen muy grande. Máximo 5MB, recibido: {len(image_data) / 1024 / 1024:.2f}MB"
                    )
                
            except Exception as e:
                raise serializers.ValidationError(f"Imagen corrupta o inválida: {str(e)}")
            
            return image_data
            
        except base64.binascii.Error:
            raise serializers.ValidationError("Base64 inválido")
        except Exception as e:
            raise serializers.ValidationError(f"Error procesando imagen: {str(e)}")
    
    def to_representation(self, instance):
        """Personalizar la salida para incluir foto como base64"""
        representation = super().to_representation(instance)
        # La foto ya se convierte automáticamente con get_foto_url
        # Remover el campo foto (bytes) y dejar solo foto_url
        representation.pop('foto', None)
        return representation

class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_detalle = ProductosSerializer(source='producto', read_only=True)
    producto = serializers.PrimaryKeyRelatedField(
        queryset=Productos.objects.all(),
        write_only=True
    )
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = DetalleVenta
        fields = ["id", "venta", "producto", "producto_detalle", "cantidad", "precio_unitario", "subtotal"]
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['producto'] = representation.pop('producto_detalle')
        return representation

class DetalleVentaItemSerializer(serializers.Serializer):
    """Serializador para items dentro de una venta (solo para escritura)"""
    producto_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1)
    precio_unitario = serializers.DecimalField(max_digits=10, decimal_places=2)

class VentaSerializer(serializers.ModelSerializer):
    # Para lectura: mostrar todos los datos del cliente
    rut_cliente_detalle = ClienteSerializer(source='rut_cliente', read_only=True)
    # Para escritura: recibir solo el RUT del cliente
    rut_cliente = serializers.CharField(write_only=True)
    # Para escritura: recibir la lista de productos
    detalles = DetalleVentaItemSerializer(many=True, write_only=True)
    # Para lectura: mostrar los detalles completos
    detalles_venta = DetalleVentaSerializer(source='detalles', many=True, read_only=True)
    
    class Meta:
        model = Venta
        fields = ["id", "numero", "fecha", "rut_cliente", "rut_cliente_detalle", "total", "detalles", "detalles_venta"]
        read_only_fields = ["fecha", "total"]  # Total se calcula automáticamente
    
    def create(self, validated_data):
        # Extraer datos
        rut_cliente = validated_data.pop('rut_cliente')
        detalles_data = validated_data.pop('detalles')
        # Remover total si viene desde Angular (se calculará automáticamente)
        validated_data.pop('total', None)
        
        # Validar que hay detalles
        if not detalles_data:
            raise serializers.ValidationError({
                'detalles': 'Debe incluir al menos un producto en la venta.'
            })
        
        # Buscar el cliente
        try:
            cliente = Cliente.objects.get(rut=rut_cliente)
        except Cliente.DoesNotExist:
            raise serializers.ValidationError({
                'rut_cliente': f'Cliente con RUT {rut_cliente} no existe. Por favor regístrelo primero.'
            })
        
        # Usar transacción para garantizar consistencia
        with transaction.atomic():
            # Generar número de venta si no se proporciona
            if 'numero' not in validated_data or not validated_data['numero']:
                fecha_actual = datetime.now()
                prefijo = fecha_actual.strftime("%Y%m%d")
                ventas_hoy = Venta.objects.filter(fecha=date.today()).count()
                validated_data['numero'] = f"{prefijo}-{ventas_hoy + 1:04d}"
            
            # Verificar stock y calcular total
            total_calculado = 0
            productos_verificados = []
            
            for detalle in detalles_data:
                try:
                    producto = Productos.objects.select_for_update().get(id=detalle['producto_id'])
                except Productos.DoesNotExist:
                    raise serializers.ValidationError({
                        'detalles': f'Producto con ID {detalle["producto_id"]} no existe.'
                    })
                
                # Verificar stock
                if producto.stock < detalle['cantidad']:
                    raise serializers.ValidationError({
                        'detalles': f'Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}, Solicitado: {detalle["cantidad"]}'
                    })
                
                productos_verificados.append({
                    'producto': producto,
                    'cantidad': detalle['cantidad'],
                    'precio_unitario': detalle['precio_unitario']
                })
                
                total_calculado += detalle['precio_unitario'] * detalle['cantidad']
            
            # Crear la venta
            venta = Venta.objects.create(
                rut_cliente=cliente,
                total=total_calculado,  # Usar el total calculado
                **validated_data
            )
            
            # Crear los detalles de venta y reducir stock
            for item in productos_verificados:
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=item['producto'],
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio_unitario']
                )
                
                # Reducir stock
                item['producto'].stock -= item['cantidad']
                item['producto'].save()
            
            return venta
    
    def to_representation(self, instance):
        # Personalizar la respuesta
        representation = super().to_representation(instance)
        # Mover los datos del cliente al campo principal
        representation['rut_cliente'] = representation.pop('rut_cliente_detalle')
        # Renombrar detalles_venta a detalles
        representation['detalles'] = representation.pop('detalles_venta')
        return representation

# Se eliminaron UserSerializer y GroupSerializer de este archivo


