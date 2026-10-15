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
if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None

if st.session_state.do_clear:
    st.session_state.main_input = ""
    st.session_state.cap = ""
    st.session_state.do_clear = False

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if isinstance(m["content"], dict):
            if "image" in m["content"]:
                st.image(m["content"]["image"], width=350)
            if "map" in m["content"]:
                st.map(pd.DataFrame([m["content"]["map"]]))
        else:
            st.write(m["content"])

def make_url(p):
    return "https://image.pollinations.ai/prompt/" + quote(p[:400]) + "?width=768&height=768&nologo=true"

GPS_MAP_HTML = """<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/><script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>body{margin:0}#map{width:100%;height:400px;border-radius:12px}#searchBox{display:flex;gap:5px;padding:8px;background:white;border-radius:8px;margin-bottom:8px}#searchInput{flex:1;padding:8px;border:1px solid #ccc;border-radius:8px}#searchBtn{padding:8px;background:#0b5fff;color:white;border:none;border-radius:8px}#controls{display:flex;gap:5px;margin-top:6px}.ctrlBtn{flex:1;padding:8px;border:none;border-radius:8px;font-weight:bold}#locateBtn{background:#25D366;color:white}#satBtn{background:#222;color:white}#streetBtn{background:#eee}</style></head><body>
<div id="searchBox"><input id="searchInput" placeholder="Search..."/><button id="searchBtn">Search</button></div><div id="map"></div>
<div id="controls"><button id="locateBtn" class="ctrlBtn">📍 GPS</button><button id="satBtn" class="ctrlBtn">🛰️ Sat</button><button id="streetBtn" class="ctrlBtn">🗺️ Street</button></div>
<div id="coords" style="font-size:12px;padding:6px;background:#f0f0f0;border-radius:6px;margin-top:6px;text-align:center">GPS ready!</div>
<script>
var map=L.map('map').setView([34.0151,71.5249],13);var street=L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19}).addTo(map);var sat=L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',{maxZoom:19});var cur=street;var userMarker=null,circle=null;
function onFound(e){if(userMarker)map.removeLayer(userMarker);if(circle)map.removeLayer(circle);circle=L.circle(e.latlng,{radius:e.accuracy,color:'#0b5fff',fillOpacity:0.15}).addTo(map);var icon=L.divIcon({html:'<div style="background:#0b5fff;width:18px;height:18px;border-radius:50%;border:3px solid white"></div>',iconSize:[18,18],iconAnchor:[9,9]});userMarker=L.marker(e.latlng,{icon:icon}).addTo(map).bindPopup("You here").openPopup();document.getElementById('coords').innerHTML="Lat:"+e.latlng.lat.toFixed(6)+" Lon:"+e.latlng.lng.toFixed(6);}
map.on('locationfound',onFound);document.getElementById('locateBtn').onclick=()=>map.locate({setView:true,maxZoom:17,enableHighAccuracy:true});
document.getElementById('satBtn').onclick=()=>{map.removeLayer(cur);sat.addTo(map);cur=sat;};document.getElementById('streetBtn').onclick=()=>{map.removeLayer(cur);street.addTo(map);cur=street;};
async function s(){var q=document.getElementById('searchInput').value;var r=await fetch("https://nominatim.openstreetmap.org/search?format=json&q="+encodeURIComponent(q));var d=await r.json();if(d.length>0)map.setView([parseFloat(d[0].lat),parseFloat(d[0].lon)],15);}document.getElementById('searchBtn').onclick=s;
</script></body></html>"""

st.divider()
c1, c2, c3 = st.columns([1, 7, 1])

with c1:
    with st.popover("＋", use_container_width=True):
        st.write("**📸 Photo**")
        up = st.file_uploader("Upload", type=["png","jpg","jpeg"], label_visibility="collapsed", key="plus")
        if up:
            st.image(up, width=150)
            st.session_state.pending_image = base64.b64encode(up.getvalue()).decode()
            st.success("Attached!")
        if st.session_state.pending_image:
            cap = st.text_input("What to do?", placeholder="make more robotic, keep faces same", key="cap")
            ca, cb = st.columns(2)
            with ca:
                if st.button("❌ Remove", use_container_width=True):
                    st.session_state.pending_image = None
                    st.rerun()
            with cb:
                if st.button("✨ CREATE", type="primary", use_container_width=True):
                    st.session_state.trigger_exact = True
                    st.rerun()
        st.divider()
        st.write("**📍 GPS Map**")
        components.html(GPS_MAP_HTML, height=520)
        lat2 = st.number_input("Lat", value=34.0151, format="%.6f", key="lat2")
        lon2 = st.number_input("Lon", value=71.5249, format="%.6f", key="lon2")
        if st.button("Share Location 📤", use_container_width=True):
            st.session_state.user_location = {"lat": lat2, "lon": lon2}
            st.success("Ready! Click Send!")

with c2:
    st.text_input("chat", placeholder="Ask JARVIS...", label_visibility="collapsed", key="main_input")

with c3:
    # FIXED VOICE - Direct, not in popover!
    st.write("🎤")
    aud = st.audio_input("Voice", label_visibility="collapsed", key="mic_main")

# --- FIXED LOGIC ---
final_prompt = None
location_to_send = None

# 1. VOICE AUTO-TRIGGER - FIXED!
if aud and st.session_state.get("last_audio_id")!= getattr(aud, 'file_id', str(len(aud.getvalue()))):
    with st.spinner("🎤 Transcribing..."):
        try:
            transcription = client.audio.transcriptions.create(
                file=("voice.wav", aud.getvalue()),
                model="whisper-large-v3",
                response_format="text"
            )
            st.session_state.last_audio_id = getattr(aud, 'file_id', str(len(aud.getvalue())))
            final_prompt = transcription
            st.toast(f"🎤 Heard: {transcription}")
        except Exception as e:
            st.error(f"Voice error: {e}")

# Check for manual trigger from photo or previous voice
if st.session_state.get("trigger_exact"):
    final_prompt = st.session_state.get("cap", "make more robotic, keep faces identical")
    st.session_state.trigger_exact = False

if st.session_state.get("voice_text") and st.session_state.get("trigger_voice"):
    final_prompt = st.session_state.pop("voice_text")
    st.session_state.trigger_voice = False

send = st.button("Send ➤", use_container_width=True)

if send and st.session_state.get("main_input"):
    final_prompt = st.session_state["main_input"]
if st.session_state.user_location and (send or final_prompt):
    location_to_send = st.session_state.user_location

if final_prompt:
    if location_to_send:
        st.session_state.messages.append({"role": "user", "content": {"map": location_to_send, "text": final_prompt}})
    else:
        st.session_state.messages.append({"role": "user", "content": final_prompt})

    with st.chat_message("user"):
        if st.session_state.pending_image:
            st.image(base64.b64decode(st.session_state.pending_image), width=150)
        if location_to_send:
            st.map(pd.DataFrame([location_to_send]))
        st.write(final_prompt)

    with st.chat_message("assistant"):
        low = final_prompt.lower()
        if location_to_send:
            resp = f"📍 Got GPS {location_to_send['lat']}, {location_to_send['lon']}"
            st.write(resp)
            st.session_state.messages.append({"role": "assistant", "content": resp})
            st.session_state.user_location = None
        elif st.session_state.pending_image:
            with st.spinner("Creating exact..."):
                try:
                    v = client.chat.completions.create(model="meta-llama/llama-4-scout-17b-16e-instruct", messages=[{"role": "user", "content": [{"type": "text", "text": f"Describe to keep exact faces and background, add: {final_prompt}"}, {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + st.session_state.pending_image}}]}])
                    full_p = v.choices[0].message.content + f", {final_prompt}, keep faces identical, keep background identical, photorealistic, 8k"
                except:
                    full_p = f"{final_prompt}, keep faces identical, keep background identical river mountains, only robotic armor, photorealistic, 8k"
                url = make_url(full_p)
                st.image(url)
                st.link_button("Download", url)
                st.session_state.messages.append({"role": "assistant", "content": {"image": url, "text": full_p}})
                st.session_state.pending_image = None
        elif any(w in low for w in ["image","picture","banao","robotic"]):
            url = make_url(final_prompt)
            st.image(url)
            st.session_state.messages.append({"role": "assistant", "content": {"image": url, "text": final_prompt}})
        else:
            full = ""
            box = st.empty()
            msgs = [{"role": "system", "content": "You are JARVIS by Hashir."}] + [m for m in st.session_state.messages if isinstance(m["content"], str)]
            s = client.chat.completions.create(model="openai/gpt-oss-20b", messages=msgs, stream=True)
            for ch in s:
                if ch.choices[0].delta.content:
                    full += ch.choices[0].delta.content
                    box.write(full + "▌")
            box.write(full)
            st.session_state.messages.append({"role": "assistant", "content": full})

    st.session_state.do_clear = True
    st.rerun()
