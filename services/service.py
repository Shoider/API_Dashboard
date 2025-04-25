import datetime
from flask import jsonify
from pymongo import ReturnDocument
from logger.logger import Logger
from bson import ObjectId

class Service:
    """Service class to that implements the logic of the CRUD operations for tickets"""

    def __init__(self, db_conn):
        self.logger = Logger()
        self.db_conn = db_conn

    def get_all_VPN(self):
        """Function to fetch all VPN registers from the database"""
        try:
            vpn = list(self.db_conn.db.vpn.find())
            return self._convert_objectid_to_str(vpn)
        except Exception as e:
            self.logger.error(f"Error fetching all VPN registers from database: {e}")
            return (
                jsonify({"error": f"Error fetching all VPN registers from database: {e}"}),
                500,
            )

    def add_VPN(self, new_vpn):
        """Function to add a VPN register to the database with a custom ID"""
        try:
            now = datetime.datetime.now()
            yy = now.strftime("%y")
            mm = now.strftime("%m")
            dd = now.strftime("%d")
            base_id = f"{yy}{mm}{dd}"

            # Atomically find and increment the daily counter
            counter_doc = self.db_conn.db.vpnCounters.find_one_and_update(
                {"_id": base_id},
                {"$inc": {"seq": 1}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )

            sequence = counter_doc.get("seq", 1)
            padded_sequence = str(sequence).zfill(4)
            custom_id = f"{base_id}{padded_sequence}"
            new_vpn["_id"] = custom_id

            self.db_conn.db.vpn.insert_one(new_vpn)
            return {"_id": custom_id}, 201
        except Exception as e:
            self.logger.error(f"Error adding VPN register to database with custom ID: {e}")
            return jsonify({"error": f"Error adding VPN register to database with custom ID: {e}"}), 500
        
    def _convert_objectid_to_str(self, data):
        """Helper function to convert ObjectId to string in a list of dictionaries"""
        if isinstance(data, list):
            for item in data:
                self._convert_objectid_to_str(item)
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, ObjectId):
                    data[key] = str(value)
                elif isinstance(value, (list, dict)):
                    self._convert_objectid_to_str(value)
        return data
    
    ## NUEVO

    def get_analytics_data(self):
        """Function to get counts for all form types for the dashboard"""
        try:
            collections = ['vpn', 'internet', 'rfc', 'tel']
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
