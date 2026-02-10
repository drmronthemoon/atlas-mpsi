import streamlit as st
import pandas as pd
import json
import hashlib
import os
import time

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="MPSI Tracker",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FICHIERS ---
DATA_FILE = "mpsi_data.json"
USERS_FILE = "users.json"
SOUND_FILE = "startup.mp3" # Assurez-vous d'avoir ce fichier

# --- FONCTIONS UTILITAIRES ---
def hacher_mdp(mdp):
    return hashlib.sha256(mdp.encode()).hexdigest()

def load_json(file_path, default):
    if not os.path.exists(file_path): return default
    try:
        with open(file_path, "r", encoding="utf-8") as f: return json.load(f)
    except: return default

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- GESTION DE L'AUTHENTIFICATION ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""

def login_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 MPSI Tracker")
        st.markdown("### Authentification")
        
        with st.form("login_form"):
            user = st.text_input("Identifiant")
            pwd = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se Connecter / Créer Compte")
        
        if submit:
            if not user or not pwd:
                st.warning("Veuillez remplir tous les champs.")
                return
            
            hashed = hacher_mdp(pwd)
            users = load_json(USERS_FILE, {})
            
            # Création automatique si vide (Premier lancement) ou nouvel user
            if user not in users:
                users[user] = hashed
                save_json(USERS_FILE, users)
                st.success("Compte créé ! Connectez-vous maintenant.")
            
            # Vérification
            elif users[user] == hashed:
                st.session_state.authenticated = True
                st.session_state.username = user
                st.success("Connexion réussie !")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Mot de passe incorrect.")

# --- APPLICATION PRINCIPALE ---
def main_app():
    # ... (début de main_app inchangé) ...

    # --- CORRECTION ROBUSTE DU CHARGEMENT ---
    data = load_json(DATA_FILE, {"planning": [], "exercices": [], "kholles": []})

    # 1. Création des DataFrames
    df_plan = pd.DataFrame(data.get("planning", []), columns=["Date", "Matière", "Type", "Description", "Statut"])
    df_exos = pd.DataFrame(data.get("exercices", []), columns=["Matière", "Chapitre", "Réf", "État"])
    df_khol = pd.DataFrame(data.get("kholles", []), columns=["Date", "Matière", "Colleur"])

    # 2. Fonction de nettoyage des dates (Crucial !)
    def clean_date_column(df, col_name):
        if not df.empty and col_name in df.columns:
            # On force la conversion en datetime (dayfirst=True gère le format fr JJ/MM/AAAA)
            df[col_name] = pd.to_datetime(df[col_name], dayfirst=True, errors='coerce')
            # On convertit les Timestamp en objets date python simples (et on remplace les erreurs par None)
            df[col_name] = df[col_name].apply(lambda x: x.date() if pd.notnull(x) else None)
        return df

    # 3. Fonction de nettoyage des textes (Pour éviter les bugs si une case est vide/null)
    def clean_text_columns(df):
        # Remplace les 'NaN' (vides) par une chaine vide "" pour éviter les plantages
        return df.fillna("")

    # Application du nettoyage
    df_plan = clean_date_column(df_plan, "Date")
    df_plan = clean_text_columns(df_plan)

    df_khol = clean_date_column(df_khol, "Date")
    df_khol = clean_text_columns(df_khol)
    
    df_exos = clean_text_columns(df_exos)
    # ---------------------------------------------

    # Onglets (La suite reste identique...)
    tab1, tab2, tab3 = st.tabs(["📅 Planning", "📝 Exercices", "🎓 Kholles"])
    # Chargement des données
    data = load_json(DATA_FILE, {"planning": [], "exercices": [], "kholles": []})

    # Conversion en Pandas DataFrame
    df_plan = pd.DataFrame(data.get("planning", []), columns=["Date", "Matière", "Type", "Description", "Statut"])
    df_exos = pd.DataFrame(data.get("exercices", []), columns=["Matière", "Chapitre", "Réf", "État"])
    df_khol = pd.DataFrame(data.get("kholles", []), columns=["Date", "Matière", "Colleur"])

    # --- CORRECTION ICI : CONVERSION DES DATES ---
    # On force la colonne "Date" à être reconnue comme une vraie date, sinon Streamlit plante
    if not df_plan.empty:
        df_plan["Date"] = pd.to_datetime(df_plan["Date"], errors='coerce').dt.date
    
    if not df_khol.empty:
        df_khol["Date"] = pd.to_datetime(df_khol["Date"], errors='coerce').dt.date
    # ---------------------------------------------

    # Onglets
    tab1, tab2, tab3 = st.tabs(["📅 Planning", "📝 Exercices", "🎓 Kholles"])
    # Son de démarrage (Via lecteur HTML caché car les navigateurs bloquent l'autoplay)
    if os.path.exists(SOUND_FILE):
        st.audio(SOUND_FILE, autoplay=True)

    # Sidebar
    with st.sidebar:
        st.title(f"Bienvenue, {st.session_state.username} 👋")
        st.write("---")
        if st.button("Se Déconnecter"):
            st.session_state.authenticated = False
            st.rerun()
        st.markdown("---")
        st.caption("Made by Gemini for Al Yazid MZOUGUI")

    st.title("🚀 Tableau de Bord MPSI - Lycée Moulay Youssef")

    # Chargement des données
    data = load_json(DATA_FILE, {"planning": [], "exercices": [], "kholles": []})

    # Conversion en Pandas DataFrame pour l'édition facile
    df_plan = pd.DataFrame(data.get("planning", []), columns=["Date", "Matière", "Type", "Description", "Statut"])
    df_exos = pd.DataFrame(data.get("exercices", []), columns=["Matière", "Chapitre", "Réf", "État"])
    df_khol = pd.DataFrame(data.get("kholles", []), columns=["Date", "Matière", "Colleur"])

    # Onglets
    tab1, tab2, tab3 = st.tabs(["📅 Planning", "📝 Exercices", "🎓 Kholles"])

    # --- ONGLET 1 : PLANNING ---
    with tab1:
        st.subheader("Agenda")
        st.info("💡 Double-cliquez sur une cellule pour modifier. Cliquez sur le '+' en bas du tableau pour ajouter une ligne.")
        
        edited_plan = st.data_editor(
            df_plan,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Date": st.column_config.DateColumn(format="DD/MM/YYYY"),
                "Matière": st.column_config.SelectboxColumn(options=["Maths", "Physique", "Chimie", "SII", "Info", "Français", "Anglais"]),
                "Type": st.column_config.SelectboxColumn(options=["DS", "DM", "Colle", "Examen", "Autre"]),
                "Statut": st.column_config.SelectboxColumn(options=["À venir", "En cours", "Terminé", "Reporté"]),
            },
            key="editor_plan"
        )

    # --- ONGLET 2 : EXERCICES ---
    with tab2:
        st.subheader("Suivi des Exercices")
        edited_exos = st.data_editor(
            df_exos,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Matière": st.column_config.SelectboxColumn(options=["Maths", "Physique", "Chimie", "SII", "Info"]),
                "État": st.column_config.SelectboxColumn(options=["À faire", "En cours", "Terminé"]),
            },
            key="editor_exos"
        )

    # --- ONGLET 3 : KHOLLES ---
    with tab3:
        st.subheader("Suivi des Kholles")
        edited_khol = st.data_editor(
            df_khol,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Date": st.column_config.DateColumn(format="DD/MM/YYYY"),
                "Matière": st.column_config.SelectboxColumn(options=["Maths", "Physique", "Chimie", "SII", "Info", "Anglais", "Français"]),
            },
            key="editor_khol"
        )

    # --- SAUVEGARDE ---
    # Bouton de sauvegarde global
    if st.button("💾 Sauvegarder les modifications", type="primary"):
        # On convertit les Dataframes édités en liste pour le JSON
        new_data = {
            "planning": edited_plan.values.tolist(), # Convertit les valeurs y compris les dates
            "exercices": edited_exos.values.tolist(),
            "kholles": edited_khol.values.tolist()
        }
        
        # Astuce pour les dates : Pandas les gère comme des Timestamps, JSON n'aime pas ça.
        # Streamlit gère ça bien, mais pour être sûr, on sauvegarde tel quel.
        # Si bug de date : on force la conversion string.
        # Ici on fait simple :
        try:
            # On force la conversion des dates en string pour le JSON
            if not edited_plan.empty:
                edited_plan['Date'] = edited_plan['Date'].astype(str)
            if not edited_khol.empty:
                edited_khol['Date'] = edited_khol['Date'].astype(str)

            final_data = {
                "planning": edited_plan.values.tolist(),
                "exercices": edited_exos.values.tolist(),
                "kholles": edited_khol.values.tolist()
            }
            save_json(DATA_FILE, final_data)
            st.toast("Données sauvegardées avec succès !", icon="✅")
        except Exception as e:
            st.error(f"Erreur de sauvegarde : {e}")

# --- ROUTEUR ---
if st.session_state.authenticated:
    main_app()
else:
    login_screen()
