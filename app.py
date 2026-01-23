import streamlit as st
import pandas as pd
import re
from io import BytesIO
import math
import subprocess
import os
import tempfile


st.set_page_config(page_title="Canivete Suíço ForjaCorp", layout="wide", page_icon="🛠️")

st.title("🛠️ Canivete Suíço - ForjaCorp")


tab1, tab2, tab3 = st.tabs(["🚀 Formatar Contatos", "🧹 Limpar Etiquetas", "🗜️ Compressor PDF"])

# ==============================================================================
# FUNÇÕES GERAIS
# ==============================================================================
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def compress_pdf(input_file, power):
    """
    Função para comprimir PDF usando Ghostscript
    """
    quality = {
        0: "/default",
        1: "/prepress",
        2: "/printer",
        3: "/ebook",
        4: "/screen"
    }
    
    # Salva arquivo temporário
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
        
        # Limpa arquivos temporários
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)
        return compressed_data
    except Exception as e:
        st.error(f"Erro na compressão: {e}")
        # Tenta limpar mesmo com erro
        if os.path.exists(input_path): os.remove(input_path)
        return None

# ==============================================================================
# ABA 1: FORMATADOR E ORGANIZADOR
# ==============================================================================
with tab1:
    st.markdown("### 🚀 Preparar planilhas para o BotConversa")
    
    col_config, col_main = st.columns([1, 3])

    with col_config:
        st.info("⚙️ **Configurações**")
        
        # 1. Ordenação
        criterio_ordenacao = st.selectbox(
            "Ordenar por:", 
            ["Original (Como veio)", "Primeiro nome", "Telefone"]
        )
        direcao_ordenacao = "Crescente"
        if criterio_ordenacao != "Original (Como veio)":
            direcao_ordenacao = st.radio("Ordem:", ["Crescente (A-Z)", "Decrescente (Z-A)"])
        
        st.divider()

        # 2. Telefone
        ddd_padrao = st.text_input("DDD Padrão (se faltar)", placeholder="Ex: 62", max_chars=2)
        
        st.divider()

        # 3. Etiquetas
        etiquetas_fixas = st.text_input("Etiquetas Fixas", placeholder="Ex: Importacao, Frio")

        st.divider()

        # 4. Grupos
        ativar_grupos = st.checkbox("Dividir em Grupos?", value=False)
        tamanho_grupo = 100
        prefixo_grupo = "grupo"
        if ativar_grupos:
            tamanho_grupo = st.number_input("Qtd por grupo", min_value=1, value=100)
            prefixo_grupo = st.text_input("Nome do grupo", value="grupo")

    with col_main:
        
        def formatar_telefone(tel):
            if pd.isna(tel): return ""
            nums = re.sub(r'\D', '', str(tel))
            if nums.startswith('0'): nums = nums[1:]
            
            # Caso 1: Sem DDD (8 ou 9 digitos)
            if len(nums) in [8, 9] and ddd_padrao:
                nums = ddd_padrao + nums 
            
            # Caso 2: Correção de DDD duplicado 
            if len(nums) >= 12 and not nums.startswith('55'):
                if nums[0:2] == nums[2:4]: # Ex: 6262...
                    nums = nums[2:] 
                elif len(nums) == 13: 
                    nums = nums[2:]

            # Caso 3: Adicionar 55
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

        uploaded_file_tab1 = st.file_uploader("📂 Solte sua planilha aqui (XLSX ou CSV)", type=['xlsx', 'csv'], key="up1")

        if uploaded_file_tab1 is not None:
            try:
                if uploaded_file_tab1.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file_tab1)
                else:
                    df = pd.read_excel(uploaded_file_tab1)

                if 'Nome' not in df.columns and 'Primeiro nome' not in df.columns:
                     st.error("❌ Erro: A planilha precisa ter uma coluna chamada 'Nome'.")
                else:
                    
                    if 'Primeiro nome' not in df.columns:
                        df[['Primeiro nome', 'Sobrenome']] = df.apply(separar_nomes, axis=1)
                    
                    col_tel = next((c for c in df.columns if 'tel' in c.lower() or 'cel' in c.lower() or 'whatsapp' in c.lower()), None)
                    
                    if col_tel:
                        df['Telefone'] = df[col_tel].apply(formatar_telefone)
                        
                        # Ordenar
                        if criterio_ordenacao != "Original (Como veio)":
                            eh_crescente = True if "Crescente" in direcao_ordenacao else False
                            col_ordem = "Primeiro nome" if criterio_ordenacao == "Primeiro nome" else "Telefone"
                            df = df.sort_values(by=col_ordem, ascending=eh_crescente).reset_index(drop=True)
                        
                        # Criar Etiquetas e Grupos
                        lista_etiquetas = []
                        for index in range(len(df)):
                            tags = []
                            if etiquetas_fixas: tags.append(etiquetas_fixas)
                            if ativar_grupos:
                                numero_grupo = math.floor(index / tamanho_grupo) + 1
                                tags.append(f"{prefixo_grupo}{numero_grupo}")
                            lista_etiquetas.append(",".join(tags))
                        
                        df['Etiquetas'] = lista_etiquetas
                        
                        # Selecionar colunas finais
                        df_final = df[['Primeiro nome', 'Sobrenome', 'Telefone', 'Etiquetas']].copy()

                        st.success(f"✅ Processado! {len(df_final)} contatos.")
                        
                        # Editor
                        df_editado = st.data_editor(df_final, num_rows="dynamic", use_container_width=True, key="editor_v7")
                        
                        # Botão Download
                        excel_data = to_excel(df_editado)
                        st.download_button(
                            label="⬇️ Baixar Planilha Pronta",
                            data=excel_data,
                            file_name="importacao_botconversa_v7.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            type="primary"
                        )
                    else:
                        st.error("Não encontrei coluna de Telefone/Celular/Whatsapp.")

            except Exception as e:
                st.error(f"Erro ao ler arquivo: {e}")

# ==============================================================================
# ABA 2: LIMPADOR DE ETIQUETAS
# ==============================================================================
with tab2:
    st.markdown("### 🧹 Limpar etiquetas de base exportada")
    st.caption("Suba o arquivo exportado do BotConversa para remover tags antigas.")

    uploaded_file_tab2 = st.file_uploader("Arquivo do BotConversa (XLSX/CSV)", type=['xlsx', 'csv'], key="up2")

    if uploaded_file_tab2 is not None:
        try:
            if uploaded_file_tab2.name.endswith('.csv'):
                df_clean = pd.read_csv(uploaded_file_tab2)
            else:
                df_clean = pd.read_excel(uploaded_file_tab2)
            
            col_tags = next((c for c in df_clean.columns if 'etiqueta' in c.lower() or 'tags' in c.lower()), None)

            if col_tags:
                # Identificar todas as tags únicas
                todas_tags = df_clean[col_tags].astype(str).str.split(',').explode().str.strip().unique()
                todas_tags = [t for t in todas_tags if t and t != 'nan']
                
                tags_para_remover = st.multiselect("Selecione as etiquetas para REMOVER:", sorted(todas_tags))

                if tags_para_remover:
                    def limpar_tags(valor_celula):
                        if pd.isna(valor_celula): return ""
                        atuais = [t.strip() for t in str(valor_celula).split(',')]
                        novas = [t for t in atuais if t not in tags_para_remover and t != '']
                        return ",".join(novas)

                    if st.button("🗑️ Aplicar Limpeza"):
                        df_clean[col_tags] = df_clean[col_tags].apply(limpar_tags)
                        
                        st.success("Limpeza concluída!")
                        st.dataframe(df_clean.head())
                        
                        excel_clean = to_excel(df_clean)
                        st.download_button(
                            label="⬇️ Baixar Base Limpa",
                            data=excel_clean,
                            file_name="base_limpa.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            else:
                st.warning("Não encontrei coluna de Etiquetas.")
        except Exception as e:
            st.error(f"Erro: {e}")

# ==============================================================================
# ABA 3: COMPRESSOR DE PDF 
# ==============================================================================
with tab3:
    st.markdown("### 🗜️ Compressor de PDF")
    st.markdown("Reduza o tamanho de arquivos PDF pesados usando o motor **Ghostscript**.")

    uploaded_pdf = st.file_uploader("Solte seu PDF pesadão aqui", type=['pdf'])

    if uploaded_pdf is not None:
        original_size = uploaded_pdf.size / 1024 / 1024 # MB
        st.write(f"📁 Tamanho Original: **{original_size:.2f} MB**")

        st.divider()
        
        nivel = st.select_slider(
            "Escolha o nível de compressão:",
            options=["Extrema (Email)", "Média (Ebook)", "Alta Qualidade (Impressão)"],
            value="Média (Ebook)"
        )

        mapa_nivel = {
            "Extrema (Email)": 4,   
            "Média (Ebook)": 3,     
            "Alta Qualidade (Impressão)": 2 
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