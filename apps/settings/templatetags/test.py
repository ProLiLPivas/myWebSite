from django import template


register = template.Library()



@register.simple_tag
def click():
   print('bla bal bal')
   return '<button type="submit">OK</button>'
