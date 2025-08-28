from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from logger.logger import Logger

class FileGeneratorRoute(Blueprint):
    """Class to handle the routes for file generation"""

    def __init__(self, service, schema):
        super().__init__("file_generator", __name__)
        self.logger = Logger()
        self.schema = schema
        self.service = service
        self.register_routes()

    def register_routes(self): 
        """Function to register the routes for file generation"""
        self.route("/api2/v1/form-counts", methods=["GET"])(self.get_form_counts)
        self.route("/api2/v1/weekly-registrations", methods=["GET"])(self.get_weekly_registrations)
        self.route("/api2/v1/old-weekly-registrations", methods=["GET"])(self.get_old_weekly_registrations)
        self.route("/api2/v1/weekly-stats", methods=["GET"])(self.get_weekly_stats)
        self.route("/api2/v1/vpnGet", methods=["POST"])(self.vpnGet)
        self.route("/api2/v1/internetGet", methods=["POST"])(self.internetGet)
        self.route("/api2/v1/telefoniaGet", methods=["POST"])(self.telefoniaGet)
        self.route("/api2/v1/rfcGet", methods=["POST"])(self.rfcGet)
        self.route("/api2/v1/rfcFiltrado", methods=["POST"])(self.rfcFiltrado)
        self.route("/api2/v1/telFiltrado", methods=["POST"])(self.telFiltrado)
        self.route("/api2/v1/vpnFiltrado", methods=["POST"])(self.vpnFiltrado)
        self.route("/api2/v1/interFiltrado", methods=["POST"])(self.interFiltrado)
        self.route("/api2/healthcheck", methods=["GET"])(self.healthcheck)

    def fetch_request_data(self):
        """Function to fetch the request data"""
        try:
            request_data = request.json
            if not request_data:
                return 400, "Invalid data", None
            return 200, None, request_data
        except Exception as e:
            self.logger.error(f"Error fetching request data: {e}")
            return 500, "Error fetching request data", None
        
    def get_form_counts(self):
        """Endpoint to get form counts for analytics dashboard"""
        try:
            analytics_data, status_code = self.service.get_analytics_data()
            return jsonify(analytics_data), status_code
        except Exception as e:
            self.logger.error(f"Error in get_form_counts: {e}")
            return jsonify({"error": "Internal server error"}), 500
        
    def get_weekly_registrations(self):
        """Endpoint to get the number of registrations for the last 6 days."""
        try:
            today = datetime.now()
            weekday = today.weekday()  # Monday is 0 and Sunday is 6
            days_to_subtract = weekday  # To get back to Monday

            start_of_week = today - timedelta(days=days_to_subtract)

            weekly_data = []
            collections = ['vpnMayoCounters', 'internetCounters', 'rfcCounters', 'telCounters']
            form_labels = {'vpnMayoCounters': 'VPN', 'internetCounters': 'Internet', 'rfcCounters': 'RFC', 'telCounters': 'Telefono'}

            for i in range(6):  # Get data for the last 6 days (including today if it's within the week)
                current_date = start_of_week + timedelta(days=i)
                formatted_date = current_date.strftime("%y%m%d")

                daily_counts = {}
                for collection in collections:
                    record = self.service.get_daily_registration_count(collection, formatted_date)
                    daily_counts[form_labels[collection]] = record['seq'] if record else 0
                
                weekly_data.append({
                    "Fecha": current_date.strftime("%d-%m-%Y"),
                    "Cuenta": daily_counts
                })

            return jsonify(weekly_data), 200
        except Exception as e:
            self.logger.error(f"Error in get_weekly_registrations: {e}")
            return jsonify({"error": "Internal server error"}), 500
        
    def get_old_weekly_registrations(self):
        """Endpoint to get the number of registrations for the last 6 days."""
        try:
            today = datetime.now()
            weekday = today.weekday()  # Monday is 0 and Sunday is 6
            days_to_subtract_to_current_monday = weekday

            # Calculate the Monday of the current week
            current_monday = today - timedelta(days=days_to_subtract_to_current_monday)

            # Calculate the Monday of the PREVIOUS week
            start_of_previous_week = current_monday - timedelta(weeks=1)

            weekly_data = []
            collections = ['vpnMayoCounters', 'internetCounters', 'rfcCounters', 'telCounters']
            form_labels = {'vpnMayoCounters': 'VPN', 'internetCounters': 'Internet', 'rfcCounters': 'RFC', 'telCounters': 'Telefono'}

            for i in range(6):  # Get data for the last 6 days (including today if it's within the week)
                current_date = start_of_previous_week + timedelta(days=i)
                formatted_date = current_date.strftime("%y%m%d")

                daily_counts = {}
                for collection in collections:
                    record = self.service.get_daily_registration_count(collection, formatted_date)
                    daily_counts[form_labels[collection]] = record['seq'] if record else 0
                
                weekly_data.append({
                    "Fecha": current_date.strftime("%d-%m-%Y"),
                    "Cuenta": daily_counts
                })

            return jsonify(weekly_data), 200
        except Exception as e:
            self.logger.error(f"Error in get_weekly_registrations: {e}")
            return jsonify({"error": "Internal server error"}), 500
        
    def get_weekly_stats(self):
        """Endpoint para obtener estadísticas semanales con porcentajes de cambio"""
        try:
            weekly_stats, status_code = self.service.get_weekly_registration_stats()
            return jsonify(weekly_stats), status_code
        except Exception as e:
            self.logger.error(f"Error in get_weekly_stats: {e}")
            return jsonify({"error": "Internal server error"}), 500
        
    def vpnGet(self):
        """Endpoint para obtener los datos de VPN"""
        try:
            vpn_data, status_code = self.service.VPN_Registros_Resumen()
            self.logger.debug("Datos obtenidos de VPN: ")
            self.logger.debug(vpn_data)
            return jsonify(vpn_data), status_code
        except Exception as e:
            self.logger.error(f"Error en get_vpn_registrations: {e}")
            return jsonify({"error": "Internal server error"}), 500
    def internetGet(self):
        """Endpoint para obtener los datos de VPN"""
        try:
            internet_data, status_code = self.service.Internet_Registros_Resumen()
            self.logger.debug("Datos obtenidos de Internet: ")
            self.logger.debug(internet_data)
            return jsonify(internet_data), status_code
        except Exception as e:
            self.logger.error(f"Error en get_internet_registrations: {e}")
            return jsonify({"error": "Internal server error"}), 500
    def telefoniaGet(self):
        """Endpoint para obtener los datos de VPN"""
        try:
            telefonia_data, status_code = self.service.Telefonia_Registros_Resumen()
            self.logger.debug("Datos obtenidos de Telefonia: ")
            self.logger.debug(telefonia_data)
            return jsonify(telefonia_data), status_code
        except Exception as e:
            self.logger.error(f"Error en get_telefonia_registrations: {e}")
            return jsonify({"error": "Internal server error"}), 500
        
    def rfcGet(self):
        """Endpoint para obtener los datos de VPN"""
        try:
            rfc_data, status_code = self.service.RFC_Registros_Resumen()
            self.logger.debug("Datos obtenidos de RFC: ")
            self.logger.debug(rfc_data)
            return jsonify(rfc_data), status_code
        except Exception as e:
            self.logger.error(f"Error en get_rfc_registrations: {e}")
            return jsonify({"error": "Internal server error"}), 500
        
    # filepath: routes.py
    def rfcFiltrado(self):
        """Filtrado ya hecho en mongodb"""
        try: 
            rfc_filter_data, status_code = self.service.RFC_Filtro()
            self.logger.debug("Datos obtenidos del filtro de RFC")
            self.logger.debug(rfc_filter_data)
            return jsonify(rfc_filter_data), status_code
        except Exception as e:
            self.logger.error(f"Error en rfc_filtrado:{e}")
            return jsonify({"error": "Internal server error"}), 500
        
    def telFiltrado(self):
        """Filtrado ya hecho en mongodb"""
        try: 
            tel_filter_data, status_code = self.service.Telefonia_Filtro()
            self.logger.debug("Datos obtenidos del filtro de Telefonia")
            self.logger.debug(tel_filter_data)
            return jsonify(tel_filter_data), status_code
        except Exception as e:
            self.logger.error(f"Error en rfc_filtrado:{e}")
            return jsonify({"error": "Internal server error"}), 500
    def vpnFiltrado(self):
        """Filtrado ya hecho en mongodb"""
        try: 
            vpn_filter_data, status_code = self.service.VPN_Filtro()
            self.logger.debug("Datos obtenidos del filtro de VPN")
            self.logger.debug(vpn_filter_data)
            return jsonify(vpn_filter_data), status_code
        except Exception as e:
            self.logger.error(f"Error en vpn_filtrado:{e}")
            return jsonify({"error": "Internal server error"}), 500
    def interFiltrado(self):
        """Filtrado ya hecho en mongodb"""
        try: 
            inter_filter_data, status_code = self.service.Inter_Filtro()
            self.logger.debug("Datos obtenidos del filtro de Internet")
            self.logger.debug(inter_filter_data)
            return jsonify(inter_filter_data), status_code
        except Exception as e:
            self.logger.error(f"Error en inter_filtrado:{e}")
            return jsonify({"error": "Internal server error"}), 500

    def healthcheck(self):
        """Function to check the health of the services API inside the docker container"""
        return jsonify({"status": "Up"}), 200