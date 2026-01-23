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
# FUNÇÕES AUXILIARES
# ==============================================================================
def compress_pdf(input_file, power):
    """
    Níveis de compressão do Ghostscript:
    0: /default   - Quase nenhuma compressão
    1: /prepress  - Alta qualidade (300 dpi) - Arquivo maior
    2: /printer   - Qualidade de impressão (150 dpi) - Médio
    3: /ebook     - Qualidade média (150 dpi) - Bom para ler em tela
    4: /screen    - Qualidade baixa (72 dpi) - Menor tamanho possível (Email)
    """
    quality = {
        0: "/default",
        1: "/prepress",
        2: "/printer",
        3: "/ebook",
        4: "/screen"
    }
    
    # Cria arquivos temporários
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
        
        # Limpeza
        os.remove(input_path)
        os.remove(output_path)
        return compressed_data
    except Exception as e:
        st.error(f"Erro na compressão: {e}")
        return None

# ==============================================================================
# ABA 1: FORMATADOR
# ==============================================================================
with tab1:
    st.markdown("### Prepare planilhas para o BotConversa")
    # ... (CÓDIGO DA ABA 1 IGUAL AO ANTERIOR - PODE MANTER O SEU AQUI)
    # Vou resumir aqui para não ficar gigante, mas mantenha sua lógica de Pandas
    st.info("Aqui fica o seu formatador de contatos (Código da V6).")

# ==============================================================================
# ABA 2: LIMPADOR
# ==============================================================================
with tab2:
    st.markdown("### Limpar etiquetas de exportação")
    # ... (CÓDIGO DA ABA 2 IGUAL AO ANTERIOR)
    st.info("Aqui fica o seu limpador de etiquetas.")

# ==============================================================================
# ABA 3: COMPRESSOR DE PDF
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
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Tamanho Original", f"{original_size:.2f} MB")
                col2.metric("Novo Tamanho", f"{novo_tamanho:.2f} MB")
                col3.metric("Redução", f"{reducao:.1f}%", delta_color="normal")
                
                st.balloons()
                
                st.download_button(
                    label="⬇️ Baixar PDF Comprimido",
                    data=pdf_comprimido,
                    file_name=f"comprimido_{uploaded_pdf.name}",
                    mime="application/pdf",
                    type="primary"
                )