
from django.http import HttpResponseForbidden
from functools import wraps


def group_required(nome_grupo):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            nome_com_prefixo = f"DJANGO_{nome_grupo}"
            if not request.user.groups.filter(name=nome_com_prefixo).exists():
                return HttpResponseForbidden("Acesso negado.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator