def create_firmware_query(dates, families, types):
    import datetime
    from library.models import Firmware
    from django.db.models import Min
    from django.db.models import Q

    type_query = Q()
    family_query = Q()

    if types:
        type_query = Q(firmware_type__type=types[0])
        for t in range(1, len(types)):
            type_query = type_query | Q(firmware_type__type=types[t])

    if families:
        family_query = Q(model_id__family_id__family_name=families[0])
        for f in range(1, len(families)):
            family_query = family_query | Q(model_id__family_id__family_name=families[f])

    if dates[0] == '':
        dates[0] = list(Firmware.objects.aggregate(Min('release_date')).values())[0].strftime('%Y-%m-%d')
    if dates[1] == '':
        dates[1] = datetime.date.today().strftime('%Y-%m-%d')

    return dates, family_query, type_query
