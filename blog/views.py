from django.views.generic import (
    ListView, DetailView, CreateView,
    UpdateView, DeleteView, ArchiveIndexView,
    YearArchiveView,
)
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post
from .forms import PostForm


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'  #<app>/<model>_<viewtype>.html   <-- what django looks for by default
    context_object_name = 'posts'
    ordering = ['-date_posted']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)

        context['featured_article'] = Post.objects.filter(featured=True)
        context['secondary_article'] = Post.objects.exclude(featured=True).order_by("-date_posted")[1:4]
        return context

    def retrieve_first_post(self):
        return Post.objects.last()

    def retrieve_all_other_posts(self):
        latest_date = Post.objects.last().date_posted
        return Post.objects.exclude(featured=True)


class PostArchiveView(ArchiveIndexView):
    model = Post
    date_field = 'date_posted'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['date_list'] = self.date_list
        return context


class PostYearArchiveView(YearArchiveView):
    model = Post
    queryset = Post.objects.all()
    date_field = 'date_posted'
    make_object_list = True
    context_object_name = 'context'
    allow_empty = True
    allow_future = True

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['date_list'] = self.date_list
        context['year'] = self.get_year()
        return context


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        #self.change_featured()
        return super().form_valid(form)

    def change_featured(self):
        for post in self.model.objects.all():
            post.featured = False
            post.save()


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            self.update_featured()
            return True
        return False

    def update_featured(self):
        penultimate_post = self.model.objects.order_by('-date_posted')[1]
        penultimate_post.featured = True
        penultimate_post.save()


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'blog/about.html', {'title': 'about'})
