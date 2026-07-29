"""
Formulários para o painel de gestão do blog Filosofia Digital.
"""
from django import forms
from django.utils.text import slugify
from .models import Post, Category


class PostForm(forms.ModelForm):
    # required=False permite submeter vazio e gerar via clean_slug
    slug = forms.SlugField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "gerado-automaticamente-do-titulo"}),
    )

    class Meta:
        model = Post
        fields = ["title", "slug", "content", "summary", "status", "category", "image"]
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "markdown-editor",
                "rows": 28,
                "placeholder": "Escreva seu ensaio em Markdown...",
            }),
            "summary": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Um breve resumo para a listagem...",
            }),
            "slug": forms.TextInput(attrs={
                "placeholder": "gerado-automaticamente-do-titulo",
            }),
            "title": forms.TextInput(attrs={
                "placeholder": "Título do ensaio",
            }),
        }

    def clean_slug(self):
        """
        Se o slug estiver vazio, gera automaticamente a partir do título.
        Se preenchido, valida unicidade (excluindo a instância atual na edição).
        """
        slug = self.cleaned_data.get("slug", "").strip()
        title = self.cleaned_data.get("title", "")

        if not slug:
            slug = slugify(title)

        # Valida unicidade excluindo a instância atual (para edição)
        qs = Post.objects.filter(slug=slug)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Post com este Slug já existe.")

        return slug


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Nome da categoria"}),
            "slug": forms.TextInput(attrs={"placeholder": "slug-da-categoria"}),
        }
