import requests
import json
from typing import Dict, List, Optional, Tuple


class EmergencyHospitalFinder:
    """Emergency hospital finder using Google Places API."""
    
    def __init__(self, google_api_key: str):
        """Initialize with Google API key."""
        self.google_api_key = google_api_key
        self.emergency_numbers = {
            "108": "National Medical Emergency Service (India)",
            "102": "Ambulance Service (India)",
            "911": "Emergency Services (USA)",
            "112": "Emergency Services (Europe)"
        }
    
    def get_location_from_ip(self) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """Auto-detect user location via IP address."""
        try:
            ipinfo_resp = requests.get("https://ipinfo.io/json", timeout=10)
            ipinfo_resp.raise_for_status()
            data = ipinfo_resp.json()
            
            loc = data.get("loc", "")  # format: "lat,long"
            if loc:
                latitude, longitude = map(float, loc.split(","))
                city = data.get("city", "Unknown City")
                region = data.get("region", "Unknown Region")
                location_str = f"{city}, {region}"
                return latitude, longitude, location_str
                
        except Exception as e:
            print(f"Failed to auto-detect location: {e}")
            
        return None, None, None
    
    def find_nearby_hospitals(self, lat: float, lon: float, radius: int = 2000) -> List[Dict]:
        """Find nearby hospitals using Google Places API."""
        try:
            nearby_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lon}",
                "radius": radius,
                "type": "hospital",
                "key": self.google_api_key
            }
            
            response = requests.get(nearby_url, params=params, timeout=10)
            response.raise_for_status()
            results = response.json().get("results", [])
            
            return results
            
        except Exception as e:
            print(f"Error finding nearby hospitals: {e}")
            return []
    
    def get_hospital_details(self, place_id: str) -> Dict:
        """Get detailed information about a hospital including phone number."""
        try:
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            params = {
                "place_id": place_id,
                "fields": "formatted_phone_number,website,rating,opening_hours,formatted_address",
                "key": self.google_api_key
            }
            
            response = requests.get(details_url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json().get("result", {})
            
            return {
                "phone": result.get("formatted_phone_number", "Phone not available"),
                "website": result.get("website", "Website not available"),
                "rating": result.get("rating", "N/A"),
                "opening_hours": result.get("opening_hours", {}).get("weekday_text", []),
                "address": result.get("formatted_address", "Address not available")
            }
            
        except Exception as e:
            print(f"Error getting hospital details: {e}")
            return {
                "phone": "Phone not available",
                "website": "Website not available", 
                "rating": "N/A",
                "opening_hours": [],
                "address": "Address not available"
            }
    
    def get_emergency_info(self, lat: float = None, lon: float = None, radius: int = 2000) -> Dict:
        """Get complete emergency information including numbers and nearby hospitals."""
        result = {
            "success": False,
            "emergency_numbers": self.emergency_numbers,
            "location": None,
            "hospitals": [],
            "error": None
        }
        
        try:
            # Auto-detect location if not provided
            if lat is None or lon is None:
                detected_lat, detected_lon, location_str = self.get_location_from_ip()
                if detected_lat and detected_lon:
                    lat, lon = detected_lat, detected_lon
                    result["location"] = location_str
                else:
                    result["error"] = "Could not determine location"
                    return result
            
            # Find nearby hospitals
            hospitals = self.find_nearby_hospitals(lat, lon, radius)
            
            # Get detailed information for each hospital
            detailed_hospitals = []
            for hospital in hospitals[:10]:  # Limit to top 10 hospitals
                hospital_info = {
                    "name": hospital.get("name", "Unknown Hospital"),
                    "vicinity": hospital.get("vicinity", "Address not available"),
                    "rating": hospital.get("rating", "N/A"),
                    "place_id": hospital.get("place_id", "")
                }
                
                # Get additional details
                if hospital_info["place_id"]:
                    details = self.get_hospital_details(hospital_info["place_id"])
                    hospital_info.update(details)
                
                detailed_hospitals.append(hospital_info)
            
            result["hospitals"] = detailed_hospitals
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
        
        return result 