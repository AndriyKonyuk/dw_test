from django import template

register = template.Library()

@register.filter(name='key')
def key(d, key_name):
    return d[key_name]

@register.filter(name='divis')
def division(first_numer, second_number):
    return first_numer/second_number