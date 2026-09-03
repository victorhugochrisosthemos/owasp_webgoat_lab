# Avaliação de Vulnerabilidades em Ambiente OWASP WebGoat
<br>
Integrante do Projeto: Victor Chrisosthemos
<br>
- Esse é um projeto avaliativo para a matéria de Segurança de Sistemas Computacionais
<br><br>
## Arquitetura do Projeto
<br><br>
- O laboratório foi executado em Ubuntu 24.10
<br>
- O alvo escolhido foi o OWASP WebGoat, disponibilizado em contêiner Docker e vinculado à interface de loopback
(127.0.0.1), conforme a orientação de isolamento do roteiro do projeto
<br><br>
### Ferramentas de apoio
<br><br>
- Docker / Docker Compose: implantação e isolamento do WebGoat.<br>
- Navegador e DevTools: inspeção de cookies, cabeçalhos HTTP, requisições e respostas.<br>
- Burp Suite Community: baixei mas não usei, deu para fazer essas funções via python, mas a intenção era usar de apoio à interceptação e repetição de requisições HTTP.<br>
- Python 3 + requests: automação da prova de conceito de sequestro de sessão e análise de token JWT.<br>
- Base64 no terminal: decodificação do cabeçalho HTTP Basic Authentication<br>
