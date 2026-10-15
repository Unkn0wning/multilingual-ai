import streamlit as st
from groq import Groq
import base64
from urllib.parse import quote
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="JARVIS AI", page_icon="🤖")
st.title("🤖 JARVIS AI")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "I am JARVIS by Hashir!"}]
if "pending_image" not in st.session_state:
    st.session_state.pending_image = None
if "do_clear" not in st.session_state:
    st.session_state.do_clear = False
if "user_location" not in st.session_state:
    st.session_state.user_location = None
if "photo_prompt" not in st.session_state:
    st.session_state.photo_prompt = "make more robotic"

if st.session_state.do_clear:
    st.session_state.main_input = ""
    st.session_state.do_clear = False

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if isinstance(m["content"], dict):
            if "image" in m["content"]:
                st.image(m["content"]["image"], width=300)
                st.write(m["content"].get("text",""))
            if "map" in m["content"]:
                st.map(pd.DataFrame([m["content"]["map"]]))
        else:
            st.write(m["content"])

def make_url(p):
    return "https://image.pollinations.ai/prompt/" + quote(p) + "?width=512&height=512&nologo=true"

GPS_MAP_HTML = """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/><script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>body{margin:0}#map{width:100%;height:350px;border-radius:12px}#searchBox{display:flex;gap:5px;padding:8px}#searchInput{flex:1;padding:10px;border:1px solid #ccc;border-radius:8px}#searchBtn{padding:10px;background:#0b5fff;color:white;border:none;border-radius:8px}#controls{display:flex;gap:5px;margin-top:6px}.ctrlBtn{flex:1;padding:8px;border:none;border-radius:8px;font-weight:bold}#locateBtn{background:#25D366;color:white}#satBtn{background:#222;color:white}#streetBtn{background:#eee}#coords{font-size:12px;padding:5px;background:#f0f0f0;border-radius:6px;margin-top:5px;text-align:center}</style></head><body>
<div id="searchBox"><input id="searchInput" placeholder="Search: Peshawar..."/><button id="searchBtn">Search</button></div><div id="map"></div>
<div id="controls"><button id="locateBtn" class="ctrlBtn">📍 GPS</button><button id="satBtn" class="ctrlBtn">🛰️ Satellite</button><button id="streetBtn" class="ctrlBtn">🗺️ Street</button></div><div id="coords">Click GPS for blue dot!</div>
<script>
var map=L.map('map').setView([34.0151,71.5249],13);
var street=L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19}).addTo(map);
var satellite=L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',{maxZoom:19});
var current=street; var userMarker=null,circle=null,searchMarker=null;
function onFound(e){if(userMarker)map.removeLayer(userMarker);if(circle)map.removeLayer(circle);circle=L.circle(e.latlng,{radius:e.accuracy,color:'#0b5fff',fillOpacity:0.15}).addTo(map);var icon=L.divIcon({html:'<div style="background:#0b5fff;width:18px;height:18px;border-radius:50%;border:3px solid white;box-shadow:0 0 10px #0b5fff"></div>',iconSize:[18,18],iconAnchor:[9,9]});userMarker=L.marker(e.latlng,{icon:icon}).addTo(map).bindPopup("You: "+e.latlng.lat.toFixed(5)+","+e.latlng.lng.toFixed(5)).openPopup();document.getElementById('coords').innerHTML="Blue Dot: "+e.latlng.lat.toFixed(6)+","+e.latlng.lng.toFixed(6);}
map.on('locationfound',onFound); document.getElementById('locateBtn').onclick=()=>{map.locate({setView:true,maxZoom:17,enableHighAccuracy:true});};
document.getElementById('satBtn').onclick=()=>{map.removeLayer(current);satellite.addTo(map);current=satellite;};
document.getElementById('streetBtn').onclick=()=>{map.removeLayer(current);street.addTo(map);current=street;};
async function searchP(){var q=document.getElementById('searchInput').value;if(!q)return;var r=await fetch("https://nominatim.openstreetmap.org/search?format=json&q="+encodeURIComponent(q));var d=await r.json();if(d.length>0){var lat=parseFloat(d[0].lat),lon=parseFloat(d[0].lon);map.setView([lat,lon],16);if(searchMarker)map.removeLayer(searchMarker);searchMarker=L.marker([lat,lon]).addTo(map).bindPopup(d[0].display_name).openPopup();}}
document.getElementById('searchBtn').onclick=searchP; document.getElementById('searchInput').addEventListener('keypress',e=>{if(e.key==='Enter')searchP();});
</script></body></html>
"""

st.divider()
c1, c2, c3 = st.columns([1, 7, 1])

with c1:
    with st.popover("＋", use_container_width=True):
        st.write("**📸 Photo**")
        up = st.file_uploader("Upload photo", type=["png","jpg","jpeg"], label_visibility="collapsed", key="plus")
        if up:
            st.image(up, width=150)
            st.session_state.pending_image = base64.b64encode(up.getvalue()).decode()
            st.success("Attached!")

        # === FIXED PART
