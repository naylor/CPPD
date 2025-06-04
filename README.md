# Podium

Sistema de Pontuação de Documentos

[![Assista ao vídeo](https://img.youtube.com/vi/iJV6Lqx4mGQ/maxresdefault.jpg)](https://www.youtube.com/watch?v=iJV6Lqx4mGQ)

> Sistema desenvolvido para agilizar processos como Classe Titular e RSC das Instituições Federais de Ensino.

> O sistema permite que usuários façam seu cadastro e participem de um processo, podemos enviando documentos e realizar sua pontuação.

> Após o processo ser submetido pelo usuário, o membros da comissão poderão conferir os documentos, que serão automaticamente organizados por índices com pontuação.

> O sistema faz marcações nos PDFs de documentos enviados para facilitar a conferência por membros da comissão.


## Tecnologias

- [Vue.js](https://vuejs.org/) (Frontend)
- [Django](https://www.djangoproject.com/) (Backend)

## Instalação

### Pré-requisitos

- [Docker](https://www.docker.com/) (Container)

### Passos

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/naylor/Podium.git
   cd Podium
   ```

2. **Configuração de ambiente:**  
   Dentro do Frontend, no arquivo .env:
    
    VITE_API_URL=http://localhost
    VITE_API_PORT=8000

    Na pasta Podium, no .env para o Backend, faça as demais configurações.

3. **Instale os Docker**

4. **Construa os Contêineres:**

   ```bash
   docker-compose build
   ```

5. **Rode os Contêineres:**

   ```bash
   docker-compose up
   ```

6. **Acesse no navegador:**  
   [http://localhost:8080](http://localhost:8080) (ou a porta configurada no seu projeto)


## Licença

Este projeto está sob licença proprietária. Consulte o autor para uso e distribuição.

---