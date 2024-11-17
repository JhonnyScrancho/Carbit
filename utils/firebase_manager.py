from firebase_admin import firestore
from datetime import datetime
from typing import Dict, List, Optional

class FirebaseManager:
    """Gestore delle operazioni su Firebase"""
    
    def __init__(self):
        """Initialize Firebase Manager"""
        try:
            self.db = firestore.client()
        except Exception as e:
            print(f"Errore nell'inizializzazione del FirebaseManager: {str(e)}")
            self.db = None

    @classmethod
    def get_instance(cls):
        """
        Singleton pattern per ottenere un'istanza del FirebaseManager
        Returns:
            FirebaseManager: Istanza unica del manager
        """
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance
    
    def save_vehicle(self, vehicle_data: Dict) -> bool:
        """
        Salva o aggiorna i dati di un veicolo
        Args:
            vehicle_data (Dict): Dati del veicolo da salvare
        Returns:
            bool: True se l'operazione ha successo, False altrimenti
        """
        if not self.db:
            return False
            
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
        if not self.db:
            return {'success': 0, 'failed': len(vehicles)}
            
        try:
            batch = self.db.batch()
            results = {'success': 0, 'failed': 0}
            
            for vehicle in vehicles:
                try:
                    # Documento principale del veicolo
                    doc_ref = self.db.collection('vehicles').document(vehicle.get('plate', ''))
                    
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
        if not self.db:
            return None
            
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
        if not self.db:
            return False
            
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

    def remove_from_watchlist(self, user_id: str, vehicle_plate: str) -> bool:
        """
        Rimuove un veicolo dalla watchlist dell'utente
        Args:
            user_id (str): ID dell'utente
            vehicle_plate (str): Targa del veicolo da rimuovere
        Returns:
            bool: True se l'operazione ha successo, False altrimenti
        """
        if not self.db:
            return False
            
        try:
            watchlist_ref = self.db.collection('watchlist').document(user_id)
            watchlist_ref.update({
                'vehicles': firestore.ArrayRemove([vehicle_plate]),
                'last_updated': datetime.now()
            })
            return True
        except Exception as e:
            print(f"Errore nella rimozione dalla watchlist: {str(e)}")
            return False

    def get_watchlist(self, user_id: str) -> List[Dict]:
        """
        Recupera tutti i veicoli nella watchlist dell'utente
        Args:
            user_id (str): ID dell'utente
        Returns:
            List[Dict]: Lista di veicoli monitorati
        """
        if not self.db:
            return []
            
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

    def get_all_vehicles(self) -> List[Dict]:
        """
        Recupera tutti i veicoli dal database
        Returns:
            List[Dict]: Lista di tutti i veicoli
        """
        if not self.db:
            return []
            
        try:
            vehicles = []
            vehicles_ref = self.db.collection('vehicles').stream()
            
            for doc in vehicles_ref:
                vehicle_data = doc.to_dict()
                vehicle_data['id'] = doc.id
                vehicles.append(vehicle_data)
                
            return vehicles
        except Exception as e:
            print(f"Errore nel recupero di tutti i veicoli: {str(e)}")
            return []

    def get_active_auctions(self) -> List[Dict]:
        """
        Recupera tutte le aste attive
        Returns:
            List[Dict]: Lista delle aste attive
        """
        if not self.db:
            return []
            
        try:
            auctions = []
            now = datetime.now()
            
            auctions_ref = self.db.collection('auctions').where(
                'end_date', '>', now
            ).stream()
            
            for doc in auctions_ref:
                auction_data = doc.to_dict()
                auction_data['id'] = doc.id
                auctions.append(auction_data)
                
            return auctions
        except Exception as e:
            print(f"Errore nel recupero delle aste attive: {str(e)}")
            return []