from django.urls import path
from . import views
from .views import (
    PostListView, PostDetailView, PostCreateView,
    PostUpdateView, PostDeleteView, PostArchiveView,
    PostYearArchiveView
)


urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('post/archive/', PostArchiveView.as_view(), name='post-archive'),
    path('post/archive/<int:year>/', PostYearArchiveView.as_view(), name='post-year'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.about, name='blog-about')
]
