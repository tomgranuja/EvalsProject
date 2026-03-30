from django import template

register = template.Library()

@register.filter
def year_month_id(date):
    return f'y{date.year}-m{date.month}-month-id'
