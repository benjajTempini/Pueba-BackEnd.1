# filepath: /c:/Users/sistemas/Documents/GitHub/Pueba-BackEnd.1/clientes/serializers.py
from rest_framework import serializers
from .models import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__' # esto icluye todos los campos