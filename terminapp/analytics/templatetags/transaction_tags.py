from django import template

register = template.Library()

@register.filter
def display_transaction_type(operation_type):
    if operation_type in ['income', 'technical_income']:
        return 'Доход'
    elif operation_type in ['expense', 'technical_expense']:
        return 'Расход'
    return 'Неизвестно'
