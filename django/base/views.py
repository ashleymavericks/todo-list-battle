from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Task


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    field = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')


class RegisterPageView(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    # redirected_authenticated_user = True -> not working
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        # get the user -> once the form is saved, return value will be user
        user = form.save()
        # if the user is successfully created -> use the login function to automatically login the user
        if user:
            login(self.request, user)
        return super(RegisterPageView, self).form_valid(form)

    # def redirect_authenticated_user(request):
    #     return redirect('tasks')

    # overriding since redirected_authenticated_user attribute not working
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        # any other situation just continue on with default action
        return super(RegisterPageView, self).get(*args, **kwargs)


# Inheriting from ListView, now we have all the functionality of ListView -> retrieving a queryset of data from the specified model and passing it to a template for display.
class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    # Alternatively, if you want only user specific data in the template, can simply override get_query_set inside TaskListView
    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     return qs.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search_area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__startswith=search_input)
            
        context['search_input'] = search_input
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'


# CreateViewList gives us a model form to work with, which are basically a class representation of a form based on a model
class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    # fields = '__all__' -> no longer need user
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        # make sure that the user is logged in user
        form.instance.user = self.request.user
        # super() allows the parent class to complete the form submission process and redirect the user to the success URL
        return super(TaskCreateView, self).form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    # fields = '__all__' -> no longer need user
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
