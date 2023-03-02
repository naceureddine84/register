from django import template

register = template.Library()
@register.filter
def pdfPub(value):
    return value.replace(".","_PUB.")