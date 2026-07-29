"""
Testes para as views autenticadas do painel de gestão.
Fases 3, 4 e 5 do TDD — autenticação, CRUD de posts e categorias.
Os testes são escritos ANTES da implementação (Red → Green → Refactor).
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Post, Category


# ---------------------------------------------------------------------------
# Fixtures helper
# ---------------------------------------------------------------------------

def criar_autor(username="wanderson", staff=True):
    user = User.objects.create_user(
        username=username,
        password="senha-segura-123",
        email=f"{username}@sansocrates.online",
    )
    if staff:
        user.is_staff = True
        user.save()
    return user


def criar_post(author, title="Post Teste", slug="post-teste", status="draft"):
    return Post.objects.create(
        title=title,
        slug=slug,
        author=author,
        content="Conteúdo filosófico de teste.",
        summary="Resumo do teste.",
        status=status,
    )


# ---------------------------------------------------------------------------
# FASE 3 — Autenticação
# ---------------------------------------------------------------------------

class AutenticacaoTest(TestCase):
    def setUp(self):
        self.autor = criar_autor()
        self.usuario_comum = criar_autor(username="leitor", staff=False)

    def test_login_com_credenciais_validas_redireciona_para_painel(self):
        # POST diretamente para a view de login da core
        response = self.client.post(reverse("core:login"), {
            "username": "wanderson",
            "password": "senha-segura-123",
        })
        self.assertRedirects(response, reverse("core:painel_dashboard"))

    def test_login_com_credenciais_invalidas_retorna_erro(self):
        response = self.client.post(reverse("core:login"), {
            "username": "wanderson",
            "password": "senha-errada",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Por favor, informe um usuário e senha corretos")

    def test_usuario_nao_staff_nao_acessa_painel(self):
        self.client.login(username="leitor", password="senha-segura-123")
        response = self.client.get(reverse("core:painel_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_logout_encerra_sessao(self):
        self.client.login(username="wanderson", password="senha-segura-123")
        response = self.client.post(reverse("core:logout"), follow=True)
        self.assertRedirects(response, reverse("core:post_list"))
        self.assertContains(response, "Sua sessão foi encerrada com sucesso.")
        # Após logout, o painel deve redirecionar para login
        res_painel = self.client.get(reverse("core:painel_dashboard"))
        login_url = reverse("core:login")
        dashboard_url = reverse("core:painel_dashboard")
        self.assertRedirects(res_painel, f"{login_url}?next={dashboard_url}")

    def test_logout_via_get_encerra_sessao_com_sucesso(self):
        self.client.login(username="wanderson", password="senha-segura-123")
        response = self.client.get(reverse("core:logout"), follow=True)
        self.assertRedirects(response, reverse("core:post_list"))
        self.assertContains(response, "Sua sessão foi encerrada com sucesso.")

    def test_rotas_de_gestao_redirecionam_anonimo_para_login(self):
        # LOGIN_URL = '/autor/login/', então o redirect inclui esse prefixo
        login_url = reverse("core:login")
        urls = [
            reverse("core:painel_dashboard"),
            reverse("core:painel_post_criar"),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"{login_url}?next={url}")


# ---------------------------------------------------------------------------
# FASE 4 — Dashboard
# ---------------------------------------------------------------------------

class PainelDashboardTest(TestCase):
    def setUp(self):
        self.autor = criar_autor()
        self.outro_autor = criar_autor(username="outro")
        self.client.login(username="wanderson", password="senha-segura-123")

        self.post_meu = criar_post(self.autor, title="Meu Post", slug="meu-post", status="published")
        self.post_rascunho = criar_post(self.autor, title="Meu Rascunho", slug="meu-rascunho", status="draft")
        self.post_outro = criar_post(self.outro_autor, title="Post do Outro", slug="post-do-outro")

    def test_dashboard_lista_todos_posts_do_autor(self):
        response = self.client.get(reverse("core:painel_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.post_meu, response.context["posts"])
        self.assertIn(self.post_rascunho, response.context["posts"])

    def test_dashboard_nao_lista_posts_de_outros_autores(self):
        response = self.client.get(reverse("core:painel_dashboard"))
        self.assertNotIn(self.post_outro, response.context["posts"])

    def test_dashboard_exibe_status_do_post(self):
        response = self.client.get(reverse("core:painel_dashboard"))
        self.assertContains(response, "Publicado")
        self.assertContains(response, "Rascunho")

    def test_dashboard_filtra_por_status_published(self):
        response = self.client.get(reverse("core:painel_dashboard") + "?status=published")
        self.assertIn(self.post_meu, response.context["posts"])
        self.assertNotIn(self.post_rascunho, response.context["posts"])

    def test_dashboard_filtra_por_status_draft(self):
        response = self.client.get(reverse("core:painel_dashboard") + "?status=draft")
        self.assertIn(self.post_rascunho, response.context["posts"])
        self.assertNotIn(self.post_meu, response.context["posts"])

    def test_dashboard_busca_textual_por_titulo(self):
        response = self.client.get(reverse("core:painel_dashboard") + "?q=Rascunho")
        self.assertIn(self.post_rascunho, response.context["posts"])
        self.assertNotIn(self.post_meu, response.context["posts"])



# ---------------------------------------------------------------------------
# FASE 4 — Criar Post
# ---------------------------------------------------------------------------

class CriarPostTest(TestCase):
    def setUp(self):
        self.autor = criar_autor()
        self.client.login(username="wanderson", password="senha-segura-123")

    def test_criar_post_valido_salva_como_rascunho(self):
        response = self.client.post(reverse("core:painel_post_criar"), {
            "title": "Novo Ensaio",
            "slug": "novo-ensaio",
            "content": "Texto filosófico.",
            "summary": "Resumo.",
            "status": "draft",
        })
        self.assertEqual(Post.objects.filter(slug="novo-ensaio").count(), 1)

    def test_criar_post_com_status_publicado(self):
        self.client.post(reverse("core:painel_post_criar"), {
            "title": "Ensaio Publicado",
            "slug": "ensaio-publicado",
            "content": "Texto.",
            "summary": "Resumo.",
            "status": "published",
        })
        post = Post.objects.get(slug="ensaio-publicado")
        self.assertEqual(post.status, "published")

    def test_criar_post_com_titulo_vazio_retorna_erro_de_validacao(self):
        response = self.client.post(reverse("core:painel_post_criar"), {
            "title": "",
            "slug": "sem-titulo",
            "content": "Texto.",
            "status": "draft",
        })
        self.assertEqual(response.status_code, 200)
        # Django 6: assertFormError recebe o objeto form, não a string "form"
        self.assertFormError(response.context["form"], "title", "Este campo é obrigatório.")

    def test_criar_post_slug_gerado_automaticamente_se_vazio(self):
        self.client.post(reverse("core:painel_post_criar"), {
            "title": "Post Sem Slug Manual",
            "slug": "",
            "content": "Texto.",
            "summary": "Resumo.",
            "status": "draft",
        })
        self.assertTrue(Post.objects.filter(slug="post-sem-slug-manual").exists())

    def test_criar_post_com_slug_duplicado_retorna_erro(self):
        criar_post(self.autor, title="Existente", slug="slug-duplicado")
        response = self.client.post(reverse("core:painel_post_criar"), {
            "title": "Novo",
            "slug": "slug-duplicado",
            "content": "Texto.",
            "status": "draft",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "slug", "Post com este Slug já existe.")


# ---------------------------------------------------------------------------
# FASE 4 — Editar Post
# ---------------------------------------------------------------------------

class EditarPostTest(TestCase):
    def setUp(self):
        self.autor = criar_autor()
        self.outro_autor = criar_autor(username="outro")
        self.client.login(username="wanderson", password="senha-segura-123")
        self.post = criar_post(self.autor, title="Post Original", slug="post-original")

    def test_editar_post_atualiza_campos(self):
        self.client.post(
            reverse("core:painel_post_editar", args=["post-original"]),
            {
                "title": "Post Atualizado",
                "slug": "post-original",
                "content": "Novo conteúdo.",
                "summary": "Novo resumo.",
                "status": "draft",
            },
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Post Atualizado")

    def test_editar_post_de_outro_autor_retorna_403(self):
        post_outro = criar_post(self.outro_autor, title="Post Alheio", slug="post-alheio")
        response = self.client.post(
            reverse("core:painel_post_editar", args=["post-alheio"]),
            {"title": "Hack", "slug": "post-alheio", "content": ".", "status": "draft"},
        )
        self.assertEqual(response.status_code, 403)

    def test_editar_post_muda_status_para_publicado(self):
        self.client.post(
            reverse("core:painel_post_editar", args=["post-original"]),
            {
                "title": "Post Original",
                "slug": "post-original",
                "content": "Conteúdo.",
                "summary": "Resumo.",
                "status": "published",
            },
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, "published")


# ---------------------------------------------------------------------------
# FASE 4 — Deletar Post
# ---------------------------------------------------------------------------

class DeletarPostTest(TestCase):
    def setUp(self):
        self.autor = criar_autor()
        self.outro_autor = criar_autor(username="outro")
        self.client.login(username="wanderson", password="senha-segura-123")
        self.post = criar_post(self.autor, title="Post a Deletar", slug="post-a-deletar")

    def test_deletar_post_remove_do_banco(self):
        self.client.post(reverse("core:painel_post_deletar", args=["post-a-deletar"]))
        self.assertFalse(Post.objects.filter(slug="post-a-deletar").exists())

    def test_deletar_post_de_outro_autor_retorna_403(self):
        post_outro = criar_post(self.outro_autor, title="Post Alheio", slug="post-alheio")
        response = self.client.post(
            reverse("core:painel_post_deletar", args=["post-alheio"])
        )
        self.assertEqual(response.status_code, 403)

    def test_confirmacao_de_delete_exibe_template_correto(self):
        response = self.client.get(
            reverse("core:painel_post_deletar", args=["post-a-deletar"])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/painel/post_confirm_delete.html")


# ---------------------------------------------------------------------------
# FASE 5 — Categorias
# ---------------------------------------------------------------------------

class CategoriaTest(TestCase):
    def setUp(self):
        self.autor = criar_autor()
        self.client.login(username="wanderson", password="senha-segura-123")
        self.cat = Category.objects.create(name="Metafísica", slug="metafisica")

    def test_listar_categorias_retorna_todas(self):
        response = self.client.get(reverse("core:painel_category_list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.cat, response.context["categories"])

    def test_criar_categoria_valida(self):
        self.client.post(reverse("core:painel_category_criar"), {
            "name": "Epistemologia",
            "slug": "epistemologia",
        })
        self.assertTrue(Category.objects.filter(slug="epistemologia").exists())

    def test_criar_categoria_com_slug_duplicado_retorna_erro(self):
        response = self.client.post(reverse("core:painel_category_criar"), {
            "name": "Outra Metafísica",
            "slug": "metafisica",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "slug", "Category com este Slug já existe.")

    def test_editar_categoria_atualiza_nome(self):
        self.client.post(
            reverse("core:painel_category_editar", args=[self.cat.pk]),
            {"name": "Metafísica Clássica", "slug": "metafisica"},
        )
        self.cat.refresh_from_db()
        self.assertEqual(self.cat.name, "Metafísica Clássica")

    def test_deletar_categoria_que_tem_posts_usa_set_null(self):
        autor = self.autor
        post = Post.objects.create(
            title="Post com Categoria",
            slug="post-com-categoria",
            author=autor,
            content="Texto.",
            status="draft",
            category=self.cat,
        )
        self.client.post(reverse("core:painel_category_deletar", args=[self.cat.pk]))
        post.refresh_from_db()
        self.assertIsNone(post.category)
