from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('categoria/<slug:category_slug>/', views.PostListView.as_view(), name='post_list_by_category'),
    path('busca/', views.PostListView.as_view(), name='post_search'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
]
