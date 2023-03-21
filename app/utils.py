import pymongo
import streamlit as st
from datetime import datetime


client = pymongo.MongoClient(st.secrets['database_uri']['MONGO_URI'])
database = client['municipios_tdpr']

collection = database['municipios']

def insert_data(municipio, description, date):
    collection.insert_one({
        "municipio": municipio,
        "description": description,
        "date": date
    })
    
def get_data_by_municipio(municipio):
    data = collection.find({"municipio": municipio})
    return data[0]

def get_all():
    data = collection.find()
    return data
