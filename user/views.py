from django.contrib.auth.decorators import login_required;
from django.contrib.auth.models import User;
from django.utils.decorators import method_decorator;
from django.views.generic import TemplateView;
from django.contrib.auth import authenticate, login, logout;
from ourjobfund.settings import STRIPE_TEST_SECRET_KEY, STATIC_ROOT;
from annoying.functions import get_object_or_None;
from django.db.models import Q, F;
from django.shortcuts import render, get_object_or_404, redirect;
from django.forms import formset_factory;
from django.http import JsonResponse, HttpResponse, Http404;
from django.core import serializers;
from pay.models import Pay;
from job.models import Job;
from datetime import datetime;
from .models import Profile;
from .forms import ChangePasswordForm, ChangeNameForm, ChangeEmailForm, LoginForm, SignUpForm, DeactivateAccountForm, ProfileForm, ChangeUsernameForm;
import json, stripe;

class LoginView(TemplateView):
    template_name = 'user/login.html';
    login_form = LoginForm;
    sign_up_form = SignUpForm;
    
    def get(self, request, *args, **kwargs):
        if (request.user.is_authenticated()):
            return redirect('home');
        else:
            return render(request, self.template_name, self.get_context_data(login_form=self.login_form, sign_up_form=self.sign_up_form));
    
    def post(self, request, *args, **kwargs):
        login_form = self.login_form;
        sign_up_form = self.sign_up_form;
        if ('sign-in' in request.POST):
            login_form = LoginForm(request.POST);
            if (login_form.is_valid()):
                user = get_object_or_None(User, email=login_form.cleaned_data['username_or_password']);
                if (user is None):
                    user = get_object_or_None(User, username=login_form.cleaned_data['username_or_password']);
                user.is_active = True;
                login(request, user);
                return redirect('home');
        elif ('sign-up' in request.POST):
            sign_up_form = SignUpForm(request.POST);
            if (sign_up_form.is_valid()):
                user = sign_up_form.save(commit=False);
                user.email = sign_up_form.cleaned_data['email'];
                user.username = sign_up_form.cleaned_data['username'];
                password = sign_up_form.cleaned_data['password'];
                user.set_password(password);
                user.save();
                user = authenticate(username=user.username, password=password);
                if (user is not None):
                    login(request, user);
                    return redirect('user:login');
        return render(request, self.template_name, self.get_context_data(login_form=login_form, sign_up_form=sign_up_form));
        
    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs);
        context['login_form'] = kwargs['login_form'];
        context['sign_up_form'] = kwargs['sign_up_form'];
        return context;

@login_required
def sign_out(request):
    logout(request);
    return redirect('user:login');

class SearchUsersView(TemplateView):
    template_name = 'user/search.html';
    
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        search = request.GET['search-users'];
        context = {
            'users' : self.getUsersFromQuery(search, 0),
            'search' : search,
            'total' : self.getTotalNumberOfUsersFromQuery(search),
        };
        return render(request, self.template_name, context);
    
    def getUsersFromQuery(self, search, num_searches):
        users = User.objects.all();
        for word in search.split():
            users = users.filter(Q(username__icontains=word) | Q(first_name__istartswith=word) | Q(last_name__istartswith=word));
            start = (50 * num_searches);
            end = start + 50;
        users = users[start:end];
        return users;
        
    def getTotalNumberOfUsersFromQuery(self, search):
        users = User.objects.all();
        for word in search.split():
            users = users.filter(Q(username__icontains=word) | Q(first_name__istartswith=word) | Q(last_name__istartswith=word));
        return users.count();

@login_required
def see_more_users(request):
    if (request.is_ajax()):
        search = request.GET['search'];
        num_searches = request.GET['num_searches'];
        users = getUsersFromQuery(search, num_searches);
        users = serializers.serialize("json", users);
        return HttpResponse(users, content_type="application/json");
    else:
        return Http404();

class DetailView(TemplateView):
    template_name = 'user/detail.html';
    nameForm = ChangeNameForm;
    profileForm = ProfileForm;
    
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=kwargs['username']);
        nameForm = self.initializeName(user, name_form=self.nameForm);
        profileForm = self.initializeProfile(user, profile_form=self.profileForm);
        return render(request, self.template_name, self.get_context_data(user=user, nameForm=nameForm, profileForm=profileForm));
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        nameForm = self.nameForm;
        profileForm = self.profileForm;
        descriptionForm = self.descriptionForm;
        if ('info' in request.POST):
            nameForm = nameForm(request.POST);
            profileForm = profileForm(request.POST);
            if (nameForm.is_valid() and profileForm.is_valid()):
                request.user.first_name = nameForm.cleaned_data['first_name'];
                request.user.last_name = nameForm.cleaned_data['last_name'];
                request.user.save();
                request.user.profile.city = profileForm.cleaned_data['city'];
                request.user.profile.state = profileForm.cleaned_data['state'];
                request.user.profile.occupation = profileForm.cleaned_data['occupation'];
                request.user.profile.education = profileForm.cleaned_data['education'];
                request.user.profile.contact = profileForm.cleaned_data['contact'];
                request.user.profile.description = descriptionForm.cleaned_data['description'];
                request.user.profile.save();
                return redirect('user:detail', username=request.user.username);
            else:
                descriptionForm = self.initializeDescription(request.user, description_form=descriptionForm);
        elif ('stripeToken' in request.POST):
            self.pay(request, job, jobuser);
            return redirect('user:confirmation', username=get_object_or_404(User, username=kwargs['username']));
        elif ('delete-stripe' in request.POST):
            request.user.profile.stripe_account_id = "";
            request.user.profile.save();
        return render(request, self.template_name, self.get_context_data(user=request.user, nameForm=nameForm, profileForm=profileForm));
        
    def initializeName(self, *args, **kwargs):
        user = args[0];
        return kwargs['name_form'](initial={'first_name' : user.first_name, 'last_name' : user.last_name });
        
    def initializeProfile(self, *args, **kwargs):
        user = args[0];
        return kwargs['profile_form'](initial={
            'city' : user.profile.city, 
            'state' : user.profile.state,
            'occupation' : user.profile.occupation,
            'education' : user.profile.education,
            'contact' : user.profile.contact,
            'description' : user.profile.description,
        });
        
    def get_context_data(self, *args, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs);
        user = kwargs['user'];
        context['detail_user'] = user;
        context['name_form'] = kwargs['nameForm'];
        context['profile_form'] = kwargs['profileForm'];
        context['currently_pledged'] = user.jobuser_set.filter(Q(job__is_finished=False) & Q(pledged__gt=0));
        context['currently_working'] = user.jobuser_set.filter(Q(job__is_finished=False) & (Q(work_status='working') | Q(work_status='finished')));
        context['finished_pledging'] = user.jobuser_set.filter(Q(job__is_finished=True) & Q(pledged__gt=0));
        context['finished_working'] = user.jobuser_set.filter(Q(job__is_finished=True) & (Q(work_status='working') | Q(work_status='finished')));
        return context;
        
class AccountView(TemplateView):
    template_name = 'user/account.html';
    usernameForm = ChangeUsernameForm;
    emailForm = ChangeEmailForm;
    passwordForm = ChangePasswordForm;
    deactivateForm = DeactivateAccountForm;
    
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        usernameForm = '';
        if ((datetime.now() - request.user.profile.last_time_username_was_changed.replace(tzinfo=None)).days >= 180):
            usernameForm = self.usernameForm(initial={'username' : request.user.username});
        emailForm = self.emailForm(initial={'email' : request.user.email});
        passwordForm = self.passwordForm;
        deactivateForm = self.deactivateForm(initial={'is_active' : True});
        return render(request, self.template_name, self.get_context_data(request, usernameForm=usernameForm, emailForm=emailForm, passwordForm=passwordForm, deactivateForm=deactivateForm));
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        usernameForm = self.usernameForm;
        emailForm = self.emailForm;
        passwordForm = self.passwordForm;
        deactivateForm = self.deactivateForm;
        if ('change-username' in request.POST):
            emailForm = usernameForm(request.POST);
            if (usernameForm.is_valid()):
                self.request.user.username = emailForm.cleaned_data['username'];
                self.request.user.save();
                self.request.user.profile.last_time_name_was_changed = datetime.now();
                self.request.user.profile.save();
                return redirect('user:account');
        elif ('change-email' in request.POST):
            emailForm = emailForm(request.POST);
            if (emailForm.is_valid()):
                self.request.user.email = emailForm.cleaned_data['email'];
                self.request.user.save();
                return redirect('user:account');
        elif ('change-password' in request.POST):
            passwordForm = passwordForm(request.POST, user=request.user);
            if (passwordForm.is_valid()):
                self.request.user.set_password(passwordForm.cleaned_data['new_password']);
                self.request.user.save();
                login(self.request, request.user);
                return redirect('user:account');
        elif ('deactivate-account' in request.POST):
            deactivateForm = deactivateForm(request.POST);
            if (deactivateForm.is_valid()):
                self.request.user.is_active = False;
                self.request.user.save();
                return redirect('user:sign_out');
        return render(request, self.template_name, self.get_context_data(request, usernameForm=usernameForm, emailForm=emailForm, passwordForm=passwordForm, deactivateForm=deactivateForm));
        
    def get_context_data(self, request, **kwargs):
        context = super(AccountView, self).get_context_data(**kwargs);
        context['change_username_form'] = kwargs['usernameForm'];
        context['change_email_form'] = kwargs['emailForm'];
        context['change_password_form'] = kwargs['passwordForm'];
        context['deactivate_form'] = kwargs['deactivateForm'];
        return context;
    
@login_required
def stripe(request):
    username = request.GET.get('state', None);
    if (username is not None):
        user = get_object_or_404(User, username=username);
        if (user.username == request.user.username):
            code = request.GET.get('code', None);
            request.user.profile.stripe_account_id = code;
            request.user.profile.save();
            return redirect('user:detail', username=username);
        else:
            Http404();
    else:
        return Http404();
    
    
    
    