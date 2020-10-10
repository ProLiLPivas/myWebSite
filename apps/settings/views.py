from django.shortcuts import render

# Create your views here.
# from django.template.defaulttags import register
from django import template


def settings (request):
   return render(request, 'settings/test.html')


register = template.Library()


@register.simple_tag
def click():
   print('bla bal bal')
   return 0
