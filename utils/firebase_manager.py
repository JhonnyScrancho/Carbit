# utils/firebase_manager.py
from firebase_admin import firestore
from datetime import datetime
from typing import Dict, List, Optional

class FirebaseManager:
    """Gestore delle operazioni su Firebase"""
    
    def __init__(self, db: firestore.Client):
        self.db = db
        
    def save_vehicle(self, vehicle_data: Dict) -> bool:
        """
        Salva o aggiorna i dati di un veicolo
        Args:
            vehicle_data (Dict): Dati del veicolo da salvare
        Returns:
            bool: True se l'operazione ha successo, False altrimenti
        """
        try:
            # Usa la targa come ID documento
            doc_ref = self.db.collection('vehicles').document(vehicle_data['plate'])
            
            # Prepara i dati del prezzo per lo storico
            price_history = {
                'price': vehicle_data.get('base_price'),
                'date': datetime.now(),
                'fonte': vehicle_data.get('fonte', 'unknown')
            }
            
            # Aggiorna il veicolo principale
            vehicle_data.update({
                'last_updated': datetime.now(),
                'created_at': vehicle_data.get('created_at', datetime.now())
            })
            
            doc_ref.set(vehicle_data, merge=True)
            
            # Aggiungi il prezzo allo storico
            history_ref = doc_ref.collection('price_history').document()
            history_ref.set(price_history)
            
            return True
        except Exception as e:
            print(f"Errore nel salvataggio del veicolo: {str(e)}")
            return False
    
    def save_auction_batch(self, vehicles: List[Dict]) -> Dict:
        """
        Salva un batch di veicoli da un'asta
        Args:
            vehicles (List[Dict]): Lista di veicoli da salvare
        Returns:
            Dict: Risultati dell'operazione con conteggio successi/fallimenti
        """
        try:
            batch = self.db.batch()
            results = {'success': 0, 'failed': 0}
            
            for vehicle in vehicles:
                try:
                    # Documento principale del veicolo
                    doc_ref = self.db.collection('vehicles').document(vehicle['plate'])
                    
                    # Aggiungi timestamp
                    vehicle.update({
                        'last_updated': datetime.now(),
                        'created_at': vehicle.get('created_at', datetime.now())
                    })
                    
                    batch.set(doc_ref, vehicle, merge=True)
                    
                    # Documento storico prezzi
                    history_ref = doc_ref.collection('price_history').document()
                    batch.set(history_ref, {
                        'price': vehicle.get('base_price'),
                        'date': datetime.now(),
                        'fonte': vehicle.get('fonte', 'unknown')
                    })
                    
                    results['success'] += 1
                except Exception as e:
                    print(f"Errore nel processing del veicolo {vehicle.get('plate')}: {str(e)}")
                    results['failed'] += 1
            
            batch.commit()
            return results
        except Exception as e:
            print(f"Errore nel salvataggio batch: {str(e)}")
            return {'success': 0, 'failed': len(vehicles)}
    
    def get_vehicle_history(self, plate: str) -> Optional[Dict]:
        """
        Recupera lo storico di un veicolo con storico prezzi
        Args:
            plate (str): Targa del veicolo
        Returns:
            Optional[Dict]: Dati del veicolo con storico prezzi o None se non trovato
        """
        try:
            # Recupera dati principali
            doc_ref = self.db.collection('vehicles').document(plate)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
                
            vehicle_data = doc.to_dict()
            
            # Recupera storico prezzi
            prices = []
            prices_ref = doc_ref.collection('price_history').order_by('date', direction=firestore.Query.DESCENDING)
            
            for price_doc in prices_ref.stream():
                price_data = price_doc.to_dict()
                prices.append(price_data)
            
            vehicle_data['price_history'] = prices
            return vehicle_data
            
        except Exception as e:
            print(f"Errore nel recupero storico: {str(e)}")
            return None

    def add_to_watchlist(self, user_id: str, vehicle_plate: str) -> bool:
        """
        Aggiunge un veicolo alla watchlist dell'utente
        Args:
            user_id (str): ID dell'utente
            vehicle_plate (str): Targa del veicolo da monitorare
        Returns:
            bool: True se l'operazione ha successo, False altrimenti
        """
        try:
            watchlist_ref = self.db.collection('watchlist').document(user_id)
            watchlist_ref.set({
                'vehicles': firestore.ArrayUnion([vehicle_plate]),
                'last_updated': datetime.now()
            }, merge=True)
            return True
        except Exception as e:
            print(f"Errore nell'aggiunta alla watchlist: {str(e)}")
            return False

    def get_watchlist(self, user_id: str) -> List[Dict]:
        """
        Recupera tutti i veicoli nella watchlist dell'utente
        Args:
            user_id (str): ID dell'utente
        Returns:
            List[Dict]: Lista di veicoli monitorati
        """
        try:
            # Recupera la watchlist dell'utente
            watchlist_doc = self.db.collection('watchlist').document(user_id).get()
            if not watchlist_doc.exists:
                return []
                
            # Recupera i dettagli di ogni veicolo
            vehicles = []
            for plate in watchlist_doc.to_dict().get('vehicles', []):
                vehicle_data = self.get_vehicle_history(plate)
                if vehicle_data:
                    vehicles.append(vehicle_data)
                    
            return vehicles
        except Exception as e:
            print(f"Errore nel recupero watchlist: {str(e)}")
            return []