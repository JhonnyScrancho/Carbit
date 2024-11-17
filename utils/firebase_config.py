# utils/firebase_config.py
import streamlit as st
from firebase_admin import credentials, initialize_app, get_app, firestore
import firebase_admin
import json

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
                    # Firebase non ancora inizializzato
                    pass

                # Crea il dict delle credenziali
                cred_dict = {
                    "type": st.secrets.firebase.type,
                    "project_id": st.secrets.firebase.project_id,
                    "private_key_id": st.secrets.firebase.private_key_id,
                    "private_key": st.secrets.firebase.private_key,
                    "client_email": st.secrets.firebase.client_email,
                    "client_id": st.secrets.firebase.client_id,
                    "auth_uri": st.secrets.firebase.auth_uri,
                    "token_uri": st.secrets.firebase.token_uri,
                    "auth_provider_x509_cert_url": st.secrets.firebase.auth_provider_x509_cert_url,
                    "client_x509_cert_url": st.secrets.firebase.client_x509_cert_url,
                    "universe_domain": st.secrets.firebase.universe_domain
                }

                # Inizializza con le credenziali
                cred = credentials.Certificate(cred_dict)
                initialize_app(cred)
                st.session_state.db = firestore.client()
                st.session_state.firebase_initialized = True
                return True

            except Exception as e:
                st.error(f"❌ Errore nell'inizializzazione di Firebase: {str(e)}")
                st.exception(e)  # Questo mostrerà l'errore completo per debug
                return False

        return st.session_state.firebase_initialized