import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin.exceptions import FirebaseError
import json

class FirebaseConfig:
    @staticmethod
    def initialize_firebase():
        """Initialize Firebase with credentials from Streamlit secrets"""
        try:
            # Check if Firebase is already initialized
            try:
                firebase_admin.get_app()
                st.session_state.db = firestore.client()
                return True
            except ValueError:
                # Firebase not yet initialized
                pass

            # Get credentials from Streamlit secrets
            firebase_creds = dict(st.secrets["firebase"])
            
            # Create a temporary credential object
            cred = credentials.Certificate(firebase_creds)
            
            # Initialize Firebase
            firebase_admin.initialize_app(cred)
            
            # Store db reference in session state
            st.session_state.db = firestore.client()
            
            return True

        except Exception as e:
            st.error(f"❌ Errore nell'inizializzazione di Firebase: {str(e)}")
            return False