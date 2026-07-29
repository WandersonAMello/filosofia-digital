"""
Testes para a camada de modelo (Post e Category).
Fase 1 do TDD — cobre contratos de modelo.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import Post, Category


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Existencialismo",
            slug="existencialismo",
        )

    def test_category_str_retorna_nome(self):
        self.assertEqual(str(self.category), "Existencialismo")

    def test_category_slug_unico(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Outro", slug="existencialismo")


class PostModelTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_superuser(
            username="wanderson",
            password="senha-segura-123",
            email="wanderson@sansocrates.online",
        )
        self.category = Category.objects.create(
            name="Ética",
            slug="etica",
        )
        self.post = Post.objects.create(
            title="A Virtude em Aristóteles",
            slug="a-virtude-em-aristoteles",
            author=self.author,
            content="## Introdução\n\nA ética aristotélica é teleológica. " * 20,
            summary="Um ensaio sobre a virtude como meio-termo.",
            status="published",
            category=self.category,
        )

    def test_post_str_retorna_titulo(self):
        self.assertEqual(str(self.post), "A Virtude em Aristóteles")

    def test_post_status_default_eh_rascunho(self):
        post_sem_status = Post.objects.create(
            title="Rascunho Inicial",
            slug="rascunho-inicial",
            author=self.author,
            content="Conteúdo de teste.",
        )
        self.assertEqual(post_sem_status.status, "draft")

    def test_post_slug_unico(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Post.objects.create(
                title="Outro Post",
                slug="a-virtude-em-aristoteles",  # slug duplicado
                author=self.author,
                content="Conteúdo.",
            )

    def test_reading_time_calcula_corretamente(self):
        # O setUp cria um post com "A ética aristotélica é teleológica. " * 20
        # = 5 palavras * 20 = 100 palavras + o conteúdo do header = ~103 palavras
        # 103 / 200 = 0.5 → ceil = 1 minuto
        self.assertGreaterEqual(self.post.reading_time(), 1)

    def test_reading_time_minimo_de_1_minuto(self):
        post_curto = Post.objects.create(
            title="Post Curto",
            slug="post-curto",
            author=self.author,
            content="Texto.",
        )
        self.assertEqual(post_curto.reading_time(), 1)

    def test_get_markdown_content_renderiza_html(self):
        html = self.post.get_markdown_content()
        # A extensão toc gera <h2 id="..."> — buscamos pelo prefixo
        self.assertIn("<h2", html)
        self.assertIn("</h2>", html)

    def test_get_absolute_url_retorna_url_correta(self):
        url = self.post.get_absolute_url()
        expected = reverse("core:post_detail", args=["a-virtude-em-aristoteles"])
        self.assertEqual(url, expected)
