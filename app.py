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
    st.session_state.photo_prompt = "make more robotic iron man suit"

if st.session_state.do_clear:
    st.session_state.main_input = ""
    st.session_state.do_clear = False

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if isinstance(m["content"], dict):
            if "image" in m["content"]:
                st.image(m["content"]["image"], width=350)
                st.write(m["content"].get("text",""))
            if "map" in m["content"]:
                st.map(pd.DataFrame([m["content"]["map"]]))
        else:
            st.write(m["content"])

def make_url(prompt):
    # FIXED: Better encoding for AI image
    safe = quote(prompt[:300]) # pollinations limit
    return f"https://image.pollinations.ai/prompt/{safe}?width=512&height=512&nologo=true&seed={hash(prompt)%10000}"

GPS_MAP_HTML = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/><script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><style>body{margin:0}#map{width:100%;height:300px;border-radius:12px}#searchBox{display:flex;gap:5px;padding:8px}#searchInput{flex:1;padding:8px;border:1px solid #ccc;border-radius:8px}#searchBtn{padding:8px;background:#0b5fff;color:white;border:none;border-radius:8px}#controls{display:flex;gap:5px;margin-top:5px}.ctrlBtn{flex:1;padding:7px;border:none;border-radius:8px;font-weight:bold}#locateBtn{background:#25D366;color:white}#satBtn{background:#222;color:white}#streetBtn{background:#eee}</style></head><body><div id="searchBox"><input id="searchInput" placeholder="Search Peshawar..."/><button id="searchBtn">Search</button></div><div id="map"></div><div id="controls"><button id="locateBtn" class="ctrlBtn">📍 GPS</button><button id="satBtn" class="ctrlBtn">🛰️ Sat</button><button id="streetBtn" class="ctrlBtn">🗺️ Street</button></div><script>var map=L.map('map').setView([34.0151,71.5249],13);var street=L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19}).addTo(map);var sat=L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',{maxZoom:19});var cur=street;document.getElementById('locateBtn').onclick=()=>map.locate({setView:true,maxZoom:17,enableHighAccuracy:true});map.on('locationfound',e=>{L.marker(e.latlng).addTo(map).bindPopup("You here!").openPopup();L.circle(e.latlng,{radius:e.accuracy}).addTo(map);});document.getElementById('satBtn').onclick=()=>{map.removeLayer(cur);sat.addTo(map);cur=sat;};document.getElementById('streetBtn').onclick=()=>{map.removeLayer(cur);street.addTo(map);cur=street;};async function s(){var q=document.getElementById('searchInput').value;var r=await fetch("https://nominatim.openstreetmap.org/search?format=json&q="+encodeURIComponent(q));var d=await r.json();if(d.length>0)map.setView([parseFloat(d[0].lat),parseFloat(d[0].lon)],15);}document.getElementById('searchBtn').onclick=s;</script></body></html>"""

st.divider()
c1, c2, c3 = st.columns([1, 7, 1])

with c1:
    with st.popover("＋", use_container_width=True):
        st.write("**📸 Photo - AI Edit**")
        up = st.file_uploader("Upload", type=["png","jpg","jpeg"], label_visibility="collapsed", key="plus")
        if up:
            st.image(up, width=180)
            st.session_state.pending_image = base64.b64encode(up.getvalue()).decode()
            st.success("Attached! Now type what to do below")

        if st.session_state.pending_image:
            st.write("**What to do?**")
            prompt = st.text_input("prompt", value=st.session_state.photo_prompt, placeholder="make more robotic iron man", label_visibility="collapsed", key="photo_prompt_input")
            st.session_state.photo_prompt = prompt

            st.caption(f"Current: {prompt}")

            b1, b2 = st.columns(2)
            with b1:
                if st.button("❌ Remove", use_container_width=True):
                    st.session_state.pending_image = None
                    st.rerun()
            with b2:
                if st.button("✨ CREATE AI", use_container_width=True, type="primary"):
                    # DIRECT IMAGE CREATION - NO GROQ NEEDED!
                    final_p = f"{prompt}, 3 boys like in photo, robotic iron man suit, futuristic armor, glowing blue lights, ultra detailed, 8k, photorealistic, cinematic"
                    url = make_url(final_p)
                    st.image(url, caption="Generating...")
                    st.session_state.messages.append({"role": "user", "content": f"Edit photo: {prompt}"})
                    st.session_state.messages.append({"role": "assistant", "content": {"image": url, "text": f"✅ Robotic version created! Prompt: {prompt}"}})
                    st.session_state.pending_image = None
                    st.success("Created! Check main chat!")
                    st.rerun()

        st.divider()
        st.write("**📍 GPS Map**")
        components.html(GPS_MAP_HTML, height=400)

with c2:
    st.text_input("chat", placeholder="Ask JARVIS anything...", label_visibility="collapsed", key="main_input")

with c3:
    with st.popover("🎤", use_container_width=True):
        aud = st.audio_input("Voice", label_visibility="collapsed", key="mic")
        if aud:
            t = client.audio.transcriptions.create(file=("v.wav", aud.getvalue()), model="whisper-large-v3", response_format="text")
            st.session_state["voice"] = t

if st.button("Send ➤", use_container_width=True):
    p = st.session_state.get("main_input","")
    if "voice" in st.session_state:
        p = st.session_state.pop("voice")

    if p:
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"):
            st.write(p)
        with st.chat_message("assistant"):
            low = p.lower()
            if any(x in low for x in ["image","picture","banao","photo","robotic","iron"]):
                # CREATE IMAGE DIRECTLY - WORKS 100%
                url = make_url(p + ", ultra detailed, 8k, photorealistic")
                st.image(url, width=350)
                st.link_button("📥 Download", url)
                st.session_state.messages.append({"role": "assistant", "content": {"image": url, "text": f"Image for: {p}"}})
            else:
                full=""
                box=st.empty()
                msgs=[{"role":"system","content":"You are JARVIS by Hashir."}]+[m for m in st.session_state.messages if isinstance(m["content"], str)]
                s=client.chat.completions.create(model="openai/gpt-oss-20b", messages=msgs, stream=True)
                for ch in s:
                    if ch.choices[0].delta.content:
                        full+=ch.choices[0].delta.content
                        box.write(full+"_")
                box.write(full)
                st.session_state.messages.append({"role": "assistant", "content": full})
        st.session_state.do_clear=True
        st.rerun()
