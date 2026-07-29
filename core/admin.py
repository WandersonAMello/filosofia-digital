from django.contrib import admin
from .models import Category, Post


def publicar_posts(modeladmin, request, queryset):
    """Ação de publicação em massa no Django Admin."""
    count = queryset.update(status="published")
    modeladmin.message_user(request, f"{count} post(s) publicado(s) com sucesso.")


publicar_posts.short_description = "Publicar posts selecionados"


def arquivar_posts(modeladmin, request, queryset):
    """Ação de arquivamento em massa no Django Admin."""
    count = queryset.update(status="draft")
    modeladmin.message_user(request, f"{count} post(s) movido(s) para rascunho.")


arquivar_posts.short_description = "Mover para rascunho"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "post_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def post_count(self, obj):
        return obj.posts.count()

    post_count.short_description = "Nº de Posts"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "category", "reading_time_display", "created_at")
    list_filter = ("status", "created_at", "author", "category")
    search_fields = ("title", "content", "summary")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    ordering = ("status", "-created_at")
    readonly_fields = ("created_at", "updated_at", "reading_time_display")
    actions = [publicar_posts, arquivar_posts]
    fieldsets = (
        ("Conteúdo", {
            "fields": ("title", "slug", "content", "summary", "image"),
        }),
        ("Publicação", {
            "fields": ("status", "author", "category"),
        }),
        ("Metadados", {
            "fields": ("created_at", "updated_at", "reading_time_display"),
            "classes": ("collapse",),
        }),
    )

    def reading_time_display(self, obj):
        return f"{obj.reading_time()} min"

    reading_time_display.short_description = "Tempo de leitura"
