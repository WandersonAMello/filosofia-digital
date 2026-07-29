from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "core"

urlpatterns = [
    # ------------------------------------------------------------------
    # Views Públicas
    # ------------------------------------------------------------------
    path("", views.PostListView.as_view(), name="post_list"),
    path("categoria/<slug:category_slug>/", views.PostListView.as_view(), name="post_list_by_category"),
    path("busca/", views.PostListView.as_view(), name="post_search"),
    path("post/<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),

    # ------------------------------------------------------------------
    # Autenticação
    # ------------------------------------------------------------------
    path("autor/login/", views.StaffLoginView.as_view(), name="login"),
    path("autor/logout/", views.StaffLogoutView.as_view(), name="logout"),

    # ------------------------------------------------------------------
    # Painel — Posts
    # ------------------------------------------------------------------
    path("painel/", views.PainelDashboardView.as_view(), name="painel_dashboard"),
    path("painel/novo/", views.PostCreateView.as_view(), name="painel_post_criar"),
    path("painel/<slug:slug>/editar/", views.PostUpdateView.as_view(), name="painel_post_editar"),
    path("painel/<slug:slug>/deletar/", views.PostDeleteView.as_view(), name="painel_post_deletar"),

    # ------------------------------------------------------------------
    # Painel — Categorias
    # ------------------------------------------------------------------
    path("painel/categorias/", views.CategoryListView.as_view(), name="painel_category_list"),
    path("painel/categorias/nova/", views.CategoryCreateView.as_view(), name="painel_category_criar"),
    path("painel/categorias/<int:pk>/editar/", views.CategoryUpdateView.as_view(), name="painel_category_editar"),
    path("painel/categorias/<int:pk>/deletar/", views.CategoryDeleteView.as_view(), name="painel_category_deletar"),
]
