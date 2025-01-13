from django import template

register = template.Library()

MONTH_NAMES = {
    1: "Январь", 2: "Февраль", 3: "Март",
    4: "Апрель", 5: "Май", 6: "Июнь",
    7: "Июль", 8: "Август", 9: "Сентябрь",
    10: "Октябрь", 11: "Ноябрь", 12: "Декабрь",
}

@register.filter
def month_name(month_number):
    """Преобразует числовой месяц в его название."""
    try:
        month_int = int(month_number)
        return MONTH_NAMES.get(month_int, str(month_number))
    except (ValueError, TypeError):
        return str(month_number)
