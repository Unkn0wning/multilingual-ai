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

if st.session_state.do_clear:
    st.session_state.main_input = ""
    st.session_state.cap = ""
    st.session_state.do_clear = False

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if isinstance(m["content"], dict):
            if "image" in m["content"]:
                st.image(m["content"]["image"], width=300)
            if "map" in m["content"]:
                st.map(pd.DataFrame([m["content"]["map"]]))
                st.write(f"📍 {m['content']['text']}")
        else:
            st.write(m["content"])

def make_url(p):
    return "https://image.pollinations.ai/prompt/" + quote(p) + "?width=512&height=512&nologo=true"

GPS_MAP_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  body { margin:0; padding:0; font-family: sans-serif; }
  #map { width:100%; height:420px; border-radius:12px; }
  #searchBox { display:flex; gap:5px; padding:8px; background:white; border-radius:8px; margin-bottom:8px; }
  #searchInput { flex:1; padding:10px; border:1px solid #ccc; border-radius:8px; font-size:14px; }
  #searchBtn { padding:10px 12px; background:#0b5fff; color:white; border:none; border-radius:8px; cursor:pointer; }
  #controls { display:flex; gap:6px; margin-top:8px; }
 .ctrlBtn { flex:1; padding:10px; border:none; border-radius:8px; cursor:pointer; font-weight:bold; font-size:13px; }
  #locateBtn { background:#25D366; color:white; }
  #satBtn { background:#222; color:white; }
  #streetBtn { background:#eee; color:#222; }
  #coords { font-size:12px; padding:6px; background:#f0f0f0; border-radius:6px; margin-top:6px; text-align:center; line-height:1.4; }
</style>
</head>
<body>
<div id="searchBox">
  <input id="searchInput" type="text" placeholder="🔍 Search: Peshawar, University..." />
  <button id="searchBtn">Search</button>
</div>
<div id="map"></div>
<div id="controls">
  <button id="locateBtn" class="ctrlBtn">📍 My GPS</button>
  <button id="satBtn" class="ctrlBtn">🛰️ Satellite</button>
  <button id="streetBtn" class="ctrlBtn">🗺️ Street</button>
</div>
<div id="coords">Click 📍 My GPS for blue dot!</div>

<script>
var map = L.map('map').setView([34.0151, 71.5249], 13);

// Street Layer (OpenStreetMap)
var street = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19, attribution: '© OSM'
});

// Satellite Layer (Esri World Imagery - Free satellite like Google)
var satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
  maxZoom: 19, attribution: '© Esri Satellite'
});

street.addTo(map); // default street
var currentLayer = street;

var userMarker = null;
var accuracyCircle = null;
var searchMarker = null;

function onLocationFound(e) {
  var lat = e.latlng.lat;
  var lng = e.latlng.lng;
  var acc = e.accuracy;

  if (userMarker) map.removeLayer(userMarker);
  if (accuracyCircle) map.removeLayer(accuracyCircle);

  accuracyCircle = L.circle(e.latlng, {radius: acc, color: '#0b5fff', fillColor: '#0b5fff', fillOpacity: 0.18}).addTo(map);

  var blueDotIcon = L.divIcon({
    className: '',
    html: '<div style="background:#0b5fff; width:18px; height:18px; border-radius:50%; border:3px solid white; box-shadow:0 0 12px #0b5fff, 0 0 0 10px rgba(11,95,255,0.2)"></div>',
    iconSize: [18,18],
    iconAnchor: [9,9]
  });

  userMarker = L.marker(e.latlng, {icon: blueDotIcon}).addTo(map).bindPopup("🔵 You are here!<br>Lat: " + lat.toFixed(6) + "<br>Lon: " + lng.toFixed(6) + "<br>Accuracy: " + Math.round(acc) + "m").openPopup();

  document.getElementById('coords').innerHTML = "✅ GPS BLUE DOT FOUND!<br>Lat: " + lat.toFixed(6) + " | Lon: " + lng.toFixed(6) + "<br>Accuracy: " + Math.round(acc) + "m - Copy to share below!";
}

function onLocationError(e) {
  document.getElementById('coords').innerHTML = "❌ GPS Error: " + e.message + "<br>Allow Location in browser settings!";
}

map.on('locationfound', onLocationFound);
map.on('locationerror', onLocationError);

document.getElementById('locateBtn').onclick = function() {
  document.getElementById('coords').innerHTML = "🔄 Getting GPS... Allow permission popup!";
  map.locate({setView: true, maxZoom: 17, enableHighAccuracy: true});
};

document.getElementById('satBtn').onclick = function() {
  if (currentLayer!== satellite) {
    map.removeLayer(currentLayer);
    satellite.addTo(map);
    currentLayer = satellite;
    document.getElementById('coords').innerHTML = "🛰️ Satellite View ON - Like Google Earth!";
  }
};

document.getElementById('streetBtn').onclick = function() {
  if (currentLayer!== street) {
    map.removeLayer(currentLayer);
    street.addTo(map);
    currentLayer = street;
    document.getElementById('coords').innerHTML = "🗺️ Street View ON!";
  }
};

async function searchPlace() {
  var query = document.getElementById('searchInput').value;
  if (!query) return;
  document.getElementById('coords').innerHTML = "🔍 Searching: " + query + "...";
  try {
    var res = await fetch("https://nominatim.openstreetmap.org/search?format=json&q=" + encodeURIComponent(query));
    var data = await res.json();
    if (data && data.length > 0) {
      var lat = parseFloat(data[0].lat);
      var lon = parseFloat(data[0].lon);
      map.setView([lat, lon], 16);
      if (searchMarker) map.removeLayer(searchMarker);
      searchMarker = L.marker([lat, lon]).addTo(map).bindPopup("🔍 " + data[0].display_name).openPopup();
      document.getElementById('coords').innerHTML = "✅ " + data[0].display_name + "<br>Lat: " + lat.toFixed(6) + " | Lon: " + lon.toFixed(6);
    } else {
      document.getElementById('coords').innerHTML = "❌ Not found: " + query;
    }
  } catch(err) {
    document.getElementById('coords').innerHTML = "❌ Search needs internet";
  }
}

document.getElementById('searchBtn').onclick = searchPlace;
document.getElementById('searchInput').addEventListener('keypress', function(e){ if(e.key==='Enter') searchPlace(); });

map.on('click', function(e){
  var lat = e.latlng.lat;
  var lng = e.latlng.lng;
  if (searchMarker) map.removeLayer(searchMarker);
  searchMarker = L.marker([lat, lng]).addTo(map).bindPopup("📍 Clicked<br>Lat: " + lat.toFixed(6) + "<br>Lon: " + lng.toFixed(6)).openPopup();
  document.getElementById('coords').innerHTML = "📍 Clicked<br>Lat: " + lat.toFixed(6) + " | Lon: " + lng.toFixed(6) + "<br>Copy to share!";
});
</script>
</body>
</html>
"""

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
            cap = st.text_input("What to do?", placeholder="make more robotic", key="cap")
            if cap:
                st.session_state.pending_caption = cap

        st.divider()
        st.write("**📍 GPS Map - Satellite + Search**")
        components.html(GPS_MAP_HTML, height=580)

        lat2 = st.number_input("Your Lat (from blue dot)", value=34.0151, format="%.6f", key="lat2")
        lon2 = st.number_input("Your Lon (from blue dot)", value=71.5249, format="%.6f", key="lon2")
        if st.button("Share Location 📤", use_container_width=True, key="share_loc"):
            st.session_state.user_location = {"lat": lat2, "lon": lon2}
            st.success("Ready! Click Send ➤ to share!")

with c2:
    chat_text = st.text_input("chat", placeholder="Ask JARVIS anything...", label_visibility="collapsed", key="main_input")

with c3:
    with st.popover("🎤", use_container_width=True):
        aud = st.audio_input("Voice", label_visibility="collapsed", key="mic")
        if aud:
            t = client.audio.transcriptions.create(file=("v.wav", aud.getvalue()), model="whisper-large-v3", response_format="text")
            st.session_state["voice"] = t

send = st.button("Send ➤")

final_prompt = None
location_to_send = None

if send and st.session_state.get("main_input"):
    final_prompt = st.session_state["main_input"]
if "voice" in st.session_state:
    final_prompt = st.session_state.pop("voice")
if st.session_state.user_location:
    if not final_prompt:
        final_prompt = f"My GPS location: {st.session_state.user_location['lat']}, {st.session_state.user_location['lon']}"
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
        want_image = True if st.session_state.pending_image else any(w in low for w in ["robotic","image","picture","banao","iron man"])
        if location_to_send:
            resp = f"📍 Got your blue dot GPS! Lat {location_to_send['lat']}, Lon {location_to_send['lon']} - Shared!"
            st.write(resp)
            st.session_state.messages.append({"role": "assistant", "content": resp})
            st.session_state.user_location = None
        elif want_image and st.session_state.pending_image:
            with st.spinner("Creating..."):
                try:
                    v = client.chat.completions.create(model="meta-llama/llama-4-scout-17b-16e-instruct", messages=[{"role": "user", "content": [{"type": "text", "text": "Describe"}, {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + st.session_state.pending_image}}]}])
                    full_p = v.choices[0].message.content + ", " + final_prompt
                except:
                    full_p = final_prompt
                url = make_url(full_p)
                st.image(url)
                st.link_button("Download", url)
                st.session_state.messages.append({"role": "assistant", "content": {"image": url, "text": full_p}})
                st.session_state.pending_image = None
        elif want_image:
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
                    box.write(full + "_")
            box.write(full)
            st.session_state.messages.append({"role": "assistant", "content": full})

    st.session_state.do_clear = True
    st.rerun()
