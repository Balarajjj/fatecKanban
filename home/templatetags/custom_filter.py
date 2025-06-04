# home/templatetags/custom_filters.py

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
# This custom filter allows you to access dictionary items in templates using the syntax {{ dictionary|get_item:key }}+