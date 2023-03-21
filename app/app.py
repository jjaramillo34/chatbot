# Streamlit Timeline Component Example

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import openai
import math
from streamlit_timeline import timeline
from streamlit_option_menu import option_menu
from pyecharts import options as opts
from pyecharts import options as opts
from streamlit_echarts import st_echarts, st_pyecharts
from pyecharts.charts import Pie, Bar, PictorialBar, Line, Grid, Page, Tab, Timeline, Graph
import geopandas as gpd

# import mongo db
from utils import insert_data, get_data_by_municipio, get_all

#millnames = ['',' Thousand',' Million',' Billion',' Trillion']
millnames = ['',' miles',' millónes',' billónes',' trillónes']

# use full page width
st.set_page_config(page_title="Timeline Example", layout="wide")

openai.api_key = st.secrets['openai']['OPENAI_API_KEY']

def millify(n):
    n = float(n)
    millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

    return '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx])

def load_data():
    df = pd.read_csv("./app/new_data.csv", encoding="utf-8")
    return df

def generate_description(prompt):
    response = openai.Completion.create(
    model="text-davinci-003",
    prompt=prompt,
    #prompt="Pequena description acerca de Aguas Buenas puerto rico municipio\n\nAguas Buenas es el segundo municipio más grande de Puerto Rico, siendo el más oriental de la Isla. Ubicado a una hora al este de San Juan, el municipio está rodeado por una gran cantidad de ríos y arroyos, y tiene una gran cantidad de bosques y colinas. Aguas Buenas es uno de los municipios de Puerto Rico con una gran diversidad cultural, con una población que abarca desde descendientes de españoles y de africanos hasta los descendientes de los habitantes aborígenes y mestizos. La ciudad se encuentra en la parte central del municipio, y es el lugar donde los habitantes acuden a disfrutar de la gastronomía local, celebrar festivales, y también de encuentros deportivos. El municipio alberga algunos de los atractivos turísticos más destacados de Puerto Rico, como el Cerro Buenas y el Mirador del Anquito. También se encuentran aquí algunas de las mejores playas de la Isla, como la Playa de los Vientos.",
    temperature=0.85,
    max_tokens=1980,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
)
    if response["choices"]:
        return response["choices"][0]["text"]
    else:
        return None

st.markdown("""
<style>
div[data-testid="metric-container"] {
   background-color: rgba(28, 131, 225, 0.1);
   border: 1px solid rgba(28, 131, 225, 0.1);
   padding: 5% 5% 5% 10%;
   border-radius: 5px;
   color: rgb(30, 103, 119);
   overflow-wrap: break-word;
}

/* breakline for metric text         */
div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
   overflow-wrap: break-word;
   white-space: break-spaces;
   color: red;
}

.span.ti {
    
}


</style>
"""
, unsafe_allow_html=True)

arrows = """
<div class="arrow-right"></div>
"""

def timeline_show():
    # dataframe with events
    df = load_data()

    #st.dataframe(df.head())
    unique_municipios = df["municipio_new"].unique()
    sorted_municipios = sorted(unique_municipios)
    #print(sorted_municipios)
    municipio = st.sidebar.selectbox("Municipio", sorted_municipios)

    # filter dataframe by selected diseno
    df = df[df["municipio_new"] == municipio]

    st.title("Todos por Puerto Rico - Pipeline de datos de Proyectos")

    cols = st.columns(4)
    # important dashboard metrics
    with cols[0]:
        st.metric("Total de Proyectos", df["municipio"].count())
    #with cols[1]:
        #st.markdown(arrows, unsafe_allow_html=True)
    with cols[1]:
        st.metric("Total de Proyectos en Construcción", df[df["diseno"] == "Completados"]["municipio"].count())
        #st.metric("Total de Proyectos Completados", df[df["diseno"] == "Completados"].count())
    with cols[2]:
        st.metric("Total Costo de Proyectos", "$" + format(df["costo"].sum(), ",d"))
    with cols[3]:
        st.metric("Total Costo de Proyectos Completados", "$" + format(df[df["diseno"] == "Completados"]["costo"].sum(), ",d"))

    # create timeline
    events = [{
        "media": {
            "url": row["image"],
            "caption": row["caption"],
            "credit": "Todos por Puerto Rico",
        },
        "start_date": {
            "year": row["year"],
            "month": row["month"],    
        },
        "text": {
            "headline": f"""<div>
                    <img src="{row['icon']}" width="18" height="18" />
            """,
            "text": f"""<p style="font-size: 20px; font-weight: bold; color: #BE9750">{row["caption"]}</p>
            <p>
            <b>Costo:</b> ${format(row["costo"], ",d")}
            <br><b style="font-weight: bold">Fecha de Inicio:</b> {row["date"]}
            <br><b>Estado:</b> {row["diseno"]}
            <br><b>Municipio:</b> {row["municipio_new"]}
            <br><b>Tragedia:</b> {row["tragedia"]}
            <br><b>Sector:</b> {row["sector"]}
            <br><b>Categoría:</b> {row["categoria"]}
            <br><b>Tamaño:</b> {row["tamano"]}
            <br><b>Sector:</b> {row["sector"]}
            <br>
            </p> 
            """
        }
    } for index, row in df.iterrows()]

    #print(events)

    timeline_json = {
        "title": {
            "media": {
            "url": "https://www.elnuevodia.com/resizer/7XT2pZ6qrm6JeRrQhvd4Q3oeixo=/arc-anglerfish-arc2-prod-gfrmedia/public/DVWPMSDP6JDB3DMYLUAZEHCG4I.png",
            #"caption": " <a target=\"_blank\" href=''>credits</a>",
            "credit": "Todos por Puerto Rico"
            },
            "text": {
            "headline": "Todos por Puerto Rico <br> Pipeline de datos de Proyectos",
            "text": "<p> Trabajando para con todos Puerto Rico</p>"
            }
        },
        "events": events
    }

    timeline(timeline_json, height=800)
    
def mapa():
    st.title("Mapa de Proyectos")
    st.markdown("Mapa de Proyectos")
    
    df = load_data()
    unique_municipios = df["municipio2"].unique()
    sorted_municipios = sorted(unique_municipios)
    #print(sorted_municipios)
    municipio = st.sidebar.selectbox("Municipio", sorted_municipios)
    # filter dataframe by selected diseno
    df = df[df["municipio2"] == municipio]

    # lat and log columns dataframe
    df = df[['lat', 'log', 'costo', 'diseno', 'municipio_new', 'caption', 'sector']]
    df = df.rename(columns={'lat': 'lat', 'log': 'lon'})
    df.dropna(inplace=True)
    
    # sort df by costo
    df = df.sort_values(by=['costo'], ascending=False)
    
    start_lat = df['lat'].mean()
    start_lon = df['lon'].mean()
    
    usa = gpd.read_file('./app/cb_2013_us_county_500k.geojson')
    json_municipio = usa[usa['Name'] == municipio]
    
    print(json_municipio)
    
    centroids = gpd.GeoDataFrame()
    centroids["geometry"] = json_municipio.geometry.centroid
    centroids["Name"] = json_municipio.Name

    print(len(df))
    print(df.head())
    cols = st.columns([0.65, 0.35])
    with cols[0]:
        st.subheader("Mapa de Proyectos")
        tooltip={"text": "{position}\nCount: {count}\n Costo: ${costo}"}
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            tooltip=tooltip,
            initial_view_state=pdk.ViewState(
                latitude=start_lat,
                longitude=start_lon,
                zoom=11,
                pitch=50,
                #bearing=0,
                
            ),
            layers=[
                pdk.Layer(
                'GridLayer',
                data=df,
                get_position='[lon, lat]',
                radius=20,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
                cell_size=200,
                #tooltip={'html': '<b>Municipio:</b> {municipio_new} <br> <b>Costo:</b> ${costo}'},
                ),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=df,
                    get_position='[lon, lat]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=2,
                    opacity=0.5,
                    #tooltip={'html': '<b>Municipio:</b> {municipio_new} <br> <b>Costo:</b> ${costo}'},
                ),
                pdk.Layer(
                    'GeoJsonLayer',
                    data=json_municipio,
                    get_fill_color=[0, 0, 0, 100],
                ),
                pdk.Layer(
                    'TextLayer',
                    data=centroids,
                    get_position="geometry.coordinates",
                    get_size=16,
                    get_color=[255, 255, 255],
                    get_text="Name",
                    get_angle=0,
                ),
            ],
        ))
    #st.dataframe(df)
    
    with cols[1]:
        st.subheader("Descripción")
        #promt = f"Pequeño resumen de los proyectos en construcción en el municipio de {municipio} en Puerto Rico"
        prompt = f"Pequena description de municipio {municipio} puerto rico municipio y wikipedia link"
        
        top_3_sector = df.groupby('sector')['costo'].sum().reset_index().sort_values(by='costo', ascending=False).head(3)
        
        sum_municipio = df.groupby('municipio_new')['costo'].sum().reset_index()
        #mean_municipio = df.groupby('municipio_new')['costo'].mean().reset_index()
        average_municipio = df.groupby('municipio_new')['costo'].mean().reset_index()
        
        sum_words = millify(sum_municipio['costo'][0])
        ave_words = millify(average_municipio['costo'][0])
        
        top_3 = top_3_sector.to_dict('records')
        
        print(top_3_sector)
        print(top_3_sector.to_dict('records'))
        
        template = f"""El municipio de {municipio} despues de los huracanes Irma, Maria y el Terremoto ha tenido un total de {len(df)} proyectos de reconstrucción. 
                    El costo total de los proyectos es de aproximadamente {sum_words} de  dolares y el costo promedio de los proyectos es de {ave_words}  dolares.
                    La mayor parte de los proyectos se encuentran en los sectores de {top_3[0]['sector']} con {millify(top_3[0]['costo'])} dolares,
                    {top_3[1]['sector']} con {millify(top_3[1]['costo'])}, and {top_3[2]['sector']} con {millify(top_3[2]['costo'])} dolares.
                    """
        #
        #template += f"\nTotal Cost: ${sum_municipio['costo'][0]:,.2f}"
        #template += f"\nMean Cost: ${mean_municipio['costo'][0]:,.2f}"
        #template += f"\nTotal Projects: {len(df)}"
        #st.markdown(template, unsafe_allow_html=True)
        
        try:
            municipio_exist = get_data_by_municipio(municipio)
            #print(municipio_exist['municipio'])
            if municipio == municipio_exist['municipio']:
                print("municipio exist")
                template += municipio_exist['description']
            else:
                ai = generate_description(prompt)
                insert_data(municipio, ai, '2023-03-19')
                template += ai
        except Exception as e:
            print(e)
            ai = generate_description(prompt)
            insert_data(municipio, ai, '2023-03-19')
            template += ai
            
        
        st.markdown(template)    
            
        #st.write(ai_test)
        st.write("Powered by OpenAI GPT-3 and Todos por Puerto Rico")
                        
        
def dashboard():
    st.title("Dashboard")
    st.markdown("Dashboard")
    df = load_data()
    #print(df)
    unique_municipios = df["diseno"].unique()
    sorted_municipios = sorted(unique_municipios)
    municipio = st.sidebar.selectbox("Municipio", sorted_municipios)
    
    df_filter = df[df["diseno"] == municipio]
    print(df_filter)
    df_filter.groupby('diseno')['costo'].count().nlargest(20).reset_index()
    
    df_test = df_filter.groupby('municipio_new')['costo'].count().nlargest(20).reset_index()
    text_count = list(df_test.itertuples(index=False, name=None))
        
    cols = st.columns(2)

    data = [{"name": name, "value": value} for name, value in text_count]
    
    print(data)
    
    with cols[0]:
        st.markdown("### TDPR Word Cloud")
        wordcloud_option = {"series": [{"type": "wordCloud", "data": data}]}
        st_echarts(wordcloud_option)
        
    nodes = [{"name": name, "symbolSize": value/100} for name, value in text_count]
    
    links = []
    for i in nodes:
        for j in nodes:
            links.append({"source": i.get("name"), "target": j.get("name")})
    c = (
        Graph()
        .add("", nodes, links, repulsion=8000)
        .set_global_opts(title_opts=opts.TitleOpts(title="Count of Municipios"))
    )

    with cols[1]:
        st.markdown("### Count of Municipios")
        st_pyecharts(c)
    
if __name__ == "__main__":
    menu_options = ['Timeline', 'Mapa', 'Dashboard', 'About']
    menu_icons = ['cast', 'map', 'dashboard', 'info']
    selected2 = option_menu(None, menu_options, 
    icons=menu_icons, menu_icon="cast", default_index=0, orientation="horizontal")

    if selected2 == "Timeline":
        timeline_show()
    elif selected2 == "Mapa":
        mapa()
    elif selected2 == "Dashboard":
        dashboard()





