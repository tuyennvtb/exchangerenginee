import logging


from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    # test Service Provider
    return HttpResponse("OK")