from pytz import timezone
from datetime import datetime, timedelta
from .models import PageView, PageHit
import re


def capture_hit(request):
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key
    client_ip = get_client_ip(request)
    page_address = get_page_address(request)
    last_slash = [m.start() for m in re.finditer('/', page_address)]
    page_object, page_created = PageView.objects.get_or_create(page=page_address,
                                                               page_category=page_address[:last_slash[-2] + 1],
                                                               page_identifier=page_address[last_slash[-2] +
                                                                                            1: len(page_address) - 1])

    hits = PageHit.objects.filter(date__range=[datetime.now(tz=timezone('US/Eastern')) - timedelta(minutes=5),
                                               datetime.now(tz=timezone('US/Eastern'))]).filter(page__page=page_address)

    if (page_created
        or
        (client_ip not in request.session and request.path not in request.session and 'last_hit' not in request.session)
            or
            (datetime.strptime(request.session['last_hit'], '%y-%m-%d-%H-%M-%S-%f')
             <= datetime.now() - timedelta(minutes=5))
            or
            not hits):
        set_page_hit(page_object, client_ip, request, session_key)


def set_page_hit(page_obj, client_ip, request, s_key):
    hit = PageHit(page=page_obj, ip=client_ip, visitor=request.user,
                  session=s_key, date=datetime.now(tz=timezone('US/Eastern')))
    hit.save()
    page_obj.increment_page_views()
    request.session[client_ip] = client_ip
    request.session[request.path] = get_page_address(request)
    request.session['last_hit'] = datetime.now().strftime('%y-%m-%d-%H-%M-%S-%f')
    print(request.session['last_hit'])


def get_page_address(request):
    return request.path


def get_client_ip(request):
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        return request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
    else:
        return request.META.get('REMOTE_ADDR')
