# utils/firebase_config.py
import streamlit as st
from firebase_admin import credentials, initialize_app, get_app, firestore
import firebase_admin

class FirebaseConfig:
    @staticmethod
    def initialize_firebase():
        """Inizializza Firebase con gestione degli errori e stato"""
        if 'firebase_initialized' not in st.session_state:
            try:
                # Verifica se Firebase è già inizializzato
                try:
                    app = get_app()
                    st.session_state.db = firestore.client()
                    st.session_state.firebase_initialized = True
                    return True
                except ValueError:
                    pass

                # Usa direttamente i secrets di Streamlit
                cred = credentials.Certificate(dict(st.secrets["firebase"]))
                initialize_app(cred)
                st.session_state.db = firestore.client()
                st.session_state.firebase_initialized = True
                return True

            except Exception as e:
                st.error(f"❌ Errore nell'inizializzazione di Firebase: {str(e)}")
                return False

        return st.session_state.firebase_initialized