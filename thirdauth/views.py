# Create your views here.
import json

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from rest_framework import status


def home(request):
    context = RequestContext(request,
                             {'request': request,
                              'user': request.user})
    return render_to_response('thirdauth/home.html',
                              context_instance=context)


