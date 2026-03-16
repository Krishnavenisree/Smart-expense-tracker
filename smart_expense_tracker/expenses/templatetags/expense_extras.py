from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Allow dict[key] access in templates: {{ mydict|get_item:key }}"""
    return dictionary.get(key, '')
