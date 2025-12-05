from django.contrib import admin
from django.urls import include, path
from ventasbasico import views
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static


router = routers.DefaultRouter()
router.register(r"productos", views.ProductosViewSet)
router.register(r"venta", views.VentaViewsSet)
router.register(r"detalleVenta", views.DetalleVentaViewSet)

urlpatterns = [
    
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),

    # ============================================
    # ENDPOINTS CON IA - GROQ CLOUD
    # ============================================
    # Estadísticas de IA (debugging)
    path('api/ia/stats/', views.stats_ia, name='stats_ia'),
    
    # Recomendador de productos inteligente
    path('api/ia/productos/recomendar/', views.recomendar_productos_ia, name='recomendar_productos_ia'),
    
    # Generador de descripciones de productos
    path('api/ia/productos/<int:producto_id>/generar-descripcion/', views.generar_descripcion_ia, name='generar_descripcion_ia'),
    
    # Chatbot de atención al cliente
    path('api/ia/chat/', views.chatbot_atencion, name='chatbot_atencion'),

    #Vista admin y Home
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    
    #Rutas para el CRUD de productos
    path('registro/', views.registro, name='registro'),
    path('editar/<int:pk>', views.editar, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar, name='eliminar'),

    # Rutas para el carrito de compras
    path('agregar-carrito/', views.agregar_carrito, name='agregar_carrito'),
    path('ver-carrito/', views.ver_carrito, name='ver_carrito'),
    path('eliminar-del-carrito/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    
    # URL para realizar ventas
    path('venta/', views.venta, name='venta'),
    
    # URLs para historial de ventas
    path('historial/', views.historial_ventas, name='historial_ventas'),
    path('detalle-venta/<int:venta_id>/', views.detalle_venta, name='detalle_venta'),
    
    # URLs para clientes - incluir todas las URLs de la app clientes
    path('clientes/', include('clientes.urls')),

    # Rutas JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Servir archivos multimedia en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
