from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView, 
    UpdateView, 
    DeleteView, 
)

from .models import Post, Status
from datetime import datetime

from django.urls import reverse_lazy
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin
)


class PostListView(ListView):
    template_name = "posts/list.html"
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        published_status = Status.objects.get(name="published")
        context["post_list"] = (
            Post.objects
            .filter(status=published_status)
            .order_by("created_on").reverse()
        )
        context ["title"] = "Published"
        return context

class DraftPostListView(LoginRequiredMixin, ListView):
    template_name = "posts/list.html"
    model = Post 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        draft_status = Status.objects.get(name="draft")
        context["post_list"] = (
            Post.objects
            .filter(status=draft_status)
            .filter(author=self.request.user)
            .order_by("created_on").reverse()
        )
        context ["title"] = "Draft"
        return context

class ArchiveView(LoginRequiredMixin, ListView):
    template_name = "posts/archive.html"
    model = Post
    context_object_name = "posts"

    def get_queryset(self):
        year = self.kwargs.get("year")
        month = self.kwargs.get("month")

        if year and month:
            return Post.objects.filter(
                published_date__year=year, 
                published_date__month=month
            )
        elif year: 
            return Post.objects.filter(published_date__year=year)
        else: 
            return Post.objects.none()

class PostDetailView(UserPassesTestMixin, DetailView):
    template_name = "posts/detail.html"
    model = Post

    def test_func(self):
        post = self.get_object()
        if post.status.name =="published":
            return True
        elif post.status.name == "archived" and self.request.user.is_authenticated:
            return True
        elif (post.status.name == "draft"
                and self.request.user.is_authenticated
                and self.request.user == post.author):
            return True
        else: 
            return False

class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = "posts/new.html"
    model = Post
    fields = [
        "title", "subtitle", "body", 
        "author", "status"
    ]

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = "posts/edit.html"
    model = Post
    fields = [
        "title", "subtitle", "body", "status"
    ]

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = "posts/delete.html"
    model = Post
    success_url = reverse_lazy("list")

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user
    

class PostArchivedView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = "posts/archived.html"
    model = Post
    success_url = reverse_lazy("list")
    
    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user
