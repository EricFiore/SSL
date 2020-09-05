from django import template
from library.models import OptionType, ProductModel, OptionBelongsToModel, Option

register = template.Library()


@register.filter(name='count_types')
def count_types(value, model_num):
    category_count = Option.objects.filter(model_id=model_num, option_type=value).count()
    return category_count


@register.filter(name='reverse_query')
def reverse_query(value, option_model_num):
    model_options = Option.objects.filter(model_id=value)
    for option in model_options:
        if option.option_model_number == option_model_num:
            return Option.objects.filter(parent_option=option.option_id)
