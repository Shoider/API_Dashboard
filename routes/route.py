import tempfile
import shutil
import os

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime, timedelta
from io import BytesIO
from logger.logger import Logger
from marshmallow import ValidationError

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
            collections = ['vpnCounters', 'internetCounters', 'rfcCounters', 'telCounters']
            form_labels = {'vpnCounters': 'VPN', 'internetCounters': 'Internet', 'rfcCounters': 'RFC', 'telCounters': 'Telefono'}

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
            collections = ['vpnCounters', 'internetCounters', 'rfcCounters', 'telCounters']
            form_labels = {'vpnCounters': 'VPN', 'internetCounters': 'Internet', 'rfcCounters': 'RFC', 'telCounters': 'Telefono'}

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

    def healthcheck(self):
        """Function to check the health of the services API inside the docker container"""
        return jsonify({"status": "Up"}), 200

