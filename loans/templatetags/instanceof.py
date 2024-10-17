from django import template

register = template.Library()

@register.filter(name='instanceof')
def isinstanceof(value, class_name):
    try:
        return value.__class__.__name__ == class_name.split('.')[-1]
    except AttributeError:
        return False
