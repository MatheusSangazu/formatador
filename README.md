# 🤖 Canivete Suíço - BotConversa

Uma ferramenta completa desenvolvida para preparar, limpar e organizar listas de contatos antes da importação na plataforma **BotConversa**, além de utilitários adicionais para compressão de PDF e download de mídia.

![Status do Projeto](https://img.shields.io/badge/Status-Ativo-green)
![Python](https://img.shields.io/badge/Python-3.9-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)

## 🚀 Funcionalidades

### 1. Formatar e Criar Grupos (Importação)
- **Tratamento de Telefones Inteligente:**
  - Padronização: Adiciona automaticamente o DDI `55` (Brasil) se ausente.
  - Correção de DDD: Detecta e remove DDD duplicado (ex: `6262999...` vira `62999...`).
  - Números Incompletos: Permite definir um DDD padrão para números salvos sem DDD (ex: `98888-1234` -> `5562988881234`).
  - Suporte Internacional: Respeita números internacionais (ex: Portugal `351...`) sem forçar o DDI brasileiro.
- **Organização de Dados:**
  - Separação de Nomes: Divide automaticamente "Nome Completo" em "Primeiro Nome" e "Sobrenome" (obrigatório para personalização de mensagens).
  - Criação de Grupos: Fatia listas grandes em lotes (ex: `grupo1`, `grupo2`) para evitar bloqueios no WhatsApp por envio em massa.
  - Etiquetas Fixas: Adiciona tags globais para toda a lista (ex: "Importação Jan, Cliente Frio").
- **Interface Visual:**
  - Editor de Tabela: Visualize, edite, adicione ou exclua contatos diretamente na tela antes de baixar.
  - Ordenação: Ordene a lista por Nome (A-Z) ou Telefone (DDD) antes de gerar os grupos.

### 2. Limpar Etiquetas Existentes (Manutenção)
- **Scanner de Etiquetas:** Analisa uma exportação do BotConversa e lista todas as etiquetas existentes.
- **Remoção Seletiva:** Permite selecionar e apagar etiquetas específicas em massa, mantendo as demais.
- **Editor Visual:** Revise e edite o resultado antes de baixar.

### 3. Compressor de PDF
- **Compressão Inteligente:** Reduza o tamanho de arquivos PDF pesados usando o motor Ghostscript.
- **Níveis de Qualidade:** Escolha entre Extrema (Email), Média (Ebook) ou Alta Qualidade (Impressão).
- **Feedback Visual:** Visualize a redução obtida antes de baixar.

### 4. Downloader de Mídia (Beta) 🧪
- **Suporte Multiplataforma:** Baixe vídeos e áudios do YouTube e Instagram.
- **Opções de Download:**
  - Vídeo: Melhor disponível, 1080p, 720p, 480p
  - Áudio: MP3 ou M4A
- **Preview Antes do Download:** Veja título, duração e thumbnail antes de baixar.
- **Detecção Automática:** Identifica automaticamente a plataforma do link.
- **Opções Avançadas:**
  - **Cookies:** Upload de arquivo cookies.txt para contornar autenticação e Cloudflare.
  - **User-Agent:** User-Agent realista configurado automaticamente para evitar bloqueios.
- **Soluções de Erros:** Mensagens informativas e dicas específicas para cada tipo de erro.
- ⚠️ **Nota:** Use apenas para conteúdo que você tem permissão para baixar.

---

## 🛠️ Tecnologias Utilizadas

- **[Streamlit](https://streamlit.io/):** Interface web interativa e ágil.
- **[Pandas](https://pandas.pydata.org/):** Manipulação e limpeza de dados de alta performance.
- **[OpenPyXL](https://openpyxl.readthedocs.io/):** Leitura e escrita de arquivos Excel (.xlsx).
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp):** Download de vídeos e áudios do YouTube e Instagram.
- **[Ghostscript](https://www.ghostscript.com/):** Compressão de PDFs.
- **[FFmpeg](https://ffmpeg.org/):** Processamento de áudio e vídeo.
- **[Docker](https://www.docker.com/):** Containerização para deploy simples em qualquer servidor.

---

## 📦 Como Rodar Localmente

Certifique-se de ter o Python instalado.

1. **Clone o** repositório:
```bash
git clone https://github.com/MatheusSangazu/formatador.git
cd formatador
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Execute a aplicação:**
```bash
streamlit run app.py
```

4. Acesse no navegador: `http://localhost:8501`

---

## 🐳 Como Rodar com Docker

1. **Build da imagem:**
```bash
docker build -t formatador-botconversa .
```

2. **Execute o container:**
```bash
docker run -p 8501:8501 formatador-botconversa
```

3. Acesse no navegador: `http://localhost:8501`

Ou use o docker-compose:
```bash
docker-compose up
```

---

## 📝 Estrutura do Projeto

```
formatador/
├── app.py              # Aplicação principal Streamlit
├── requirements.txt     # Dependências Python
├── Dockerfile          # Configuração do container Docker
├── docker-compose.yml  # Orquestração Docker Compose
├── documentação.md     # Documentação oficial da biblioteca yt-dlp
├── .gitignore         # Arquivos ignorados pelo Git
└── README.md          # Este arquivo
```

---

## ⚠️ Notas Importantes

- **Downloader (Beta):** Esta funcionalidade está em fase Beta. Pode apresentar instabilidades ou não funcionar com alguns links.
- **Uso Responsável:** O downloader deve ser utilizado apenas para conteúdo que você tem permissão para baixar.
- **FFmpeg Local:** Para usar o downloader localmente (fora do Docker), é necessário instalar o FFmpeg separadamente.
- **Cookies do Navegador:** Para criar um arquivo cookies.txt, use a extensão "Get cookies.txt LOCALLY" no Chrome ou "cookies.txt" no Firefox. Isso ajuda a contornar problemas de autenticação e Cloudflare.
- **Erros de Autenticação:** Se encontrar erros como "Sign in to confirm you're not a bot", tente:
  1. Abrir o vídeo no navegador e resolver o captcha
  2. Usar a opção "Opções Avançadas (Cookies)" com um arquivo cookies.txt
  3. Baixar apenas o áudio (funciona melhor em alguns casos)

---

## 📄 Licença

Este projeto está disponível sob a Licença MIT.

---

## 👤 Autor

Desenvolvido por [Matheus Sangazu](https://github.com/MatheusSangazu)