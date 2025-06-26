from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from .forms import EditProfileForm, ChangePasswordForm
from .models import Profile
from sohome.views import home
import base64


def login_user(request):
    if request.method == 'POST':
        usuario = request.POST.get('username')
        senha = request.POST.get('password')
        user = authenticate(request, username=usuario, password=senha)
        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next') or home)
        else:
            messages.warning(request, "⚠️ Usuário ou senha incorreto !")
            return redirect('login')
    else:
        return render(request, 'login.html') 


@login_required
def logout_user(request):
    logout(request)
    return redirect('login')


def register_user(request):
    if request.method == 'POST':
        nome = request.POST.get('first_name')
        sobrenome = request.POST.get('last_name')
        e_mail = request.POST.get('email')
        usuario = request.POST.get('username')
        senha = request.POST.get('password')

        if not all([nome, sobrenome, e_mail, usuario, senha]):
            messages.warning(request, "⚠️ Todos os campos são obrigatórios!")
            return redirect('register')

        if User.objects.filter(username=usuario).exists():
            messages.warning(request, "⚠️ Este usuário já existe!")
            return redirect('register')

        if User.objects.filter(email=e_mail).exists():
            messages.warning(request, "⚠️ Este e-mail já está cadastrado!")
            return redirect('register')

        user = User.objects.create_user(first_name=nome, last_name=sobrenome, email=e_mail, username=usuario, password=senha)
        group  = Group.objects.get_or_create(name='DJANGO_CLIENTE')[0]
        user.groups.add(group)
        user = authenticate(request, username=usuario, password=senha)
        login(request, user)
        messages.success(request, "✅ Usuário cadastrado com sucesso!")
        return redirect('login') 

    return render(request, 'register.html')


@login_required()
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            
            arquivo = request.FILES.get('foto')
            if arquivo:
                base64_string = base64.b64encode(arquivo.read()).decode('utf-8')
                profile, created = Profile.objects.get_or_create(user=request.user)
                profile.foto_base64 = base64_string
                profile.save()

            messages.success(request, "Profile Updated Successfully")
            return redirect(home)
    else:
        form = EditProfileForm(instance=request.user)

    context = {'form': form}
    return render(request, 'edit_profile.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password Changed Successfully")
            return redirect(home)
    else:
        form = ChangePasswordForm(user=request.user)
        print(form)
    context = {
        'form': form,
    }
    return render(request, 'change_password.html', context)


@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        logout(request)  
        messages.success(request, "Sua conta foi excluída com sucesso.")
        return redirect('login')
    else: return render(request, 'delete_account.html')
