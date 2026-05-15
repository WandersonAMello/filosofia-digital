# Plano de Implementação: Filosofia Digital (Sansocrates.online)

## Stack Tecnológica
* **Linguagem**: Python 3.12
* **Framework**: Django 5.x
* **Banco de Dados**: SQLite (Pronto para produção em pequena escala)
* **Servidor Web**: Gunicorn + WhiteNoise (para arquivos estáticos)
* **Implantação**: Docker & Docker Compose

## Arquitetura
### 1. Apps Django
* `config`: Configurações, roteamento global.
* `core`: Modelos (`Post`, `Category`), Views e URLs do blog.

### 2. Modelo de Dados
* `Category`: `name`, `slug`
* `Post`: `title`, `slug`, `author` (User), `content` (suporte a Markdown), `summary`, `status` (Rascunho/Publicado), `created_at`, `category`

### 3. Sistema Visual
* Arquivo CSS único com Variáveis CSS.
* Efeitos de Glassmorphism para uma sensação premium.
* Layouts responsivos (Mobile-first).

### 4. Medidas de Segurança
* `DEBUG=False` em produção.
* Configuração SSL/TLS (gerenciada por Docker/Proxy).
* Configurações de Cookies seguros.
* Execução do Docker com usuário não-root.
