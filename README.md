# Filosofia Digital (Sansocrates.online)

Um blog de filosofia simples, seguro e esteticamente premium, desenvolvido com Django e gerenciado por agentes de IA (Antigravity).

Disponível em: [https://sansocrates.online](https://sansocrates.online)

## 🚀 Metodologia: Spec-Driven Development
Este projeto segue a metodologia do `github/spec-kit`, onde cada funcionalidade é documentada e planejada antes da implementação.

### Estrutura de Documentação
- [Especificação](docs/1_specification.md)
- [Plano de Implementação](docs/2_implementation_plan.md)
- [Lista de Tarefas](docs/3_tasks.md)

## 🛠 Tech Stack
- **Backend**: Django 5+
- **Gerenciador de Dependências**: `uv`
- **Frontend**: Vanilla CSS (Rich Aesthetics)
- **Deployment**: Docker & Docker Compose

## 📦 Como rodar localmente
1. Certifique-se de ter o `uv` instalado.
2. Clone o repositório.
3. Crie o arquivo `.env` baseado no exemplo.
4. Rode as migrações:
   ```bash
   uv run python manage.py migrate
   ```
5. Inicie o servidor:
   ```bash
   uv run python manage.py runserver
   ```

---
*Desenvolvido em parceria com Antigravity (AI Agent).*
