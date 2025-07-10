import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pandas as pd
import os

from constantes import TITULO_PRINCIPAL, TITULO_MAPA
from layout import output_layout

page_names = {
    "main.py": "Mapa de GCs",
    "lista_gc.py": "Lista de GCs"
}


# Configuração da página
st.set_page_config(
    page_title=TITULO_PRINCIPAL,
    page_icon=":earth_americas:",
    layout="wide"
)

# Aplicar layout padrão
output_layout()

# Título da aplicação
st.header(f":blue[{TITULO_PRINCIPAL}]")
st.subheader(f":orange[{TITULO_MAPA}]", divider="orange")

# Função para carregar os dados
@st.cache_data
def load_data():
    # Tenta carregar o arquivo da pasta local
    try:
        for file in os.listdir('.'):
            if file.endswith('.csv'):
                df = pd.read_csv(file)
                if all(col in df.columns for col in ['Latitude', 'Longitude', 'Endereço', 'Lideres', 'Tipo GC', 'Igreja Sede']):
                    # Filtrar apenas os registros com coordenadas válidas
                    return df.dropna(subset=['Latitude', 'Longitude'])
        
        # Se não encontrar nos arquivos listados, tenta especificamente o arquivo padrão
        df = pd.read_csv('lista_gc.csv')
        return df.dropna(subset=['Latitude', 'Longitude'])
    except:
        return pd.DataFrame()

# Carregar os dados
df = load_data()

if df.empty:
    st.warning("Não foi possível encontrar dados de pontos comerciais na pasta. Por favor, faça upload do arquivo.")
    uploaded_file = st.file_uploader("Faça upload do arquivo CSV com os GCs", type=['csv'])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        # Filtrar apenas os registros com coordenadas válidas
        df = df.dropna(subset=['Latitude', 'Longitude'])
        if df.empty:
            st.error("O arquivo não contém coordenadas válidas.")
        else:
            # Salvar arquivo localmente
            df.to_csv('lista_gc.csv', index=False)
            st.success("Arquivo carregado com sucesso!")
            st.experimental_rerun()
else:
    # Definir coordenadas centrais de Taubaté-SP
    taubate_lat = -23.0268
    taubate_lon = -45.5563
    
    # Criar mapa centralizado em Taubaté
    m = folium.Map(location=[taubate_lat, taubate_lon], zoom_start=12.5)
    
    # Definir cores por tipo de ponto
    color_map = {
        'Casal': 'green',
        'Feminino': 'pink',
        'Masculino': 'blue',
        'Jovens': 'orange',
        'Adolescentes': 'purple',
        'Misto': 'red'
    }
    
    # Adicionar todos os pontos ao mapa
    for idx, row in df.iterrows():
        color = color_map.get(row['Tipo GC'], 'gray')
        
        # Criar popup com informações
        popup_html = f'''
        <div style="width: 250px">
            <h4>{row['Endereço']}</h4>
            <b>Tipo:</b> {row['Tipo GC']}<br>
            <b>Líderes:</b> {row['Lideres']}<br>
            <b>Dia/Horário:</b> {row['Dia/Horário']}<br>
        </div>
        '''
        popup = folium.Popup(popup_html, max_width=300)
        
        # Adicionar marcador
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=popup,
            tooltip=row['Endereço'],
            icon=folium.Icon(color=color, icon="info-sign")
        ).add_to(m)
        
        # Adicionar círculo de cobertura de 1km
        folium.Circle(
            location=[row['Latitude'], row['Longitude']],
            radius=1000,  # 1km em metros
            color=color,
            fill=True,
            fill_opacity=0.1,
            weight=2,
            tooltip=f"{row['Lideres']}: {row['Endereço']}"
        ).add_to(m)
        
    # Exibir mapa
    folium_static(m, width=1100, height=500)
    
    # Interface para busca
    st.write("### Encontre o GC mais próximo")
    
    # Lado a lado: endereço e tipo de GC
    col1, col2 = st.columns([3, 1])
    
    with col1:
        address_input = st.text_input("Digite o endereço para pesquisa:", placeholder="Ex: Rua José Dias de Carvalho, 123")
    
    with col2:
        # Tipos de GC disponíveis para filtro
        tipos_gc = ["Todos"] + sorted(df['Tipo GC'].unique().tolist())
        tipo_selecionado = st.selectbox("Tipo de GC:", tipos_gc)

    
    # Botão de busca
    buscar = st.button("Buscar GC mais próximo", type="primary")
    
    
    
    # Processamento da busca
    if buscar and address_input:
        st.markdown('<hr>', unsafe_allow_html=True)
        
        # Geocodificar o endereço
        geolocator = Nominatim(user_agent="gc_mapping_app")
        
        try:
            # Adicionar ", Taubaté, SP, Brasil" para melhorar a precisão
            if "taubaté" not in address_input.lower():
                search_address = f"{address_input}, Taubaté, SP, Brasil"
            else:
                search_address = address_input
                
            location = geolocator.geocode(search_address)
            
            if location:
                input_lat = location.latitude
                input_lon = location.longitude
                
                # Filtrar por tipo se necessário
                df_filtered = df
                if tipo_selecionado != "Todos":
                    df_filtered = df[df['Tipo GC'] == tipo_selecionado]
                
                if df_filtered.empty:
                    st.warning(f"Não há pontos do tipo {tipo_selecionado} cadastrados.")
                else:
                    # Calcular distância para todos os pontos
                    distances = []
                    for idx, row in df_filtered.iterrows():
                        distance = geodesic(
                            (input_lat, input_lon),
                            (row['Latitude'], row['Longitude'])
                        ).kilometers
                        
                        distances.append({
                            'index': idx,
                            'distance': distance,
                            'endereço': row['Endereço'],
                            'tipo': row['Tipo GC'],
                            'líderes': row['Lideres'],
                            'dia_horário': row['Dia/Horário'],
                            'coordenação': row['Coordenação'],
                            'latitude': row['Latitude'],
                            'longitude': row['Longitude']
                        })
                    
                    # Ordenar por distância
                    distances.sort(key=lambda x: x['distance'])
                    
                    # Pegar o mais próximo
                    nearest = distances[0]
                    
                    # Mostrar resultado
                    st.success("### GC mais próximo encontrado")
                    st.info(f"**Endereço:** {nearest['endereço']}  \n**Líderes:** {nearest['líderes']}  \n**Tipo:** {nearest['tipo']}  \n**Dia/Horário:** {nearest['dia_horário']}  \n**Distância:** {nearest['distance']:.2f} km")
                    
                    # Verificar se está dentro da área de cobertura (2km)
                    if nearest['distance'] <= 2:
                        st.success("✅ Seu endereço está dentro da área de cobertura de 1km deste GC.")
                    else:
                        st.info("ℹ️ Seu endereço está fora da área de cobertura de 1km, mas este é o GC mais próximo.")
                    
                    # Criar mapa com o resultado
                    m_result = folium.Map(location=[input_lat, input_lon], zoom_start=14)
                    
                    # Adicionar marcador para o endereço pesquisado
                    folium.Marker(
                        location=[input_lat, input_lon],
                        popup="Seu endereço",
                        tooltip="Sua localização",
                        icon=folium.Icon(color="red", icon="home")
                    ).add_to(m_result)
                    
                    # Adicionar marcador para o GC mais próximo
                    color = color_map.get(nearest['tipo'], 'blue')
                    folium.Marker(
                        location=[nearest['latitude'], nearest['longitude']],
                        popup=f"{nearest['endereço']} - {nearest['líderes']}",
                        tooltip=f"GC mais próximo ({nearest['distance']:.2f} km)",
                        icon=folium.Icon(color=color, icon="info-sign")
                    ).add_to(m_result)
                    
                    # Desenhar linha entre o endereço pesquisado e o GC
                    folium.PolyLine(
                        locations=[[input_lat, input_lon], [nearest['latitude'], nearest['longitude']]],
                        color="blue",
                        weight=3,
                        opacity=0.7,
                        tooltip=f"Distância: {nearest['distance']:.2f} km"
                    ).add_to(m_result)
                    
                    # Desenhar círculo de cobertura
                    folium.Circle(
                        location=[nearest['latitude'], nearest['longitude']],
                        radius=1000,  # 1km em metros
                        color=color,
                        fill=True,
                        fill_opacity=0.1,
                        weight=2,
                        tooltip=f"Cobertura de 1km"
                    ).add_to(m_result)
                    
                    # Exibir mapa com o resultado
                    st.write("### Mapa do resultado")
                    folium_static(m_result, width=1100, height=600)
            else:
                st.error("Não foi possível encontrar o endereço. Tente ser mais específico ou incluir a cidade.")
        except Exception as e:
            st.error(f"Erro ao processar o endereço: {e}")
