from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import PostForm, CategoryForm
from .models import Post, Category


# ---------------------------------------------------------------------------
# Mixin de autorização: apenas staff pode acessar o painel
# ---------------------------------------------------------------------------

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Garante que apenas usuários is_staff acessam as views de gestão."""

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseForbidden("Acesso restrito a administradores.")


class AuthorRequiredMixin(StaffRequiredMixin):
    """
    Garante que somente o autor do post pode editá-lo ou deletá-lo.
    Retorna 403 se o usuário é staff mas não é o autor.
    """

    def get_object(self, queryset=None):
        from django.core.exceptions import PermissionDenied
        obj = super().get_object(queryset)
        if obj.author != self.request.user:
            raise PermissionDenied
        return obj


# ---------------------------------------------------------------------------
# Views Públicas
# ---------------------------------------------------------------------------

class PostListView(ListView):
    model = Post
    template_name = "core/index.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.filter(status="published")

        # Filtro por Categoria
        category_slug = self.kwargs.get("category_slug")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Busca Textual
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(summary__icontains=query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["current_category"] = self.kwargs.get("category_slug")
        context["search_query"] = self.request.GET.get("q")
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "core/detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return Post.objects.filter(status="published")


from django.contrib.auth import views as auth_views, logout


# ---------------------------------------------------------------------------
# Views de Autenticação
# ---------------------------------------------------------------------------

class StaffLoginView(auth_views.LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        nome = self.request.user.first_name or self.request.user.username
        messages.success(self.request, f"Bem-vindo(a) de volta, {nome}!")
        return response

    def get_success_url(self):
        return reverse_lazy("core:painel_dashboard")


class StaffLogoutView(auth_views.LogoutView):
    http_method_names = ["get", "post", "options"]
    next_page = reverse_lazy("core:post_list")

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
            messages.info(request, "Sua sessão foi encerrada com sucesso.")
        return redirect(self.next_page)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "Sua sessão foi encerrada com sucesso.")
        return super().post(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Views do Painel (CRUD de Posts)
# ---------------------------------------------------------------------------

class PainelDashboardView(StaffRequiredMixin, ListView):
    template_name = "core/painel/dashboard.html"
    context_object_name = "posts"
    paginate_by = 20

    def get_queryset(self):
        queryset = Post.objects.filter(author=self.request.user).order_by("-created_at")

        # Filtro por Status
        status_filter = self.request.GET.get("status")
        if status_filter in ["published", "draft"]:
            queryset = queryset.filter(status=status_filter)

        # Busca Textual
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(summary__icontains=query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = Post.objects.filter(author=self.request.user)
        context["total_publicados"] = qs.filter(status="published").count()
        context["total_rascunhos"] = qs.filter(status="draft").count()
        context["categories"] = Category.objects.all()
        context["current_status"] = self.request.GET.get("status", "all")
        context["search_query"] = self.request.GET.get("q", "")
        return context


class PostCreateView(StaffRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "core/painel/post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Post salvo com sucesso!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("core:painel_dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo_pagina"] = "Novo Post"
        return context


class PostUpdateView(AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "core/painel/post_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Post atualizado com sucesso!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("core:painel_dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo_pagina"] = f"Editando: {self.object.title}"
        return context


class PostDeleteView(AuthorRequiredMixin, DeleteView):
    model = Post
    template_name = "core/painel/post_confirm_delete.html"
    success_url = reverse_lazy("core:painel_dashboard")

    def form_valid(self, form):
        messages.success(self.request, "Post removido com sucesso.")
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# Views do Painel (CRUD de Categorias)
# ---------------------------------------------------------------------------

class CategoryListView(StaffRequiredMixin, ListView):
    model = Category
    template_name = "core/painel/category_list.html"
    context_object_name = "categories"


class CategoryCreateView(StaffRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "core/painel/category_form.html"
    success_url = reverse_lazy("core:painel_category_list")

    def form_valid(self, form):
        messages.success(self.request, "Categoria criada com sucesso!")
        return super().form_valid(form)


class CategoryUpdateView(StaffRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "core/painel/category_form.html"
    success_url = reverse_lazy("core:painel_category_list")

    def form_valid(self, form):
        messages.success(self.request, "Categoria atualizada!")
        return super().form_valid(form)


class CategoryDeleteView(StaffRequiredMixin, DeleteView):
    model = Category
    template_name = "core/painel/category_confirm_delete.html"
    success_url = reverse_lazy("core:painel_category_list")
