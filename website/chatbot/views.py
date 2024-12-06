from django.shortcuts import render
from django.http import HttpResponse


def start(request):
    return render(request, 'chatbot/start.html')

def test(request):
    return HttpResponse('Тестовая страница')

def chatbot(request):
    return render(request, 'chatbot/chatbot.html')
# Create your views here.
