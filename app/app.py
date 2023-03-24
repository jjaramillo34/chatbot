# Streamlit Timeline Component Example

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import openai
import math
import json
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
millnames = ['',' mil',' millónes',' billónes',' trillónes']

# use full page width
st.set_page_config(page_title="Timeline Example", layout="wide")

openai.api_key = st.secrets['openai']['OPENAI_API_KEY']

def millify(n):
    n = float(n)
    millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

    return '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx])

def load_data():
    df = pd.read_csv("./app/new_data copy.csv", encoding="utf-8")
    return df

def generate_integer(n):
    if n < 1:
        raise ValueError("n must be >= 1")
    return int('1' * n)

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

    #cols = st.columns(4)
    ## important dashboard metrics
    #with cols[0]:
    #    st.metric("Total de Proyectos", df["municipio"].count())
    ##with cols[1]:
    #    #st.markdown(arrows, unsafe_allow_html=True)
    #with cols[1]:
    #    st.metric("Total de Proyectos en Construcción", df[df["diseno"] == "Completados"]["municipio"].count())
    #    #st.metric("Total de Proyectos Completados", df[df["diseno"] == "Completados"].count())
    #with cols[2]:
    #    st.metric("Total Costo de Proyectos", "$" + format(df["costo"].sum(), ",d"))
    #with cols[3]:
    #    st.metric("Total Costo de Proyectos Completados", "$" + format(df[df["diseno"] == "Completados"]["costo"].sum(), ",d"))

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
            "headline": "Pipeline de datos de Proyectos",
            "text": "<p> Trabajando para con todos Puerto Rico</p>"
            }
        },
        "events": events
    }

    timeline(timeline_json, height=800)
    
def mapa():
    
    df = load_data()
    total_costo = df["costo"].sum()
    total_count = df["municipio2"].count()
    unique_municipios = df["municipio2"].unique()
    sorted_municipios = sorted(unique_municipios)
    #print(sorted_municipios)
    st.sidebar.title("Filter by Municipio")
    #municipio = st.sidebar.selectbox("Municipio", sorted_municipios)
    municipio = st.sidebar.selectbox("Por favor seleccione un municipio", sorted_municipios)
    # filter dataframe by selected diseno
    df = df[df["municipio2"] == municipio]
    #print(df)

    # lat and log columns dataframe
    df = df[['lat', 'log', 'costo', 'diseno', 'municipio_new', 'caption', 'title', 'sector', 'costo_ele', "municipio2", "tragedia", "categoria", "tamano", "image", "icon", "year", "month", "date", "precio"]]
    df = df.rename(columns={'lat': 'lat', 'log': 'lon'})
    df.dropna(inplace=True)
    
    # sort df by costo
    df = df.sort_values(by=['costo'], ascending=False)
    
    start_lat = df['lat'].mean()
    start_lon = df['lon'].mean()
    
    usa = gpd.read_file('./app/cb_2013_us_county_500k.geojson')
    usa = usa[usa['LSAD'] == '13']
    json_municipio = usa[usa['Name'] == municipio]
    json_municipio = json_municipio.to_crs("EPSG:4326")
    centroids = gpd.GeoDataFrame()
    centroids["geometry"] = json_municipio.geometry.centroid
    centroids["Name"] = json_municipio.Name

    cols = st.columns(4)
    total_costo_proyectos = "$" + format(df["costo"].sum(), ",d")
    delta1 = (df["costo"].sum() / total_costo) * 100
    cols[0].metric("Costo Total de Proyectos", total_costo_proyectos, delta=f"% {str(round(delta1, 2))} del costo total de proyectos en la isla.")
    total_proyectos = df["municipio2"].count()
    delta2 = (df["municipio2"].count() / total_count) * 100
    cols[1].metric("Total de Proyectos", total_proyectos, delta=f"% {str(round(delta2, 2))} del total de proyectos en la isla.")
    total_proyectos_completados = df[df["diseno"] == "Completado"]["municipio2"].count()
    delta3 = (df[df["diseno"] == "Completado"]["municipio2"].count() / total_proyectos) * 100
    cols[3].metric("Total de Proyectos Completados", total_proyectos_completados, delta=f"% {str(round(delta3, 2))} de los proyectos en {municipio}.")
    total_costo_proyectos_completados = "$" + format(df[df["diseno"] == "Completado"]["costo"].sum(), ",d")
    delta4 = (df[df["diseno"] == "Completado"]["costo"].sum() / df['costo'].sum()) * 100
    cols[2].metric("Costo Total de Proyectos Completados", total_costo_proyectos_completados, delta=f"% {str(round(delta4, 2))} de la inversion total en {municipio}.")
    
    cols = st.columns([0.70, 0.30])
    
    with cols[0]:
        st.subheader("Mapa de Proyectos")        
        st.pydeck_chart(pdk.Deck(
            
            map_style='mapbox://styles/mapbox/light-v9',
            #costo=0,
            tooltip={
                'html': '<h5>{caption}</h5> <br> <b>Costo del Proyecto: </b> {precio} <br> <b>Estado: </b> {diseno} <br> <b>Municipio: </b> {municipio2} <br> <b>Proyecto: </b> {title} <br> <b>Sector: </b> {sector}',
                'style': {
                    'backgroundColor': 'steelblue',
                    'color': 'white',
                    'font-family': 'Helvetica Neue, Helvetica, Arial, sans-serif',
                    'font-size': '14px',
                    'padding': '10px',
                    'border-radius': '10px',
                    'border': '1px solid #ccc',
                }
            },
            initial_view_state=pdk.ViewState(
                latitude=start_lat,
                longitude=start_lon,
                zoom=10,
                pitch=50,
                #bearing=0,
            ),
            layers=[
                pdk.Layer(
                    'ColumnLayer',
                    data=df,
                    get_position=["lon", "lat"],
                    get_color='[200, 30, 0, 160]',
                    get_elevation='costo_ele',
                    elevation_scale=100,
                    get_fill_color='[100, 30, 0, 160]',
                    get_line_color='[100, 30, 0, 160]',
                    #elevation_range=[0, 10000000],
                    size_scale=10,
                    radius=50,
                    pickable=True,
                    extruded=True,
                    cell_size=200,
                    #auto_highlight=True,
                ),
                pdk.Layer(
                    "GridLayer",
                    data=df,
                    get_position=["lon", "lat"],
                    get_color='[20, 30, 0, 160]',
                    elevation_scale=50,
                    elevation_range=[0, 100],
                    size_scale=int(5),
                    radius=int(20),
                    #pickable=True,
                    #extruded=bool(True),
                    auto_highlight=True,
                    
                ),
                pdk.Layer(
                    'ScatterplotLayer',
                    data=df,
                    get_position='[lon, lat]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=0,
                    opacity=0.5,
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
                    get_size=14,
                    get_color=[255, 255, 255],
                    get_text="Name",
                    get_angle=0,
                ),
                
            ],
        ))
    
    with cols[1]:
        st.subheader("Descripción")
        #promt = f"Pequeño resumen de los proyectos en construcción en el municipio de {municipio} en Puerto Rico"
        prompt = f"Pequena description de municipio {municipio} puerto rico municipio y wikipedia link"
        
        top_3_sector = df.groupby('sector')['costo'].sum().reset_index().sort_values(by='costo', ascending=False).head(3)
        
        sum_municipio = df.groupby('municipio2')['costo'].sum().reset_index()
        #mean_municipio = df.groupby('municipio_new')['costo'].mean().reset_index()
        average_municipio = df.groupby('municipio2')['costo'].mean().reset_index()
        
        sum_words = millify(sum_municipio['costo'][0])
        ave_words = millify(average_municipio['costo'][0])
        
        #st.write(sum_municipio, sum_words)
        #st.write(average_municipio, ave_words)
        
        top_3 = top_3_sector.to_dict('records')
        
        print(top_3_sector)
        print(top_3_sector.to_dict('records'))
        
        template = f"""El municipio de {municipio} despues de los huracanes Irma, Maria y el Terremoto ha tenido un total de {len(df)} proyectos de reconstrucción. 
                    El costo total de los proyectos es de aproximadamente {sum_words} de  dolares y el costo promedio de los proyectos es de {ave_words} dolares.
                    La mayor parte de los proyectos se encuentran en los sectores de {top_3[0]['sector']} con {millify(top_3[0]['costo'])} dolares,
                    {top_3[1]['sector']} con {millify(top_3[1]['costo'])}, y {top_3[2]['sector']} con {millify(top_3[2]['costo'])} dolares.
                    """
                    
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
    #print(df_filter)
    df_filter.groupby('diseno')['costo'].count().nlargest(20).reset_index()
    
    #df_test = df_filter.groupby('municipio_new')['costo'].count().nlargest(20).reset_index()
    #text_count = list(df_test.itertuples(index=False, name=None))
    #    
    #cols = st.columns(2)

    #data = [{"name": name, "value": value} for name, value in text_count]
    #
    #print(data)
    #
    #with cols[0]:
    #    st.markdown("### TDPR Word Cloud")
    #    wordcloud_option = {"series": [{"type": "wordCloud", "data": data}]}
    #    st_echarts(wordcloud_option)
    #    
    #nodes = [{"name": name, "symbolSize": value/100} for name, value in text_count]
    #
    #links = []
    #for i in nodes:
    #    for j in nodes:
    #        links.append({"source": i.get("name"), "target": j.get("name")})
    #c = (
    #    Graph()
    #    .add("", nodes, links, repulsion=8000)
    #    .set_global_opts(title_opts=opts.TitleOpts(title="Count of Municipios"))
    #)

    #with cols[1]:
    #    st.markdown("### Count of Municipios")
    #    st_pyecharts(c)
        
    #st.dataframe(df_filter)
    
    pathSymbols = {
    "Agua": "path://M16.0001 13.3848C16.0001 14.6088 15.526 15.7828 14.6821 16.6483C14.203 17.1397 13.6269 17.5091 13 17.7364M19 13.6923C19 7.11538 12 2 12 2C12 2 5 7.11538 5 13.6923C5 15.6304 5.7375 17.4893 7.05025 18.8598C8.36301 20.2302 10.1436 20.9994 12.0001 20.9994C13.8566 20.9994 15.637 20.2298 16.9497 18.8594C18.2625 17.4889 19 15.6304 19 13.6923Z",
    "Edificios Públicos": "path://M7.743 21.8h3.485v22.4h5.229v-19.2h5.229v19.2h5.228v-19.2h5.23v19.2h5.229v-22.4h3.484c.963 0 1.744-.716 1.744-1.6 0-.534-.288-1.004-.727-1.294l.003-.003-.026-.015-.045-.027-16.635-8.609v-2.522c3.072 1.412 5.601-1.02 9.585.442v-5.571c-3.986-1.462-6.514.968-9.585-.443v-.358c0-.443-.389-.8-.871-.8s-.87.357-.87.8v8.452l-16.635 8.607-.045.027-.025.017v.003c-.437.29-.724.761-.724 1.294-.001.884.78 1.6 1.742 1.6zm1.742 24.001l-3.485 3.199h36.602l-3.487-3.199z",
    "Educación": "path://m 12.499079,12.25525 c 0.0968,0 0.188377,-0.0436 0.249339,-0.11884 0.06096,-0.0752 0.08473,-0.17385 0.06473,-0.26853 l -0.202146,-0.95662 c 0.115125,-0.11137 0.187491,-0.26686 0.187491,-0.43975 0,-0.182 -0.08106,-0.34343 -0.206876,-0.45558 l 0,-3.32202 -0.810333,0.50146 0,2.82056 c -0.125815,0.11215 -0.2069,0.27358 -0.2069,0.45558 0,0.17291 0.07239,0.32841 0.187515,0.43975 l -0.20217,0.95662 c -0.02,0.0947 0.0038,0.19335 0.06473,0.26853 0.06096,0.0752 0.152539,0.11884 0.249339,0.11884 l 0.625281,0 z M 12.773741,4.75539 7.5021019,1.49209 C 7.3477151,1.39699 7.1736728,1.34925 6.9996305,1.34925 c -0.1740423,0 -0.3482077,0.0477 -0.5016586,0.14284 l -5.271713,3.2633 C 1.0854931,4.84249 0.99999905,4.99633 0.99999905,5.1619 c 0,0.1656 0.085494,0.31949 0.22625985,0.40673 l 5.2716883,3.26333 c 0.153451,0.0952 0.3276163,0.14284 0.5016586,0.14284 0.1740423,0 0.3481092,-0.0477 0.5024714,-0.14284 L 12.773741,5.56863 c 0.140766,-0.0872 0.22626,-0.24113 0.22626,-0.40673 0,-0.16557 -0.08549,-0.31946 -0.22626,-0.40651 z M 6.9996059,9.78508 c -0.3283798,0 -0.6488777,-0.0912 -0.928242,-0.26411 l -3.0750017,-1.90368 0,3.27796 c 0,0.97016 1.7931578,1.7555 4.0032436,1.7555 2.2108742,0 4.0038842,-0.78536 4.0038842,-1.7555 l 0,-3.27796 -3.0748786,1.90368 C 7.6492472,9.69388 7.3279857,9.78508 6.9996059,9.78508 Z",
    "Energía": "path://M16.678,17.086h9.854l-2.703,5.912c5.596,2.428,11.155,5.575,16.711,8.607c3.387,1.847,6.967,3.75,10.541,5.375 v-6.16l-4.197-2.763v-5.318L33.064,12.197h-11.48L20.43,15.24h-4.533l-1.266,3.286l0.781,0.345L16.678,17.086z M49.6,31.84 l0.047,1.273L27.438,20.998l0.799-1.734L49.6,31.84z M33.031,15.1l12.889,8.82l0.027,0.769L32.551,16.1L33.031,15.1z M22.377,14.045 h9.846l-1.539,3.365l-2.287-1.498h1.371l0.721-1.352h-2.023l-0.553,1.037l-0.541-0.357h-0.34l0.359-0.684h-2.025l-0.361,0.684 h-3.473L22.377,14.045z M23.695,20.678l-0.004,0.004h0.004V20.678z M24.828,18.199h-2.031l-0.719,1.358h2.029L24.828,18.199z  M40.385,34.227c-12.85-7.009-25.729-14.667-38.971-12.527c1.26,8.809,9.08,16.201,8.213,24.328 c-0.553,4.062-3.111,0.828-3.303,7.137c15.799,0,32.379,0,48.166,0l0.066-4.195l1.477-7.23 C50.842,39.812,45.393,36.961,40.385,34.227z M13.99,35.954c-1.213,0-2.195-1.353-2.195-3.035c0-1.665,0.98-3.017,2.195-3.017 c1.219,0,2.195,1.352,2.195,3.017C16.186,34.604,15.213,35.954,13.99,35.954z M23.691,20.682h-2.02l-0.588,1.351h2.023 L23.691,20.682z M19.697,18.199l-0.721,1.358h2.025l0.727-1.358H19.697z",
    "Municipios": "path://M49.592,40.883c-0.053,0.354-0.139,0.697-0.268,0.963c-0.232,0.475-0.455,0.519-1.334,0.475 c-1.135-0.053-2.764,0-4.484,0.068c0,0.476,0.018,0.697,0.018,0.697c0.111,1.299,0.697,1.342,0.931,1.342h3.7 c0.326,0,0.628,0,0.861-0.154c0.301-0.196,0.43-0.772,0.543-1.78c0.017-0.146,0.025-0.336,0.033-0.56v-0.01 c0-0.068,0.008-0.154,0.008-0.25V41.58l0,0C49.6,41.348,49.6,41.09,49.592,40.883L49.592,40.883z M6.057,40.883 c0.053,0.354,0.137,0.697,0.268,0.963c0.23,0.475,0.455,0.519,1.334,0.475c1.137-0.053,2.762,0,4.484,0.068 c0,0.476-0.018,0.697-0.018,0.697c-0.111,1.299-0.697,1.342-0.93,1.342h-3.7c-0.328,0-0.602,0-0.861-0.154 c-0.309-0.18-0.43-0.772-0.541-1.78c-0.018-0.146-0.027-0.336-0.035-0.56v-0.01c0-0.068-0.008-0.154-0.008-0.25V41.58l0,0 C6.057,41.348,6.057,41.09,6.057,40.883L6.057,40.883z M49.867,32.766c0-2.642-0.344-5.224-0.482-5.507 c-0.104-0.207-0.766-0.749-2.271-1.773c-1.522-1.042-1.487-0.887-1.766-1.566c0.25-0.078,0.492-0.224,0.639-0.241 c0.326-0.034,0.345,0.274,1.023,0.274c0.68,0,2.152-0.18,2.453-0.48c0.301-0.303,0.396-0.405,0.396-0.672 c0-0.268-0.156-0.818-0.447-1.146c-0.293-0.327-1.541-0.49-2.273-0.585c-0.729-0.095-0.834,0-1.022,0.121 c-0.304,0.189-0.32,1.919-0.32,1.919l-0.713,0.018c-0.465-1.146-1.11-3.452-2.117-5.269c-1.103-1.979-2.256-2.599-2.737-2.754 c-0.474-0.146-0.904-0.249-4.131-0.576c-3.298-0.344-5.922-0.388-8.262-0.388c-2.342,0-4.967,0.052-8.264,0.388 c-3.229,0.336-3.66,0.43-4.133,0.576s-1.633,0.775-2.736,2.754c-1.006,1.816-1.652,4.123-2.117,5.269L9.87,23.109 c0,0-0.008-1.729-0.318-1.919c-0.189-0.121-0.293-0.225-1.023-0.121c-0.732,0.104-1.98,0.258-2.273,0.585 c-0.293,0.327-0.447,0.878-0.447,1.146c0,0.267,0.094,0.379,0.396,0.672c0.301,0.301,1.773,0.48,2.453,0.48 c0.68,0,0.697-0.309,1.023-0.274c0.146,0.018,0.396,0.163,0.637,0.241c-0.283,0.68-0.24,0.524-1.764,1.566 c-1.506,1.033-2.178,1.566-2.271,1.773c-0.139,0.283-0.482,2.865-0.482,5.508s0.189,5.02,0.189,5.86c0,0.354,0,0.976,0.076,1.565 c0.053,0.354,0.129,0.697,0.268,0.966c0.232,0.473,0.447,0.516,1.334,0.473c1.137-0.051,2.779,0,4.477,0.07 c1.135,0.043,2.297,0.086,3.33,0.11c2.582,0.051,1.826-0.379,2.928-0.36c1.102,0.016,5.447,0.196,9.424,0.196 c3.976,0,8.332-0.182,9.423-0.196c1.102-0.019,0.346,0.411,2.926,0.36c1.033-0.018,2.195-0.067,3.332-0.11 c1.695-0.062,3.348-0.121,4.477-0.07c0.886,0.043,1.103,0,1.332-0.473c0.132-0.269,0.218-0.611,0.269-0.966 c0.086-0.592,0.078-1.213,0.078-1.565C49.678,37.793,49.867,35.408,49.867,32.766L49.867,32.766z M13.219,19.735 c0.412-0.964,1.652-2.9,2.256-3.244c0.145-0.087,1.426-0.491,4.637-0.706c2.953-0.198,6.217-0.276,7.73-0.276 c1.513,0,4.777,0.078,7.729,0.276c3.201,0.215,4.502,0.611,4.639,0.706c0.775,0.533,1.842,2.28,2.256,3.244 c0.412,0.965,0.965,2.858,0.861,3.116c-0.104,0.258,0.104,0.388-1.291,0.275c-1.387-0.103-10.088-0.216-14.185-0.216 c-4.088,0-12.789,0.113-14.184,0.216c-1.395,0.104-1.188-0.018-1.291-0.275C12.254,22.593,12.805,20.708,13.219,19.735 L13.219,19.735z M16.385,30.511c-0.619,0.155-0.988,0.491-1.764,0.482c-0.775,0-2.867-0.353-3.314-0.371 c-0.447-0.017-0.842,0.302-1.076,0.362c-0.23,0.06-0.688-0.104-1.377-0.318c-0.688-0.216-1.092-0.155-1.316-1.094 c-0.232-0.93,0-2.264,0-2.264c1.488-0.068,2.928,0.069,5.621,0.826c2.693,0.758,4.191,2.213,4.191,2.213 S17.004,30.357,16.385,30.511L16.385,30.511z M36.629,37.293c-1.23,0.164-6.386,0.207-8.794,0.207c-2.412,0-7.566-0.051-8.799-0.207 c-1.256-0.164-2.891-1.67-1.764-2.865c1.523-1.627,1.24-1.576,4.701-2.023C24.967,32.018,27.239,32,27.834,32 c0.584,0,2.865,0.025,5.859,0.404c3.461,0.447,3.178,0.396,4.699,2.022C39.521,35.623,37.887,37.129,36.629,37.293L36.629,37.293z  M48.129,29.582c-0.232,0.93-0.629,0.878-1.318,1.093c-0.688,0.216-1.145,0.371-1.377,0.319c-0.231-0.053-0.627-0.371-1.074-0.361 c-0.448,0.018-2.539,0.37-3.313,0.37c-0.772,0-1.146-0.328-1.764-0.481c-0.621-0.154-0.966-0.154-0.966-0.154 s1.49-1.464,4.191-2.213c2.693-0.758,4.131-0.895,5.621-0.826C48.129,27.309,48.361,28.643,48.129,29.582L48.129,29.582z",
    "Recursos Naturales y Culturales": "path://M16.0001 13.3848C16.0001 14.6088 15.526 15.7828 14.6821 16.6483C14.203 17.1397 13.6269 17.5091 13 17.7364M19 13.6923C19 7.11538 12 2 12 2C12 2 5 7.11538 5 13.6923C5 15.6304 5.7375 17.4893 7.05025 18.8598C8.36301 20.2302 10.1436 20.9994 12.0001 20.9994C13.8566 20.9994 15.637 20.2298 16.9497 18.8594C18.2625 17.4889 19 15.6304 19 13.6923Z",
    "Salud y Servicios Sociales": "path://M16.0001 13.3848C16.0001 14.6088 15.526 15.7828 14.6821 16.6483C14.203 17.1397 13.6269 17.5091 13 17.7364M19 13.6923C19 7.11538 12 2 12 2C12 2 5 7.11538 5 13.6923C5 15.6304 5.7375 17.4893 7.05025 18.8598C8.36301 20.2302 10.1436 20.9994 12.0001 20.9994C13.8566 20.9994 15.637 20.2298 16.9497 18.8594C18.2625 17.4889 19 15.6304 19 13.6923Z",
    "Transportación": "path://M16.0001 13.3848C16.0001 14.6088 15.526 15.7828 14.6821 16.6483C14.203 17.1397 13.6269 17.5091 13 17.7364M19 13.6923C19 7.11538 12 2 12 2C12 2 5 7.11538 5 13.6923C5 15.6304 5.7375 17.4893 7.05025 18.8598C8.36301 20.2302 10.1436 20.9994 12.0001 20.9994C13.8566 20.9994 15.637 20.2298 16.9497 18.8594C18.2625 17.4889 19 15.6304 19 13.6923Z",
    "Vivienda": "path://M16.0001 13.3848C16.0001 14.6088 15.526 15.7828 14.6821 16.6483C14.203 17.1397 13.6269 17.5091 13 17.7364M19 13.6923C19 7.11538 12 2 12 2C12 2 5 7.11538 5 13.6923C5 15.6304 5.7375 17.4893 7.05025 18.8598C8.36301 20.2302 10.1436 20.9994 12.0001 20.9994C13.8566 20.9994 15.637 20.2298 16.9497 18.8594C18.2625 17.4889 19 15.6304 19 13.6923Z",
}
    labelSetting = {
        "normal": {
            "show": True,
            "position": "right",
            "offset": [10, 0],
            "textStyle": {"fontSize": 16},
        }
    }
    
    # pivot table by sector and year
    count_sector = df.pivot_table(
        index="sector", columns="year", values="municipio", aggfunc="count"
    )
    # replace nan with 0
    new = count_sector.fillna(0)
    
    data = [
    ['Agua', 1, 17, 81, 18, 39, 7],
    ['Edificios Públicos', 7, 6, 53, 467, 82, 0],
    ['Educación', 0, 0, 79, 132, 193, 0],
    ['Energía', 2, 0, 0, 7, 29, 0],
    ['Municipios', 1, 103, 2572, 1151, 789, 60],
    ['Recursos Naturales y Culturales', 2, 8, 79, 132, 248, 0],
    ['Salud y Servicios Sociales', 1, 61, 105, 348, 157, 42],
    ['Transportación', 0, 9, 150, 346, 153, 13],
    ['Vivienda', 0, 2, 24, 23, 3, 0]
]

    years = range(2018, 2024)

    data_by_year = {i+2018: {data[j][0]: data[j][i+1] for j in range(len(data))} for i in range(len(data[0])-1)}

    map_2018 = [
        {'value': val, 'symbol': pathSymbols[key]} for key, val in data_by_year[2018].items()
    ]
    
    map_2019 = [
        {'value': val, 'symbol': pathSymbols[key]} for key, val in data_by_year[2019].items()
    ]
    
    map_2020 = [
        {'value': val, 'symbol': pathSymbols[key]} for key, val in data_by_year[2020].items()
    ]
    
    map_2021 = [
        {'value': val, 'symbol': pathSymbols[key]} for key, val in data_by_year[2021].items()
    ]
    
    map_2022 = [
        {'value': val, 'symbol': pathSymbols[key]} for key, val in data_by_year[2022].items()
    ]
    
    map_2023 = [
        {'value': val, 'symbol': pathSymbols[key]} for key, val in data_by_year[2023].items()
    ]
    
    map_data = map_2018 + map_2019 + map_2020 + map_2021 + map_2022 + map_2023
    
    #st.write(map_data)
    
    series = [
            {
                "name": key,
                "type": "pictorialBar",
                "label": labelSetting,
                "barGap": "20%",
                "symbolRepeat": True,
                "symbolSize": ["60%", "40%"],
                "barCategoryGap": "30%",
                "data": map_data[0: ],
            }
                for i, key in enumerate(years)
        ]
    
    for i in range(len(series)):
        series[i]['data'] = map_data[i*9: (i+1)*9]
        
    #st.write(series)
    
    option = {
        "title": {"text": "Proyectos por sector"},
        "legend": {"data": ["2018", "2019", "2020", "2021", "2022", "2023"]},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "grid": {"containLabel": True, "left": 20},
        "yAxis": {
            "data": ["Agua", "Edificions Publicos", "Educacion", "Energia", "Municipios", "Recursos Naturales", "Salud", "Transportacion", "Vivienda"],
            "inverse": True,
            "axisLine": {"show": False},
            "axisTick": {"show": False},
            "axisLabel": {"margin": 40, "fontSize": 12},
            "axisPointer": {"label": {"show": True, "margin": 30}},
        },
        "xAxis": {
            "splitLine": {"show": False},
            "axisLabel": {"show": False},
            "axisTick": {"show": False},
            "axisLine": {"show": False},
        },
        "series": series,
    }
    st_echarts(option, height="700px", key="echarts")
    
    st.write(new, use_column_width=True)
    print(new)
    
    #st.json(option)
    
def about():
    st.write("---")
    cols = st.columns(2)
    with cols[0]:
        st.image("https://www.elnuevodia.com/resizer/7XT2pZ6qrm6JeRrQhvd4Q3oeixo=/arc-anglerfish-arc2-prod-gfrmedia/public/DVWPMSDP6JDB3DMYLUAZEHCG4I.png", caption="Trabaja con ustedes")
    with cols[1]:
        st.markdown("## **Acerca**")
        st.markdown("""Este proyecto es una iniciativa de Todos por Puerto Rico, una organización sin fines de lucro que busca promover la transparencia y 
                    la rendición de cuentas en la administración pública. El objetivo de este proyecto es crear una herramienta que permita a los ciudadanos
                    de cada municipio de Puerto Rico tener acceso a la información de los proyectos de infraestructura que se están ejecutando en su municipio.""")
                    
        st.markdown("## **Proyecto de Investigación**")
        st.markdown("""Este proyecto es parte de un proyecto de investigación que se está llevando a cabo con la ayuda de Todos por Puerto Rico. El objetivo de este proyecto es
                    dar a conocer la información de los proyectos de infraestructura que se están ejecutando en Puerto Rico. Para esto, se ha creado una herramienta que permite
                    filtrar la información por municipio, sector y año.""")
        #st.markdown("## **Equipo**")
        #st.markdown("""
        #            Este proyecto ha sido desarrollado por dos emprededores de Puerto Rico y Ecuador, Daniel Ortiz (mandrake) y Javier Jaramillo (javierjaramillo). Aqui puedes encontrar
        #            los repositorios de los proyectos de Javier: [Github](https://github.com/jjaramillo34/) y [LinkedIn](https://www.linkedin.com/in/javier-jaramillo-7b5b3b1b3/). O nos puedes
        #            contactor por email: [Javier](mailto:jjaramillo34@gmail.com) y [Daniel](mailto:d@vinte.sh)""")
                    
        st.markdown("## **Agradecimientos**")
        st.markdown(""" Agradecemos a Todos por Puerto Rico por la oportunidad de llevar a cabo este proyecto. Darles las gracias a los miembros de la organización por su apoyo y orientación
                        en el desarrollo de este proyecto. Sin su ayuda este proyecto no hubiera sido posible. Mi agradecimiento a mi familia, esposa e hijos, por su apoyo y paciencia durante el
                        desarrollo de este proyecto.""")
                    
    st.write("---")
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
    elif selected2 == "About":
        about()





