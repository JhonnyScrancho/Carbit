import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin.exceptions import FirebaseError
import json

class FirebaseConfig:
    @staticmethod
    def initialize_firebase():
        try:
            # Verifica se Firebase è già inizializzato
            try:
                firebase_admin.get_app()
                return True
            except ValueError:
                # Firebase non ancora inizializzato
                pass

            # Ottieni le credenziali da Streamlit secrets
            firebase_secrets = dict(st.secrets["firebase"])
            
            # Assicurati che la private key sia nel formato corretto
            if "private_key" in firebase_secrets:
                firebase_secrets["private_key"] = firebase_secrets["private_key"].replace("\\n", "\n")

            # Inizializza Firebase
            cred = credentials.Certificate(firebase_secrets)
            firebase_admin.initialize_app(cred)
            
            return True

        except Exception as e:
            st.error(f"❌ Errore nell'inizializzazione di Firebase: {str(e)}")
            st.error("Dettagli credenziali:")
            st.json(firebase_secrets)  # Per debug - RIMUOVERE IN PRODUZIONE
            return False