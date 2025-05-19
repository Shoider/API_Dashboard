from datetime import datetime, timedelta
from flask import jsonify
from pymongo import ReturnDocument
from logger.logger import Logger
from bson import ObjectId

class Service:
    """Service class to that implements the logic of the CRUD operations for tickets"""

    def __init__(self, db_conn):
        self.logger = Logger()
        self.db_conn = db_conn

    def get_analytics_data(self):
        """Function to get counts for all form types for the dashboard"""
        try:
            collections = ['vpnMayo', 'internet', 'rfc', 'tel']
            analytics_data = []
            
            for collection in collections:
                count = self.db_conn.db[collection].count_documents({})
                label = collection.title()
                
                analytics_data.append({
                    "label": label,
                    "value": count
                })
            
            return analytics_data, 200
            
        except Exception as e:
            self.logger.error(f"Error fetching analytics data: {e}")
            return {"error": f"Error fetching analytics data: {e}"}, 500
        
    def get_daily_registration_count(self, collection_name, formatted_date):
        """Function to get the registration count for a specific collection and date."""
        try:
            collection = self.db_conn.db[collection_name]
            record = collection.find_one({"_id": formatted_date})
            return record
        except Exception as e:
            self.logger.error(f"Error querying {collection_name} for {formatted_date}: {e}")
            return None

    def get_weekly_registration_stats(self):
        """Obtiene estadísticas semanales de registros con porcentajes de cambio"""
        try:
            collections = ['vpnMayoCounters', 'internetCounters', 'rfcCounters', 'telCounters']
            label_mapping = {
                'vpnMayoCounters': 'vpn',
                'internetCounters': 'internet',
                'rfcCounters': 'rfc',
                'telCounters': 'telefonia'
            }
            
            end_date = datetime.now()
            start_date = end_date - timedelta(weeks=6)
            
            results = {}
            
            for collection in collections:
                # Obtener conteos por semana
                weekly_counts = self._get_weekly_counts_from_daily(collection, start_date, end_date)
                
                # Calcular porcentajes de cambio
                stats_with_change = self._calculate_weekly_changes(weekly_counts)
                
                # Formatear nombre para el frontend
                formatted_name = label_mapping.get(collection, collection)
                results[formatted_name] = stats_with_change
            
            return results, 200
            
        except Exception as e:
            self.logger.error(f"Error getting weekly registration stats: {e}")
            return {"error": f"Error getting weekly registration stats: {e}"}, 500
    
    def _get_weekly_counts_from_daily(self, collection_name, start_date, end_date):
        """Obtiene conteos semanales sumando los registros diarios"""
        weekly_counts = []
        
        # Generar todas las semanas en el rango
        current_week_start = start_date - timedelta(days=start_date.weekday())
        
        while current_week_start <= end_date:
            week_end = current_week_start + timedelta(days=6)
            week_total = 0
            
            # Sumar registros para cada día de la semana
            for day in range(7):
                current_date = current_week_start + timedelta(days=day)
                formatted_date = current_date.strftime("%y%m%d")
                
                record = self.get_daily_registration_count(collection_name, formatted_date)
                week_total += record['seq'] if record else 0
            
            # Agregar datos de la semana
            week_str = current_week_start.strftime("Semana #%U")
            weekly_counts.append({
                "week": week_str,
                "count": week_total
            })
            
            # Mover a la siguiente semana
            current_week_start += timedelta(weeks=1)
        
        return weekly_counts
    
    def _calculate_weekly_changes(self, weekly_counts):
        """Calcula porcentajes de cambio semana a semana"""
        if len(weekly_counts) < 2:
            return weekly_counts
        
        # Ordenar por semana (más antigua primero)
        sorted_counts = sorted(weekly_counts, key=lambda x: x['week'])
        
        # Calcular cambios porcentuales
        for i in range(1, len(sorted_counts)):
            current_count = sorted_counts[i]['count']
            previous_count = sorted_counts[i-1]['count']
            
            # Manejar casos especiales con ceros
            if previous_count == 0:
                if current_count == 0:
                    change_percent = 0.0
                else:
                    change_percent = 100.0  # Crecimiento infinito (de 0 a X)
            else:
                change_percent = ((current_count - previous_count) / previous_count) * 100
            
            sorted_counts[i]['percent'] = round(change_percent, 2)
        
        # La primera semana no tiene cambio porcentual
        if len(sorted_counts) > 0:
            sorted_counts[0]['percent'] = 0.0
        
        # Devolver solo las últimas 6 semanas
        return sorted_counts[-6:]

    def VPN_Registros_Resumen(self):
        """Te da un resumen de los registros VPN 2.0 para el Dashboard"""
        """
        Extrae _id, nombre, extension, correo y movimiento de todos los registros
        en la colección 'vpnMayo'.
        """
        # Necesitamos devolver los registros asi:
        # NoFormato, Nombre, Correo, Extension, Movimiento

        try:
            vpn_collection = self.db_conn.db['vpnMayo']
            projection = {
                "_id": 1,
                "nombre": 1,
                "correo": 1,
                "movimiento": 1,
                "puestojefe": 1
            }
            registros_vpn = list(vpn_collection.find({}, projection))
            return registros_vpn, 200
        except Exception as e:
            self.logger.error(f"Error al obtener datos de la colección 'vpnMayo': {e}")
            return {"error": "Error al obtener datos de VPN_Mayo"}, 500
        
    def Internet_Registros_Resumen(self):
        """Te da un resumen de los registros VPN para el Dashboard"""
        """
        Extrae _id, nombreUsuario, correoUsuario, ipUsuario de todos los registros
        en la colección 'internet'.
        """
        # Necesitamos devolver los registros asi:
        # NoFormato, Nombre, Correo, Extension, Movimiento

        try:
            internet_collection = self.db_conn.db['internet']
            projection = {
                "_id": 1,
                "nombreUsuario": 1,
                "correoUsuario": 1,
                "ipUsuario": 1,
                "nombreJefe": 1
            }
            registros_internet = list(internet_collection.find({}, projection))
            return registros_internet, 200
        except Exception as e:
            self.logger.error(f"Error al obtener datos de la colección 'internet': {e}")
            return {"error": "Error al obtener datos de Internet"}, 500
        
    def Telefonia_Registros_Resumen(self):
        """Te da un resumen de los registros VPN para el Dashboard"""
        """
        Extrae _id, nombreUsuario, correoUsuario, movimiento de todos los registros
        en la colección 'telefonia'.
        """
        # Necesitamos devolver los registros asi:
        # NoFormato, Nombre, Correo, Extension, Movimiento

        try:
            telefonia_collection = self.db_conn.db['tel']
            projection = {
                "_id": 1,
                "nombreUsuario": 1,
                "correoUsuario": 1,
                "movimiento": 1,
                "nombreJefe": 1
            }
            registros_telefonia = list(telefonia_collection.find({}, projection))
            return registros_telefonia, 200
        except Exception as e:
            self.logger.error(f"Error al obtener datos de la colección 'telefonia': {e}")
            return {"error": "Error al obtener datos de Telefonia"}, 500
        
    def RFC_Registros_Resumen(self):
        """Te da un resumen de los registros RFC para el Dashboard"""
        """
        Extrae _id, nombreUsuario, correoUsuario, movimiento de todos los registros
        en la colección 'rfc'.
        """
        # Necesitamos devolver los registros asi:
        # NoFormato, Nombre, Correo, Extension, Movimiento

        try:
            rfc_collection = self.db_conn.db['rfc']
            projection = {
                "_id": 1,
                "noticket": 1,
                "memo": 1,
                "descbreve": 1,
                "nombreJefe": 1
            }
            registros_rfc = list(rfc_collection.find({}, projection))
            return registros_rfc, 200
        except Exception as e:
            self.logger.error(f"Error al obtener datos de la colección 'telefonia': {e}")
            return {"error": "Error al obtener datos de Telefonia"}, 500