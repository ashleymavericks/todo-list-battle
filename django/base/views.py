from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Task

# Create your views here.
class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    field = '__all__'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('tasks')

    
# Inheriting from ListView, now we have all the functionality of ListView -> returns back a template with queryset of data
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
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'
    
    
# CreateViewList gives us a model form to work with, which are basically a class representation of a form based on a model
class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    # fields = '__all__' -> no longer need user
    fields = ['title','description','complete']
    success_url = reverse_lazy('tasks')
    
    def form_valid(self, form):
        # make sure that the user is logged in user
        form.instance.user = self.request.user
        # allows the parent class to complete the form submission process and redirect the user to the success URL
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