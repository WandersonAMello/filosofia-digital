# Especificação: Filosofia Digital (Sansocrates.online)

## Propósito
Um blog pessoal focado em filosofia, projetado para ser simples, funcional e esteticamente agradável. O objetivo é proporcionar uma experiência de leitura serena para conteúdos de fôlego (long-form).
Disponível em: **https://sansocrates.online**

## Persona do Usuário
Wanderson (O Autor) e leitores interessados em filosofia e pensamento profundo.

## Recursos Principais
1. **Listagem de Artigos**: Uma página inicial limpa exibindo uma lista cronológica de ensaios filosóficos com resumos e tempos de leitura.
2. **Visualização de Leitura**: Uma experiência de leitura otimizada com tipografia elegante, cabeçalhos claros e foco total no conteúdo.
3. **Categorias/Tags**: Capacidade de agrupar postagens por ramos filosóficos (ex: Existencialismo, Ética, Lógica).
4. **Painel Administrativo**: Uma área segura para o autor escrever e gerenciar o conteúdo.
5. **Segurança**: Configurações do Django endurecidas, configuração segura do Docker e limitação de taxa (rate limiting) básica.
6. **Simplicidade**: Sem dependências complexas. Sem frameworks JavaScript pesados. Rápido e confiável.

## Direção Visual
* **Tipografia**: Fontes Serif para o corpo do texto (como Lora ou Playfair Display) e Sans-serif limpa para os cabeçalhos (como Inter).
* **Paleta de Cores**: Fundo off-white, texto em grafite profundo (deep charcoal) e acentos sutis de uma cor calma (ex: verde sálvia ou azul suave).
* **Estética**: "Jardim Digital" encontra o "Livro Tradicional".

## Restrições Técnicas
* **Framework**: Django (Python).
* **Banco de Dados**: SQLite (gerenciado via volume Docker).
* **Ambiente**: Docker & Docker Compose.
* **Servidor**: Pronto para implantação na internet.
