from django.db.models import Q


def create_tech_tip_query(models, errors):
    model_query = Q()
    error_query = Q()

    if models:
        for model in models:
            model_query = model_query | Q(model_id__model_number__icontains=model)

    if errors:
        for error in errors:
            error_query = error_query | Q(repairs_error__error_name=error)

    return model_query, error_query


def create_tech_tip_error_query(models):
    if models is None:
        raise TypeError

    query = Q()
    for model in models:
        query = query | Q(techtipfix__model_id__model_number__icontains=model)

    return query


def create_man_fix_query(models, errors):
    model_query = Q()
    error_query = Q()

    for model in models:
        model_query = model_query | Q(model_id__model_number__icontains=model)

    for error in errors:
        error_query = error_query | Q(repairs_error__error_name__icontains=error)

    return model_query, error_query
