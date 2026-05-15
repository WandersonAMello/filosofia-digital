from django.db.models import Q
from django.views.generic import ListView, DetailView
from .models import Post, Category

class PostListView(ListView):
    model = Post
    template_name = 'core/index.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.filter(status='published')
        
        # Filtro por Categoria
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
            
        # Busca Textual
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query) |
                Q(summary__icontains=query)
            )
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.kwargs.get('category_slug')
        context['search_query'] = self.request.GET.get('q')
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'core/detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(status='published')
