
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.core.mail import EmailMessage, EmailMultiAlternatives
# Create your views here.
from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, UserLoginForm, UserRegisterForm
from allauth.account.views import LoginView, LogoutView, SignupView
from allauth.account.views import _ajax_response
from django.urls import reverse, reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from . import app_settings
from allauth.account.adapter import get_adapter, DefaultAccountAdapter
from django.views.generic import UpdateView, CreateView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.files import File
import os
from pathlib import Path

from allauth.account.utils import (
    complete_signup,
    get_login_redirect_url,
    get_next_redirect_url,
    logout_on_password_change,
    passthrough_next_redirect_url,
    perform_login,
    sync_user_email_addresses,
    url_str_to_user_pk,
)
from .tokens import account_activation_token

import glob
from django.conf import settings

def activate(request, uidb64, token):
    try:
        # https://stackoverflow.com/questions/70382084/import-error-force-text-from-django-utils-encoding
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        # login(request, user)
        return redirect('users_login')
        # return redirect('home')
        # return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')
def send_emails(request,email_template,message):
    html_body = render_to_string(email_template, message)
    # html_body = get_template("assessment/templates/template_email_test_invitation.html",merge_data).render()

    message = EmailMultiAlternatives(
        subject='Confirm email',
        body="mail testing",
        from_email=settings.EMAIL_HOST_USER,
        to=[request.POST['email']]
    )
    message.attach_alternative(html_body, "text/html")
    message.send(fail_silently=False)
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)

            email_template = 'users/account_signup_confirmation_email.html'
            message =  {
                'user': mark_safe(str(user.email)),
                'domain': mark_safe(str(current_site.domain)),
                'uid': mark_safe(str(urlsafe_base64_encode(force_bytes(user.pk)))),
                # # 'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': mark_safe(str(account_activation_token.make_token(user))),
            }

            send_emails(request,email_template,message)

            messages.success(request, f'Account created for {user.email}!')
            return redirect('users_login')

    else: # get
        form = UserRegisterForm()
        return render(request, 'users/signup.html', {'form': form})
    messages.success(request, 'wrong email/password')
    return redirect('users_signup')

class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = "users/login.html"
    success_url = reverse_lazy('users_profile')  # Redirect to the user's profile page

    def get_success_url(self):
        # Construct the profile URL with the user's primary key
        profile_url = reverse_lazy('users_profile', kwargs={'pk': self.request.user.pk})
        return profile_url

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        # Add any additional context data if needed
        return ret

@method_decorator(login_required, name='dispatch')
class UserLogoutView(LogoutView):
        template_name = "users/logout.html"

        def get(self, *args, **kwargs):
            if app_settings.LOGOUT_ON_GET:
                return self.post(*args, **kwargs)
            if not self.request.user.is_authenticated:
                response = redirect(self.get_redirect_url())
                return _ajax_response(self.request, response)
            if self.request.user.is_authenticated:
                self.logout()
            ctx = self.get_context_data()
            response = self.render_to_response(ctx)
            return _ajax_response(self.request, response)

        def post(self, *args, **kwargs):
            url = self.get_redirect_url()
            if self.request.user.is_authenticated:
                self.logout()
            response = redirect(url)
            return _ajax_response(self.request, response)

        def get_redirect_url(self):
            return (
                    get_next_redirect_url(
                        self.request,
                        self.redirect_field_name) or get_adapter(
                self.request).get_logout_redirect_url(
                self.request))

class UserSignupOkView(SignupView):
    form_class = UserRegisterForm
    template_name = "users/emailconfirmationsent.html"
    # success_url = reverse_lazy('users_login')

@method_decorator(login_required, name='dispatch')
class UserProfileView(UpdateView):
    template_name = 'users/profile.html'
    # form_class = ProfileUpdateForm

    def get(self, request, *args, **kwargs):
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

        context = {
            'u_form': u_form,
            'p_form': p_form
        }

        return render(request, 'users/profile.html', context)

    def post(self, request, *args, **kwargs):
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Account update successfully!')
        return HttpResponseRedirect(reverse('users_profile', kwargs={'pk': kwargs['pk']}))


@method_decorator(login_required, name='dispatch')
class UserProfileChangePictureView(UpdateView):
    template_name = 'users/profile_change_picture.html'
    # form_class = ProfileUpdateForm
    context_object_name = 'profilechangeview'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def get(self, request, *args, **kwargs):

        rdir = os.path.join(settings.MEDIA_ROOT,"profile_pics/gallery") # needed in production
        files = os.listdir(rdir)
        files_path = [os.path.join("grouping/media/profile_pics/gallery",fil) for fil in files]
        mylist = ['/'+f for f in files_path]
        # # context = self.get_context_data(**kwargs)
        context = {'mylist': mylist}

        # print('glob.glob:')
        # print(glob.glob("users/media/profile_pics/gallery/*.*"))
        print('mylist:')
        # print(mylist)
        return render(request, 'users/profile_change_picture.html', context)

    def post(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs['pk'])
        if len(request.FILES)!=0:
        # u_form = UserUpdateForm(request.POST, instance=request.user)
            user.profile.image = request.FILES['file']
            user.profile.save()
            # p_form = ProfileUpdateForm(request.POST,
            #                            request.FILES,
            #                            instance=request.user.profile)
            #
            # if p_form.is_valid():
            #     p_form.save()
            #     messages.success(request, f'Account update successfully!')
        else:

            pre_path = os.getcwd()
            path_suf = request.POST['selected'].split('/grouping')[1]

            if 'users_management' in pre_path:
                new_path = Path(pre_path + '/grouping' + path_suf)
            else:
                new_path = Path(pre_path + '/users_management/grouping' + path_suf)

            image_url = new_path
            initial_path = user.profile.image.name

            # https: // stackoverflow.com / questions / 1308386 / programmatically - saving - image - to - django - imagefield
            # result = urllib.urlretrieve(image_url)

            user.profile.image.save(
                os.path.basename(new_path),
                File(open(image_url, 'rb'))
            )

            user.profile.save()



            # with new_path.open(mode='r') as f:
            #     ...
            #     new_image = File(f, name=new_path.name)
            # user.profile.image = new_image
            # user.profile.image = Image.open(new_path)
            # https: // docs.djangoproject.com / en / 4.0 / topics / files /
            # https: // stackoverflow.com / questions / 67702770 / unidentifiedimageerror - at - login - cannot - identify - image - file - c - users - sudha
            # user.save()
            # user.profile.save()
            # os.rename(initial_path, new_path)new_path
            # user.profile.image  = models.ImageField(default=full_path)




            # return redirect('users_profile')

        return HttpResponseRedirect(reverse('users_profile', kwargs={'pk': kwargs['pk']}))

@method_decorator(login_required, name='dispatch')
class UserChangePasswordView(PasswordChangeView):
    from_class = PasswordChangeForm
    success_url = reverse_lazy('users_login')

    def get(self, request, *args, **kwargs):
        request.session['get_post'] = 'get'
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.session['get_post'] == 'post':
            if context['form'].is_valid():
                context['password_change'] = 'success'
            else:
                context['password_change'] = 'try again, there were some errors'

        elif self.request.session['get_post'] == 'get':
            context['password_change'] = ''
        return context
    def post(self, request, *args, **kwargs):
        request.session['get_post'] = 'post'
        return super().post(request, *args, **kwargs)

