# Podium

Sistema de Pontuação de Documentos

[Assista ao vídeo de apresentação](https://www.youtube.com/watch?v=iJV6Lqx4mGQ)

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


7. **Usuário padrão:**
   user: admin
   pass: admin


## Alterações no projeto

Criar o .venv:
   ```bash
   python3 -m venv .venv
   ```

Ativar o .venv:
   ```bash
   source .venv/bin/activate
   ```

Instalar as dependências:
   ```bash
   pip install -r requirements.txt
   ```

Para o banco de dados:
   ```bash
   python manage.py makemigrations sysdoc
   ```
   ```bash
   python manage.py migrate
   ```

Para criar o admin:
   ```bash
   python manage.py createsuperuser
   ```

Rodar o backend:
   ```bash
   python manage.py runserver
   ou
   gunicorn config.wsgi:application
   ```

Rodar o frontend:
   ```bash
   npm run dev
   ```  
   
   

Este projeto está sob licença proprietária. Consulte o autor para uso e distribuição.

---