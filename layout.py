import streamlit as st
import base64
import os

def carregar_imagem(caminho_imagem):
    # Carrega uma imagem e retorna como base64
    if os.path.exists(caminho_imagem):
        with open(caminho_imagem, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

def exibir_imagem_header(caminho_imagem, largura=200):
    # Exibe a imagem no header
    img_base64 = carregar_imagem(caminho_imagem)
    if img_base64:
        st.markdown(
            f'<div style="display: flex; justify-content: center;"><img src="data:image/jpeg;base64,{img_base64}" width="{largura}"></div>',
            unsafe_allow_html=True
        )
    else:
        st.warning(f"Imagem não encontrada: {caminho_imagem}")

def output_layout():
    
    # Configurar o menu de navegação na barra lateral
    with st.sidebar:
        exibir_imagem_header("diamante_branco.jpg", largura=150)
        
        
        # Determinar o script atual
        is_main = "main.py" in st.experimental_get_query_params().get("page", ["main.py"])[0]
        is_lista = "lista_gc.py" in st.experimental_get_query_params().get("page", [""])[0]
        
        
        # Informações adicionais
        st.subheader("Informações")
        st.info(
            "Esta aplicação permite visualizar os GCs no mapa e "
            "encontrar o GC mais próximo do seu endereço."
        )
        
        st.subheader("Cobertura")
        st.info("Cada GC tem um raio de cobertura de 1km.")
