from django.shortcuts import render

def home(request):
    return render(request, 'venta/home.html')