import streamlit as st
import pandas as pd
import re
from io import BytesIO
import math
# --- NOVOS IMPORTS PARA O COMPRESSOR ---
import subprocess
import os
import tempfile
# --- IMPORT PARA O DOWNLOADER ---
import yt_dlp

# Configuração da página (Mantida)
st.set_page_config(page_title="Canivete Suíço BotConversa", layout="wide")

st.title("🤖 Canivete Suíço - BotConversa")

# --- FUNÇÃO AUXILIAR DO COMPRESSOR (Adicionada no topo para organização) ---
def compress_pdf(input_file, power):
    quality = {
        0: "/default",
        1: "/prepress",
        2: "/printer",
        3: "/ebook",
        4: "/screen"
    }
    
    # Cria arquivo temporário para entrada
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_input:
        tmp_input.write(input_file.read())
        input_path = tmp_input.name
    
    output_path = input_path.replace(".pdf", "_compressed.pdf")

    # Comando Ghostscript
    gs_command = [
        "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={quality[power]}",
        "-dNOPAUSE", "-dQUIET", "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path
    ]

    try:
        subprocess.run(gs_command, check=True)
        with open(output_path, "rb") as f:
            compressed_data = f.read()
        
        # Limpeza dos arquivos temporários
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)
        return compressed_data
    except Exception as e:
        st.error(f"Erro na compressão: {e}")
        if os.path.exists(input_path): os.remove(input_path)
        return None


# ATUALIZADO: Agora são 4 abas
tab1, tab2, tab3, tab4 = st.tabs(["🚀 Formatar e Criar Grupos", "🧹 Limpar Etiquetas Existentes", "🗜️ Compressor PDF", "📥 Downloader (Beta)"])


# ==============================================================================
# ABA 1: FORMATADOR (SEU CÓDIGO ORIGINAL - INTACTO)
# ==============================================================================
with tab1:
    st.markdown("### Prepare planilhas novas para subir no BotConversa")
    
    # --- BARRA LATERAL (CONFIGURAÇÕES ABA 1) ---
    st.sidebar.header("🏷️ Configuração (Importação)")
    
    # 1. Ordenação
    st.sidebar.subheader("🔃 Ordenação")
    criterio_ordenacao = st.sidebar.selectbox(
        "Ordenar planilha por:", 
        ["Original (Como veio)", "Primeiro nome", "Telefone"]
    )
    if criterio_ordenacao != "Original (Como veio)":
        direcao_ordenacao = st.sidebar.radio(
            "Sentido da ordem:", 
            ["Crescente (A-Z ou 0-9)", "Decrescente (Z-A ou 9-0)"]
        )
    
    # 2. Configurações de Telefone (DDD Padrão) - NOVO
    st.sidebar.markdown("---")
    st.sidebar.subheader("📞 Telefone")
    ddd_padrao = st.sidebar.text_input(
        "DDD Padrão (para números sem DDD)", 
        placeholder="Ex: 62",
        max_chars=2,
        help="Se o número tiver apenas 8 ou 9 dígitos, usaremos este DDD."
    )
    
    # 3. Etiquetas Fixas
    st.sidebar.markdown("---")
    st.sidebar.subheader("🏷️ Etiquetas")
    etiquetas_fixas = st.sidebar.text_input(
        "Etiquetas Fixas (para todos)", 
        placeholder="Ex: Importacao, Cliente Novo"
    )

    # 4. Configuração de Grupos
    st.sidebar.markdown("---")
    st.sidebar.subheader("📦 Divisão em Lotes")
    ativar_grupos = st.sidebar.checkbox("Dividir contatos em grupos?", value=False)
    
    tamanho_grupo = 100
    prefixo_grupo = "grupo"

    if ativar_grupos:
        tamanho_grupo = st.sidebar.number_input("Pessoas por grupo", min_value=1, value=100)
        prefixo_grupo = st.sidebar.text_input("Nome do grupo", value="grupo")
        st.sidebar.info(f"Isso vai gerar: {prefixo_grupo}1, {prefixo_grupo}2...")

    # --- LÓGICA DE FORMATAÇÃO (V6) ---
    def formatar_telefone(tel):
        if pd.isna(tel): return ""
        nums = re.sub(r'\D', '', str(tel))
        
        # Remove zero à esquerda
        if nums.startswith('0'): nums = nums[1:]
        
        # --- CASO 1: NÚMERO SEM DDD (8 ou 9 dígitos) ---
        # Se o usuário definiu um DDD Padrão, usa ele aqui.
        if len(nums) in [8, 9] and ddd_padrao:
            nums = ddd_padrao + nums # Agora tem DDD (10 ou 11) e cai na regra abaixo do 55
            
        # --- CASO 2: CORREÇÃO DE DDD DUPLICADO ---
        # Se tem 12 ou 13 dígitos E NÃO começa com 55 (Ex: 626299...)
        if len(nums) >= 12 and not nums.startswith('55'):
            if nums[0:2] == nums[2:4]:
                nums = nums[2:] 
            elif len(nums) == 13: 
                nums = nums[2:]

        # --- CASO 3: REGRA FINAL DO 55 ---
        if len(nums) in [10, 11]:
            nums = '55' + nums
            
        return nums

    def separar_nomes(row):
        nome_full = str(row['Nome']).strip() if 'Nome' in row and not pd.isna(row['Nome']) else ""
        sobre_orig = str(row['Sobrenome']).strip() if 'Sobrenome' in row and not pd.isna(row['Sobrenome']) else ""
        
        if not sobre_orig:
            partes = nome_full.split(maxsplit=1)
            p_nome = partes[0] if len(partes) > 0 else ""
            s_nome = partes[1] if len(partes) > 1 else ""
        else:
            p_nome = nome_full
            s_nome = sobre_orig
        return pd.Series([p_nome, s_nome])

    # --- UPLOAD ABA 1 ---
    uploaded_file_tab1 = st.file_uploader("Escolha o arquivo para IMPORTAÇÃO (XLSX ou CSV)", type=['xlsx', 'csv'], key="up1")

    if uploaded_file_tab1 is not None:
        try:
            if uploaded_file_tab1.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file_tab1)
            else:
                df = pd.read_excel(uploaded_file_tab1)

            st.success(f"Arquivo carregado! {len(df)} contatos encontrados.")

            with st.spinner('Processando e Ordenando...'):
                if 'Nome' not in df.columns and 'Primeiro nome' not in df.columns:
                     st.error("A planilha precisa ter uma coluna 'Nome'.")
                else:
                    if 'Primeiro nome' not in df.columns:
                        df[['Primeiro nome', 'Sobrenome']] = df.apply(separar_nomes, axis=1)
                    
                    col_tel = next((c for c in df.columns if 'tel' in c.lower() or 'cel' in c.lower()), None)
                    
                    if col_tel:
                        # Aplica a formatação passando pela lógica do DDD Padrão
                        df['Telefone'] = df[col_tel].apply(formatar_telefone)
                        
                        # Ordenação
                        if criterio_ordenacao != "Original (Como veio)":
                            eh_crescente = True if "Crescente" in direcao_ordenacao else False
                            if criterio_ordenacao in df.columns:
                                df = df.sort_values(by=criterio_ordenacao, ascending=eh_crescente)
                                df = df.reset_index(drop=True)
                        
                        # Etiquetas
                        lista_etiquetas = []
                        for index in range(len(df)):
                            tags = []
                            if etiquetas_fixas: tags.append(etiquetas_fixas)
                            if ativar_grupos:
                                numero_grupo = math.floor(index / tamanho_grupo) + 1
                                tags.append(f"{prefixo_grupo}{numero_grupo}")
                            lista_etiquetas.append(",".join(tags))
                        
                        df['Etiquetas'] = lista_etiquetas
                        df_inicial = df[['Primeiro nome', 'Sobrenome', 'Telefone', 'Etiquetas']].copy()

                        st.divider()
                        st.subheader("Edição e Conferência")
                        
                        df_editado = st.data_editor(
                            df_inicial, 
                            num_rows="dynamic", 
                            use_container_width=True,
                            key="editor_importacao"
                        )
                        
                        if ativar_grupos:
                            qtd_grupos = math.ceil(len(df_editado) / tamanho_grupo)
                            st.caption(f"📊 Total: {len(df_editado)} | Grupos gerados: {qtd_grupos}")

                        buffer = BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            df_editado.to_excel(writer, index=False)
                        
                        st.download_button(
                            label="⬇️ Baixar Tabela Pronta",
                            data=buffer.getvalue(),
                            file_name="importacao_botconversa_v6.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            type="primary"
                        )
                    else:
                        st.error("Não encontrei uma coluna de Telefone/Celular.")
        except Exception as e:
            st.error(f"Erro ao processar: {e}")


# ==============================================================================
# ABA 2: LIMPADOR (SEU CÓDIGO ORIGINAL - INTACTO)
# ==============================================================================
with tab2:
    st.markdown("### Limpar etiquetas de uma base exportada")
    
    uploaded_file_tab2 = st.file_uploader("Escolha o arquivo do BOTCONVERSA (XLSX ou CSV)", type=['xlsx', 'csv'], key="up2")

    if uploaded_file_tab2 is not None:
        try:
            if uploaded_file_tab2.name.endswith('.csv'):
                df_clean = pd.read_csv(uploaded_file_tab2)
            else:
                df_clean = pd.read_excel(uploaded_file_tab2)
            
            col_tags = next((c for c in df_clean.columns if 'etiqueta' in c.lower() or 'tags' in c.lower()), None)

            if col_tags:
                st.info(f"Coluna de etiquetas identificada: **{col_tags}**")
                
                todas_tags = df_clean[col_tags].astype(str).str.split(',').explode().str.strip().unique()
                todas_tags = [t for t in todas_tags if t != 'nan' and t != ''] 
                todas_tags.sort()

                tags_para_remover = st.multiselect(
                    "❌ Selecione quais etiquetas REMOVER:",
                    options=todas_tags
                )

                if tags_para_remover:
                    def limpar_tags(valor_celula):
                        if pd.isna(valor_celula): return ""
                        tags_atuais = [t.strip() for t in str(valor_celula).split(',')]
                        tags_finais = [t for t in tags_atuais if t not in tags_para_remover and t != '']
                        return ",".join(tags_finais)

                    df_clean['Etiquetas'] = df_clean[col_tags].apply(limpar_tags)
                else:
                    if 'Etiquetas' not in df_clean.columns:
                        df_clean['Etiquetas'] = df_clean[col_tags]

                cols_para_mostrar = [c for c in df_clean.columns if c != col_tags] 
                if 'Etiquetas' not in cols_para_mostrar: cols_para_mostrar.append('Etiquetas')
                
                st.divider()
                st.markdown("### Revise e Edite o resultado:")
                
                df_clean_editado = st.data_editor(
                    df_clean[cols_para_mostrar], 
                    num_rows="dynamic",
                    use_container_width=True,
                    key="editor_limpeza"
                )
                    
                buffer_clean = BytesIO()
                with pd.ExcelWriter(buffer_clean, engine='openpyxl') as writer:
                    df_clean_editado.to_excel(writer, index=False)
                
                st.download_button(
                    label="⬇️ Baixar Planilha Limpa",
                    data=buffer_clean.getvalue(),
                    file_name="base_atualizada_sem_etiquetas.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )

            else:
                st.error("Não encontrei uma coluna chamada 'Etiquetas' ou 'Tags'.")

        except Exception as e:
            st.error(f"Erro ao processar: {e}")

# ==============================================================================
# ABA 3: COMPRESSOR DE PDF (NOVA FUNCIONALIDADE)
# ==============================================================================
with tab3:
    st.header("🗜️ Compressor de PDF")
    st.markdown("Reduza o tamanho de arquivos PDF pesados usando o motor **Ghostscript**.")

    uploaded_pdf = st.file_uploader("Solte seu PDF pesadão aqui", type=['pdf'])

    if uploaded_pdf is not None:
        # Mostra tamanho original
        original_size = uploaded_pdf.size / 1024 / 1024 # MB
        st.write(f"📁 Tamanho Original: **{original_size:.2f} MB**")

        st.divider()
        
        # Seletor de Nível
        nivel = st.select_slider(
            "Escolha o nível de compressão:",
            options=["Extrema (Email)", "Média (Ebook)", "Alta Qualidade (Impressão)"],
            value="Média (Ebook)"
        )

        mapa_nivel = {
            "Extrema (Email)": 4,   # /screen
            "Média (Ebook)": 3,     # /ebook
            "Alta Qualidade (Impressão)": 2 # /printer
        }

        if st.button("🔥 Comprimir PDF", type="primary"):
            with st.spinner("O robô está espremendo o arquivo..."):
                pdf_comprimido = compress_pdf(uploaded_pdf, mapa_nivel[nivel])
            
            if pdf_comprimido:
                novo_tamanho = len(pdf_comprimido) / 1024 / 1024
                reducao = (1 - (novo_tamanho / original_size)) * 100
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Tamanho Original", f"{original_size:.2f} MB")
                c2.metric("Novo Tamanho", f"{novo_tamanho:.2f} MB")
                c3.metric("Redução", f"{reducao:.1f}%", delta_color="normal")
                
                st.balloons()
                
                st.download_button(
                    label="⬇️ Baixar PDF Comprimido",
                    data=pdf_comprimido,
                    file_name=f"comprimido_{uploaded_pdf.name}",
                    mime="application/pdf",
                    type="primary"
                )


# ==============================================================================
# ABA 4: DOWNLOADER DE MÍDIA (NOVA FUNCIONALIDADE - BETA)
# ==============================================================================
with tab4:
    st.header("📥 Downloader de Mídia (Beta)")
    st.markdown("Baixe vídeos e áudios do **YouTube** e **Instagram**.")
    st.caption("⚠️ Use apenas para conteúdo que você tem permissão para baixar.")

    # Aviso de Beta
    st.info("🧪 Esta funcionalidade está em fase Beta. Pode apresentar instabilidades ou não funcionar com alguns links.")

    st.divider()

    # Input da URL
    url_input = st.text_input("Cole o link do vídeo/áudio:", placeholder="https://www.youtube.com/watch?v=... ou https://www.instagram.com/p/...")

    if url_input:
        # Detectar plataforma
        plataforma = "Desconhecida"
        if "youtube.com" in url_input or "youtu.be" in url_input:
            plataforma = "YouTube"
        elif "instagram.com" in url_input:
            plataforma = "Instagram"

        st.info(f"Plataforma detectada: **{plataforma}**")

        # Opções de download
        col1, col2 = st.columns(2)

        with col1:
            tipo_download = st.radio(
                "O que deseja baixar?",
                ["Vídeo", "Áudio apenas"],
                horizontal=True
            )

        with col2:
            if tipo_download == "Vídeo":
                qualidade_video = st.selectbox(
                    "Qualidade do vídeo:",
                    ["Melhor disponível", "1080p", "720p", "480p"]
                )
            else:
                formato_audio = st.selectbox(
                    "Formato do áudio:",
                    ["MP3", "M4A"]
                )

        st.divider()

        # Botão de download
        if st.button("🎬 Baixar Mídia", type="primary"):
            with st.spinner("Preparando download..."):
                try:
                    # Configurações do yt-dlp
                    ydl_opts = {
                        'quiet': True,
                        'no_warnings': True,
                    }

                    if tipo_download == "Áudio apenas":
                        ydl_opts['format'] = 'bestaudio/best'
                        ydl_opts['postprocessors'] = [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': formato_audio.lower(),
                            'preferredquality': '192',
                        }]
                        ydl_opts['outtmpl'] = '%(title)s.%(ext)s'
                    else:
                        # Configuração de vídeo
                        if qualidade_video == "Melhor disponível":
                            ydl_opts['format'] = 'best'
                        elif qualidade_video == "1080p":
                            ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best'
                        elif qualidade_video == "720p":
                            ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best'
                        else:
                            ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best'

                        ydl_opts['outtmpl'] = '%(title)s.%(ext)s'
                        ydl_opts['merge_output_format'] = 'mp4'

                    # Obter informações primeiro
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url_input, download=False)
                        titulo = info.get('title', 'Video')
                        duracao = info.get('duration', 0)
                        thumb = info.get('thumbnail', '')

                        # Converter duração para formato legível
                        minutos = duracao // 60
                        segundos = duracao % 60
                        duracao_str = f"{minutos}:{segundos:02d}"

                    # Exibir informações do vídeo
                    st.success("Informações do vídeo:")
                    col_info1, col_info2 = st.columns(2)
                    col_info1.write(f"📌 Título: {titulo}")
                    col_info2.write(f"⏱️ Duração: {duracao_str}")

                    if thumb:
                        st.image(thumb, width=300, caption="Thumbnail")

                    # Fazer o download em arquivo temporário
                    temp_dir = tempfile.mkdtemp()
                    temp_file = os.path.join(temp_dir, 'downloaded_file')

                    with st.spinner("Baixando mídia..."):
                        with yt_dlp.YoutubeDL({**ydl_opts, 'outtmpl': temp_dir + '/%(title)s.%(ext)s'}) as ydl:
                            ydl.download([url_input])

                        # Encontrar o arquivo baixado
                        downloaded_files = []
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                downloaded_files.append(os.path.join(root, file))

                        if downloaded_files:
                            arquivo_final = downloaded_files[0]
                            nome_arquivo = os.path.basename(arquivo_final)
                            tamanho_arquivo = os.path.getsize(arquivo_final) / (1024 * 1024) # MB

                            with open(arquivo_final, 'rb') as f:
                                arquivo_bytes = f.read()

                            # Limpar arquivos temporários
                            import shutil
                            shutil.rmtree(temp_dir)

                            st.success(f"Download concluído! Tamanho: {tamanho_arquivo:.2f} MB")

                            # Determinar MIME type
                            if tipo_download == "Áudio apenas":
                                mime_type = "audio/mpeg" if formato_audio == "MP3" else "audio/mp4"
                            else:
                                mime_type = "video/mp4"

                            st.download_button(
                                label="⬇️ Baixar Arquivo",
                                data=arquivo_bytes,
                                file_name=nome_arquivo,
                                mime=mime_type,
                                type="primary"
                            )
                        else:
                            st.error("Erro ao localizar arquivo baixado.")

                except Exception as e:
                    st.error(f"Erro ao baixar mídia: {str(e)}")
                    st.caption("💡 Dica: Verifique se o link está correto e se o vídeo está disponível publicamente.")