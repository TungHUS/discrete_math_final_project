import streamlit as st
from pyvis.network import Network
import json
import streamlit.components.v1 as components

def get_data(filename):
    with open(f'data/{filename}.json', "r") as file:
        data = json.load(file)
        return data

coor = get_data('coor')
link = get_data('network')

pos = {key: [int(round(coor[key][0]-51.5,5)*10**5),int(round(coor[key][1],5)*10**5)] for key in coor.keys()}

st.title("A* search algorithms")
st.write(coor)

