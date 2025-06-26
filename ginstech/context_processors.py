
def grupos_do_usuario(request):
    if request.user.is_authenticated:
        grupos_raw = request.user.groups.values_list('name', flat=True)
        grupos = [nome.replace("DJANGO_", "") for nome in grupos_raw]
    else:
        grupos = []
    return {'grupos_usuario': grupos}