import streamlit as st
import requests

# FastAPI Backend URL
API_URL = "http://127.0.0.1:8000/notes"

# Page styling configuration
st.set_page_config(page_title="Notes API Frontend", page_icon="📝", layout="wide")
st.title("📝 Notes API - Interaktives Web-Frontend (Tag 7)")

# Split layout into 2 columns: left for listing notes, right for creating notes
col1, col2 = st.columns([1.2, 1.0])

with col1:
    st.header("📋 Gespeicherte Notizen")
    
    # Fetch data from the FastAPI Backend
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            notes = response.json()
            
            if not notes:
                st.info("Noch keine Notizen in der SQLite-Datenbank vorhanden.")
            else:
                for n in notes:
                    # Interactive component to expand and see note details
                    with st.expander(f"📌 {n['title']} (Kategorie: {n['category']})"):
                        st.write(f"**Inhalt:** {n['content']}")
                        st.write(f"**Priorität:** {'⭐' * n['priority']}")
                        
                        if n.get('author_email'):
                            st.write(f"📧 **Autor:** {n['author_email']}")
                            
                        if n.get('tags'):
                            st.write(f"🏷️ **Tags:** {', '.join(n['tags'])}")
                            
                        st.caption(f"Erstellt am: {n['created_at']}")
        else:
            st.error("Fehler beim Abrufen der Notizen vom Server.")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Keine Verbindung zum Backend! Läuft dein FastAPI-Server (`uv run fastapi dev`)?")

with col2:
    st.header("➕ Neue Notiz erstellen")
    
    # Form layout to bundle inputs and submit at once (Tag 7 Requirement)
    with st.form("create_note_form", clear_on_submit=True):
        title = st.text_input("Titel (mind. 3 Zeichen)")
        content = st.text_area("Inhalt (mind. 5 Zeichen)")
        category = st.text_input("Kategorie (z. B. study, work)")
        tags_raw = st.text_input("Tags (kommagetrennt, z. B. python, fastapi)")
        priority = st.slider("Priorität", min_value=1, max_value=5, value=3)
        author_email = st.text_input("Autor-E-Mail (Optional)")
        
        submit_button = st.form_submit_button("Notiz abspeichern")
        
        if submit_button:
            # Process comma-separated tags into a clean list
            tags_list = [t.strip() for t in tags_raw.split(",") if t.strip()]
            
            # Prepare payload for FastAPI
            payload = {
                "title": title,
                "content": content,
                "category": category,
                "tags": tags_list,
                "priority": priority,
                "author_email": author_email if author_email else None
            }
            
            # Send POST request to FastAPI to create the note
            try:
                post_response = requests.post(API_URL, json=payload)
                
                if post_response.status_code == 201:
                    st.success("🎉 Notiz erfolgreich angelegt!")
                    st.rerun()  # Instantly refresh UI to update the left column list
                elif post_response.status_code == 422:
                    st.error("❌ Validierungsfehler! Eingaben entsprechen nicht den Pydantic-Regeln.")
                    st.json(post_response.json()["detail"])
                else:
                    st.error(f"Unerwarteter Fehler: {post_response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Backend nicht erreichbar. Bitte starte das FastAPI-Backend.")