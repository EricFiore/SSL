from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin, FormView, DeleteView, CreateView
from django.views.generic import ListView
from django.views import View
from resolutions.views import ResolutionsResultsView
from users.models import Profile
from resolutions.forms import MainSearch
from .models import Message
from .forms import CommunicationForm


class MessageSend(LoginRequiredMixin, SingleObjectMixin, FormView):
    model = Message
    template_name = 'communications/message_list.html'
    form_class = CommunicationForm

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = User.objects.get(username=self.request.user)
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('message-list')


class MessageView(View):

    def get(self, request, *args, **kwargs):
        view = MessageListView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = MessageSend.as_view()
        return view(request, *args, **kwargs)


class MessageListView(LoginRequiredMixin, FormMixin, ListView):
    model = Message
    form_class = MainSearch
    paginate_by = 5
    context_object_name = 'user_messages'

    def get_queryset(self):
        user_message = Message.objects.filter(send_to=self.request.user).order_by('-date') \
            if self.request.user.id else {}
        return user_message

    def get(self, request, *args, **kwargs):
        if request.GET.get('search'):
            view = ResolutionsResultsView.as_view()
            return view(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['user'] = Profile.objects.get(user=self.request.user) if self.request.user.id else {}
        context['new_message_form'] = CommunicationForm()
        return context


class MessageDeleteView(LoginRequiredMixin, UserPassesTestMixin, FormMixin, DeleteView):
    model = Message
    form_class = MainSearch
    context_object_name = 'message'
    template_name_suffix = '_delete_form'

    def get(self, request, *args, **kwargs):
        if request.GET.get('search'):
            view = ResolutionsResultsView.as_view()
            return view(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def test_func(self):
        if self.get_object().send_to != self.request.user:
            return False
        return True

    def get_success_url(self):
        return reverse('message-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Profile.objects.get(user=self.request.user) if self.request.user.id else {}
        return context
