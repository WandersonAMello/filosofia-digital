"""
Testes para as views públicas do blog (PostListView, PostDetailView).
Fase 2 do TDD — garante contratos das views existentes antes de adicionar auth.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Post, Category


class PostListViewTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_superuser(
            username="wanderson",
            password="senha-segura-123",
            email="wanderson@sansocrates.online",
        )
        self.cat_etica = Category.objects.create(name="Ética", slug="etica")
        self.cat_logica = Category.objects.create(name="Lógica", slug="logica")

        self.post_publicado = Post.objects.create(
            title="Post Publicado",
            slug="post-publicado",
            author=self.author,
            content="Conteúdo publicado.",
            summary="Resumo do post publicado.",
            status="published",
            category=self.cat_etica,
        )
        self.post_rascunho = Post.objects.create(
            title="Post Rascunho",
            slug="post-rascunho",
            author=self.author,
            content="Conteúdo em rascunho.",
            summary="Resumo do rascunho.",
            status="draft",
            category=self.cat_etica,
        )

    def test_lista_apenas_posts_publicados(self):
        response = self.client.get(reverse("core:post_list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.post_publicado, response.context["posts"])
        self.assertNotIn(self.post_rascunho, response.context["posts"])

    def test_rascunho_nao_aparece_na_lista(self):
        response = self.client.get(reverse("core:post_list"))
        self.assertNotContains(response, "Post Rascunho")

    def test_busca_por_titulo_retorna_resultado(self):
        response = self.client.get(reverse("core:post_search"), {"q": "Publicado"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Post Publicado")

    def test_busca_sem_resultado_exibe_mensagem_vazia(self):
        response = self.client.get(reverse("core:post_search"), {"q": "xyzzy-inexistente"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nenhuma postagem publicada")

    def test_filtro_por_categoria(self):
        post_logica = Post.objects.create(
            title="Post de Lógica",
            slug="post-de-logica",
            author=self.author,
            content="Sobre lógica.",
            status="published",
            category=self.cat_logica,
        )
        response = self.client.get(
            reverse("core:post_list_by_category", args=["logica"])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(post_logica, response.context["posts"])
        self.assertNotIn(self.post_publicado, response.context["posts"])

    def test_paginacao_com_mais_de_10_posts(self):
        for i in range(12):
            Post.objects.create(
                title=f"Post Extra {i}",
                slug=f"post-extra-{i}",
                author=self.author,
                content="Conteúdo.",
                status="published",
            )
        response = self.client.get(reverse("core:post_list"))
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["posts"]), 10)


class PostDetailViewTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_superuser(
            username="wanderson",
            password="senha-segura-123",
            email="wanderson@sansocrates.online",
        )
        self.post_publicado = Post.objects.create(
            title="Artigo Publicado",
            slug="artigo-publicado",
            author=self.author,
            content="## Seção 1\n\nTexto filosófico profundo.",
            status="published",
        )
        self.post_rascunho = Post.objects.create(
            title="Artigo Rascunho",
            slug="artigo-rascunho",
            author=self.author,
            content="Conteúdo ainda não pronto.",
            status="draft",
        )

    def test_detalhe_post_publicado_retorna_200(self):
        response = self.client.get(
            reverse("core:post_detail", args=["artigo-publicado"])
        )
        self.assertEqual(response.status_code, 200)

    def test_detalhe_post_rascunho_retorna_404(self):
        response = self.client.get(
            reverse("core:post_detail", args=["artigo-rascunho"])
        )
        self.assertEqual(response.status_code, 404)

    def test_detalhe_exibe_conteudo_renderizado_markdown(self):
        response = self.client.get(
            reverse("core:post_detail", args=["artigo-publicado"])
        )
        # get_markdown_content() deve ter convertido ## em <h2>
        # A extensão toc gera <h2 id="..."> — buscamos pelo prefixo
        self.assertContains(response, "<h2")
