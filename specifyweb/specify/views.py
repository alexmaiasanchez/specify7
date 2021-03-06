import mimetypes
from functools import wraps

from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control
from django.conf import settings
from django import http

from .specify_jar import specify_jar
from . import api, models

if settings.ANONYMOUS_USER:
    login_maybe_required = lambda func: func
else:
    def login_maybe_required(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated():
                return http.HttpResponseForbidden()
            return view(request, *args, **kwargs)
        return wrapped

class HttpResponseConflict(http.HttpResponse):
    status_code = 409

def api_view(dispatch_func):
    """Create a Django view function that handles exceptions arising
    in the api logic."""
    @login_maybe_required
    @csrf_exempt
    @cache_control(private=True, max_age=2)
    def view(request, *args, **kwargs):
        if request.method != "GET" and (
            settings.RO_MODE or
            request.specify_user.usertype not in ('Manager', 'FullAccess')
        ):
            return http.HttpResponseForbidden()
        try:
            return dispatch_func(request, *args, **kwargs)
        except api.StaleObjectException as e:
            return HttpResponseConflict(e)
        except api.MissingVersionException as e:
            return http.HttpResponseBadRequest(e)
        except http.Http404 as e:
            return http.HttpResponseNotFound(e)
    return view

resource = api_view(api.resource_dispatch)
collection = api_view(api.collection_dispatch)

def raise_error(request):
    raise Exception('This error is a test. You may now return to your regularly '
                    'scheduled hacking.')

@login_maybe_required
@require_GET
def rows(request, model):
    return api.rows(request, model)

@require_GET
@cache_control(max_age=365*24*60*60, public=True)
def images(request, path):
    """A Django view that serves images and icons from the Specify thickclient jar file."""
    mimetype = mimetypes.guess_type(path)[0]
    path = 'edu/ku/brc/specify/images/' + path
    try:
        image = specify_jar.read(path)
    except KeyError as e:
        raise http.Http404(e)
    return http.HttpResponse(image, content_type=mimetype)

@login_maybe_required
@require_GET
@cache_control(max_age=24*60*60, public=True)
def properties(request, name):
    """A Django view that serves .properities files from the thickclient jar file."""
    path = name + '.properties'
    return http.HttpResponse(specify_jar.read(path), content_type='text/plain')

@login_maybe_required
@require_POST
@csrf_exempt
def set_password(request, userid):
    """Set target specify user's password."""
    if not request.specify_user.is_admin():
        return http.HttpResponseForbidden()

    user = models.Specifyuser.objects.get(pk=userid)
    user.set_password(request.POST['password'])
    user.save()
    return http.HttpResponse('', status=204)

@login_maybe_required
@require_POST
@csrf_exempt
def set_admin_status(request, userid):
    if not request.specify_user.is_admin():
        return http.HttpResponseForbidden()

    user = models.Specifyuser.objects.get(pk=userid)
    if request.POST['admin_status'] == 'true':
        user.set_admin()
        return http.HttpResponse('true', content_type='text/plain')
    else:
        user.clear_admin()
        return http.HttpResponse('false', content_type='text/plain')

