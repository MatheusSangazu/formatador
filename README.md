# 🤖 Formatador de Contatos - BotConversa

Uma ferramenta robusta desenvolvida para preparar, limpar e organizar listas de contatos antes da importação na plataforma **BotConversa**. O sistema resolve problemas comuns como telefones fora do padrão, nomes misturados e falta de segmentação.

![Status do Projeto](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Python-3.9-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)

## 🚀 Funcionalidades

### 1. Tratamento de Telefones Inteligente
- **Padronização:** Adiciona automaticamente o DDI `55` (Brasil) se ausente.
- **Correção de DDD:** Detecta e remove DDD duplicado (ex: `6262999...` vira `62999...`).
- **Números Incompletos:** Permite definir um DDD padrão para números salvos sem DDD (ex: `98888-1234` -> `5562988881234`).
- **Suporte Internacional:** Respeita números internacionais (ex: Portugal `351...`) sem forçar o DDI brasileiro.

### 2. Organização de Dados
- **Separação de Nomes:** Divide automaticamente "Nome Completo" em "Primeiro Nome" e "Sobrenome" (obrigatório para personalização de mensagens).
- **Criação de Grupos:** Fatia listas grandes em lotes (ex: `grupo1`, `grupo2`) para evitar bloqueios no WhatsApp por envio em massa.
- **Etiquetas Fixas:** Adiciona tags globais para toda a lista (ex: "Importação Jan, Cliente Frio").

### 3. Manutenção de Base (Limpeza)
- **Scanner de Etiquetas:** Analisa uma exportação do BotConversa e lista todas as etiquetas existentes.
- **Remoção Seletiva:** Permite selecionar e apagar etiquetas específicas em massa, mantendo as demais.

### 4. Interface Visual
- **Editor de Tabela:** Visualize, edite, adicione ou exclua contatos diretamente na tela antes de baixar.
- **Ordenação:** Ordene a lista por Nome (A-Z) ou Telefone (DDD) antes de gerar os grupos.

---

## 🛠️ Tecnologias Utilizadas

- **[Streamlit](https://streamlit.io/):** Interface web interativa e ágil.
- **[Pandas](https://pandas.pydata.org/):** Manipulação e limpeza de dados de alta performance.
- **[OpenPyXL](https://openpyxl.readthedocs.io/):** Leitura e escrita de arquivos Excel (.xlsx).
- **[Docker](https://www.docker.com/):** Containerização para deploy simples em qualquer servidor.

---

## 📦 Como Rodar Localmente

Certifique-se de ter o Python instalado.

1. **Clone o