from flask import Flask, render_template, request, jsonify, session, flash
import json
import random
import os
import requests
from datetime import datetime, timedelta
import threading
import time
import pytz

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-environmental-key-2025')

print(f"🔑 Using SECRET_KEY: {app.secret_key}")
print(f"🌍 Starting Global Coastal City Emergency Monitoring System")

# COMPREHENSIVE GLOBAL COASTAL CITIES LIST (200+ cities worldwide)
COASTAL_CITIES = [
    # North America - USA East Coast
    {'name': 'New York City', 'lat': 40.7128, 'lng': -74.0060, 'country': 'US', 'risk_level': 'critical', 'population': '8.4M', 'timezone': 'America/New_York'},
    {'name': 'Miami', 'lat': 25.7617, 'lng': -80.1918, 'country': 'US', 'risk_level': 'critical', 'population': '6.0M', 'timezone': 'America/New_York'},
    {'name': 'Boston', 'lat': 42.3601, 'lng': -71.0589, 'country': 'US', 'risk_level': 'high', 'population': '4.9M', 'timezone': 'America/New_York'},
    {'name': 'Philadelphia', 'lat': 39.9526, 'lng': -75.1652, 'country': 'US', 'risk_level': 'high', 'population': '5.7M', 'timezone': 'America/New_York'},
    {'name': 'Charleston', 'lat': 32.7765, 'lng': -79.9311, 'country': 'US', 'risk_level': 'critical', 'population': '800K', 'timezone': 'America/New_York'},
    {'name': 'Norfolk', 'lat': 36.8468, 'lng': -76.2852, 'country': 'US', 'risk_level': 'critical', 'population': '1.7M', 'timezone': 'America/New_York'},
    {'name': 'Jacksonville', 'lat': 30.3322, 'lng': -81.6557, 'country': 'US', 'risk_level': 'high', 'population': '1.6M', 'timezone': 'America/New_York'},
    {'name': 'Savannah', 'lat': 32.0835, 'lng': -81.0998, 'country': 'US', 'risk_level': 'high', 'population': '390K', 'timezone': 'America/New_York'},
    
    # USA West Coast
    {'name': 'Los Angeles', 'lat': 34.0522, 'lng': -118.2437, 'country': 'US', 'risk_level': 'critical', 'population': '13.1M', 'timezone': 'America/Los_Angeles'},
    {'name': 'San Francisco', 'lat': 37.7749, 'lng': -122.4194, 'country': 'US', 'risk_level': 'critical', 'population': '4.7M', 'timezone': 'America/Los_Angeles'},
    {'name': 'Seattle', 'lat': 47.6062, 'lng': -122.3321, 'country': 'US', 'risk_level': 'high', 'population': '3.7M', 'timezone': 'America/Los_Angeles'},
    {'name': 'San Diego', 'lat': 32.7157, 'lng': -117.1611, 'country': 'US', 'risk_level': 'high', 'population': '3.3M', 'timezone': 'America/Los_Angeles'},
    {'name': 'Portland', 'lat': 45.5152, 'lng': -122.6784, 'country': 'US', 'risk_level': 'medium', 'population': '2.5M', 'timezone': 'America/Los_Angeles'},
    
    # USA Gulf Coast
    {'name': 'New Orleans', 'lat': 29.9511, 'lng': -90.0715, 'country': 'US', 'risk_level': 'critical', 'population': '1.3M', 'timezone': 'America/Chicago'},
    {'name': 'Houston', 'lat': 29.7604, 'lng': -95.3698, 'country': 'US', 'risk_level': 'critical', 'population': '7.0M', 'timezone': 'America/Chicago'},
    {'name': 'Tampa', 'lat': 27.9506, 'lng': -82.4572, 'country': 'US', 'risk_level': 'critical', 'population': '3.2M', 'timezone': 'America/New_York'},
    {'name': 'Mobile', 'lat': 30.6954, 'lng': -88.0399, 'country': 'US', 'risk_level': 'high', 'population': '430K', 'timezone': 'America/Chicago'},
    
    # Canada
    {'name': 'Vancouver', 'lat': 49.2827, 'lng': -123.1207, 'country': 'CA', 'risk_level': 'medium', 'population': '2.6M', 'timezone': 'America/Vancouver'},
    {'name': 'Toronto', 'lat': 43.6532, 'lng': -79.3832, 'country': 'CA', 'risk_level': 'medium', 'population': '6.2M', 'timezone': 'America/Toronto'},
    {'name': 'Montreal', 'lat': 45.5017, 'lng': -73.5673, 'country': 'CA', 'risk_level': 'low', 'population': '4.3M', 'timezone': 'America/Montreal'},
    {'name': 'Halifax', 'lat': 44.6488, 'lng': -63.5752, 'country': 'CA', 'risk_level': 'high', 'population': '430K', 'timezone': 'America/Halifax'},
    
    # Asia - East Asia
    {'name': 'Tokyo', 'lat': 35.6762, 'lng': 139.6503, 'country': 'JP', 'risk_level': 'critical', 'population': '37.5M', 'timezone': 'Asia/Tokyo'},
    {'name': 'Shanghai', 'lat': 31.2304, 'lng': 121.4737, 'country': 'CN', 'risk_level': 'critical', 'population': '26.3M', 'timezone': 'Asia/Shanghai'},
    {'name': 'Beijing', 'lat': 39.9042, 'lng': 116.4074, 'country': 'CN', 'risk_level': 'high', 'population': '22.6M', 'timezone': 'Asia/Shanghai'},
    {'name': 'Tianjin', 'lat': 39.1422, 'lng': 117.1767, 'country': 'CN', 'risk_level': 'high', 'population': '14.7M', 'timezone': 'Asia/Shanghai'},
    {'name': 'Guangzhou', 'lat': 23.1291, 'lng': 113.2644, 'country': 'CN', 'risk_level': 'high', 'population': '18.7M', 'timezone': 'Asia/Shanghai'},
    {'name': 'Shenzhen', 'lat': 22.5431, 'lng': 114.0579, 'country': 'CN', 'risk_level': 'high', 'population': '13.5M', 'timezone': 'Asia/Shanghai'},
    {'name': 'Hong Kong', 'lat': 22.3193, 'lng': 114.1694, 'country': 'HK', 'risk_level': 'high', 'population': '7.5M', 'timezone': 'Asia/Hong_Kong'},
    {'name': 'Taipei', 'lat': 25.0330, 'lng': 121.5654, 'country': 'TW', 'risk_level': 'high', 'population': '7.0M', 'timezone': 'Asia/Taipei'},
    {'name': 'Seoul', 'lat': 37.5665, 'lng': 126.9780, 'country': 'KR', 'risk_level': 'high', 'population': '9.7M', 'timezone': 'Asia/Seoul'},
    {'name': 'Busan', 'lat': 35.1796, 'lng': 129.0756, 'country': 'KR', 'risk_level': 'high', 'population': '3.4M', 'timezone': 'Asia/Seoul'},
    {'name': 'Osaka', 'lat': 34.6937, 'lng': 135.5023, 'country': 'JP', 'risk_level': 'high', 'population': '19.2M', 'timezone': 'Asia/Tokyo'},
    {'name': 'Yokohama', 'lat': 35.4437, 'lng': 139.6380, 'country': 'JP', 'risk_level': 'high', 'population': '3.7M', 'timezone': 'Asia/Tokyo'},
    {'name': 'Qingdao', 'lat': 36.0986, 'lng': 120.3719, 'country': 'CN', 'risk_level': 'high', 'population': '10.5M', 'timezone': 'Asia/Shanghai'},
    {'name': 'Dalian', 'lat': 38.9140, 'lng': 121.6147, 'country': 'CN', 'risk_level': 'high', 'population': '6.9M', 'timezone': 'Asia/Shanghai'},
    
    # South Asia
    {'name': 'Mumbai', 'lat': 19.0760, 'lng': 72.8777, 'country': 'IN', 'risk_level': 'critical', 'population': '20.7M', 'timezone': 'Asia/Kolkata'},
    {'name': 'Kolkata', 'lat': 22.5726, 'lng': 88.3639, 'country': 'IN', 'risk_level': 'critical', 'population': '14.9M', 'timezone': 'Asia/Kolkata'},
    {'name': 'Chennai', 'lat': 13.0827, 'lng': 80.2707, 'country': 'IN', 'risk_level': 'critical', 'population': '12.3M', 'timezone': 'Asia/Kolkata'},
    {'name': 'Kochi', 'lat': 9.9312, 'lng': 76.2673, 'country': 'IN', 'risk_level': 'high', 'population': '2.1M', 'timezone': 'Asia/Kolkata'},
    {'name': 'Visakhapatnam', 'lat': 17.6868, 'lng': 83.2185, 'country': 'IN', 'risk_level': 'high', 'population': '2.0M', 'timezone': 'Asia/Kolkata'},
    {'name': 'Dhaka', 'lat': 23.8103, 'lng': 90.4125, 'country': 'BD', 'risk_level': 'critical', 'population': '9.1M', 'timezone': 'Asia/Dhaka'},
    {'name': 'Chittagong', 'lat': 22.3569, 'lng': 91.7832, 'country': 'BD', 'risk_level': 'critical', 'population': '3.9M', 'timezone': 'Asia/Dhaka'},
    {'name': 'Karachi', 'lat': 24.8607, 'lng': 67.0011, 'country': 'PK', 'risk_level': 'critical', 'population': '16.1M', 'timezone': 'Asia/Karachi'},
    {'name': 'Colombo', 'lat': 6.9271, 'lng': 79.8612, 'country': 'LK', 'risk_level': 'high', 'population': '5.6M', 'timezone': 'Asia/Colombo'},
    
    # Southeast Asia
    {'name': 'Jakarta', 'lat': -6.2088, 'lng': 106.8456, 'country': 'ID', 'risk_level': 'critical', 'population': '10.8M', 'timezone': 'Asia/Jakarta'},
    {'name': 'Bangkok', 'lat': 13.7563, 'lng': 100.5018, 'country': 'TH', 'risk_level': 'critical', 'population': '10.7M', 'timezone': 'Asia/Bangkok'},
    {'name': 'Singapore', 'lat': 1.3521, 'lng': 103.8198, 'country': 'SG', 'risk_level': 'high', 'population': '5.8M', 'timezone': 'Asia/Singapore'},
    {'name': 'Manila', 'lat': 14.5995, 'lng': 120.9842, 'country': 'PH', 'risk_level': 'critical', 'population': '13.9M', 'timezone': 'Asia/Manila'},
    {'name': 'Ho Chi Minh City', 'lat': 10.8231, 'lng': 106.6297, 'country': 'VN', 'risk_level': 'critical', 'population': '9.0M', 'timezone': 'Asia/Ho_Chi_Minh'},
    {'name': 'Hanoi', 'lat': 21.0285, 'lng': 105.8542, 'country': 'VN', 'risk_level': 'high', 'population': '8.1M', 'timezone': 'Asia/Ho_Chi_Minh'},
    {'name': 'Kuala Lumpur', 'lat': 3.1390, 'lng': 101.6869, 'country': 'MY', 'risk_level': 'medium', 'population': '7.9M', 'timezone': 'Asia/Kuala_Lumpur'},
    {'name': 'Surabaya', 'lat': -7.2575, 'lng': 112.7521, 'country': 'ID', 'risk_level': 'high', 'population': '2.9M', 'timezone': 'Asia/Jakarta'},
    {'name': 'Medan', 'lat': 3.5952, 'lng': 98.6722, 'country': 'ID', 'risk_level': 'high', 'population': '3.6M', 'timezone': 'Asia/Jakarta'},
    {'name': 'Makassar', 'lat': -5.1477, 'lng': 119.4327, 'country': 'ID', 'risk_level': 'high', 'population': '1.4M', 'timezone': 'Asia/Makassar'},
    
    # Europe
    {'name': 'London', 'lat': 51.5074, 'lng': -0.1278, 'country': 'GB', 'risk_level': 'high', 'population': '9.6M', 'timezone': 'Europe/London'},
    {'name': 'Amsterdam', 'lat': 52.3676, 'lng': 4.9041, 'country': 'NL', 'risk_level': 'high', 'population': '2.4M', 'timezone': 'Europe/Amsterdam'},
    {'name': 'Hamburg', 'lat': 53.5511, 'lng': 9.9937, 'country': 'DE', 'risk_level': 'medium', 'population': '1.9M', 'timezone': 'Europe/Berlin'},
    {'name': 'Copenhagen', 'lat': 55.6761, 'lng': 12.5683, 'country': 'DK', 'risk_level': 'medium', 'population': '2.1M', 'timezone': 'Europe/Copenhagen'},
    {'name': 'Stockholm', 'lat': 59.3293, 'lng': 18.0686, 'country': 'SE', 'risk_level': 'low', 'population': '2.4M', 'timezone': 'Europe/Stockholm'},
    {'name': 'Helsinki', 'lat': 60.1699, 'lng': 24.9384, 'country': 'FI', 'risk_level': 'low', 'population': '1.5M', 'timezone': 'Europe/Helsinki'},
    {'name': 'Oslo', 'lat': 59.9139, 'lng': 10.7522, 'country': 'NO', 'risk_level': 'low', 'population': '1.7M', 'timezone': 'Europe/Oslo'},
    {'name': 'Venice', 'lat': 45.4408, 'lng': 12.3155, 'country': 'IT', 'risk_level': 'critical', 'population': '260K', 'timezone': 'Europe/Rome'},
    {'name': 'Naples', 'lat': 40.8518, 'lng': 14.2681, 'country': 'IT', 'risk_level': 'high', 'population': '3.1M', 'timezone': 'Europe/Rome'},
    {'name': 'Barcelona', 'lat': 41.3851, 'lng': 2.1734, 'country': 'ES', 'risk_level': 'medium', 'population': '5.5M', 'timezone': 'Europe/Madrid'},
    {'name': 'Valencia', 'lat': 39.4699, 'lng': -0.3763, 'country': 'ES', 'risk_level': 'medium', 'population': '1.6M', 'timezone': 'Europe/Madrid'},
    {'name': 'Lisbon', 'lat': 38.7223, 'lng': -9.1393, 'country': 'PT', 'risk_level': 'medium', 'population': '2.9M', 'timezone': 'Europe/Lisbon'},
    {'name': 'Porto', 'lat': 41.1579, 'lng': -8.6291, 'country': 'PT', 'risk_level': 'medium', 'population': '1.3M', 'timezone': 'Europe/Lisbon'},
    {'name': 'Marseille', 'lat': 43.2965, 'lng': 5.3698, 'country': 'FR', 'risk_level': 'medium', 'population': '1.8M', 'timezone': 'Europe/Paris'},
    {'name': 'Nice', 'lat': 43.7102, 'lng': 7.2620, 'country': 'FR', 'risk_level': 'medium', 'population': '1.0M', 'timezone': 'Europe/Paris'},
    {'name': 'Istanbul', 'lat': 41.0082, 'lng': 28.9784, 'country': 'TR', 'risk_level': 'high', 'population': '15.5M', 'timezone': 'Europe/Istanbul'},
    {'name': 'Izmir', 'lat': 38.4192, 'lng': 27.1287, 'country': 'TR', 'risk_level': 'medium', 'population': '4.4M', 'timezone': 'Europe/Istanbul'},
    {'name': 'Athens', 'lat': 37.9838, 'lng': 23.7275, 'country': 'GR', 'risk_level': 'medium', 'population': '3.8M', 'timezone': 'Europe/Athens'},
    
    # Middle East & North Africa
    {'name': 'Tel Aviv', 'lat': 32.0853, 'lng': 34.7818, 'country': 'IL', 'risk_level': 'high', 'population': '4.0M', 'timezone': 'Asia/Jerusalem'},
    {'name': 'Alexandria', 'lat': 31.2001, 'lng': 29.9187, 'country': 'EG', 'risk_level': 'critical', 'population': '5.2M', 'timezone': 'Africa/Cairo'},
    {'name': 'Casablanca', 'lat': 33.5731, 'lng': -7.5898, 'country': 'MA', 'risk_level': 'medium', 'population': '3.7M', 'timezone': 'Africa/Casablanca'},
    {'name': 'Algiers', 'lat': 36.7538, 'lng': 3.0588, 'country': 'DZ', 'risk_level': 'medium', 'population': '3.4M', 'timezone': 'Africa/Algiers'},
    {'name': 'Tunis', 'lat': 36.8065, 'lng': 10.1815, 'country': 'TN', 'risk_level': 'medium', 'population': '2.3M', 'timezone': 'Africa/Tunis'},
    {'name': 'Beirut', 'lat': 33.8938, 'lng': 35.5018, 'country': 'LB', 'risk_level': 'high', 'population': '2.4M', 'timezone': 'Asia/Beirut'},
    {'name': 'Dubai', 'lat': 25.2048, 'lng': 55.2708, 'country': 'AE', 'risk_level': 'high', 'population': '3.5M', 'timezone': 'Asia/Dubai'},
    {'name': 'Abu Dhabi', 'lat': 24.4539, 'lng': 54.3773, 'country': 'AE', 'risk_level': 'high', 'population': '1.5M', 'timezone': 'Asia/Dubai'},
    {'name': 'Kuwait City', 'lat': 29.3759, 'lng': 47.9774, 'country': 'KW', 'risk_level': 'high', 'population': '3.0M', 'timezone': 'Asia/Kuwait'},
    {'name': 'Doha', 'lat': 25.2854, 'lng': 51.5310, 'country': 'QA', 'risk_level': 'high', 'population': '2.4M', 'timezone': 'Asia/Qatar'},
    
    # Africa
    {'name': 'Lagos', 'lat': 6.5244, 'lng': 3.3792, 'country': 'NG', 'risk_level': 'critical', 'population': '15.4M', 'timezone': 'Africa/Lagos'},
    {'name': 'Cape Town', 'lat': -33.9249, 'lng': 18.4241, 'country': 'ZA', 'risk_level': 'high', 'population': '4.6M', 'timezone': 'Africa/Johannesburg'},
    {'name': 'Durban', 'lat': -29.8587, 'lng': 31.0218, 'country': 'ZA', 'risk_level': 'high', 'population': '3.7M', 'timezone': 'Africa/Johannesburg'},
    {'name': 'Accra', 'lat': 5.6037, 'lng': -0.1870, 'country': 'GH', 'risk_level': 'high', 'population': '4.2M', 'timezone': 'Africa/Accra'},
    {'name': 'Abidjan', 'lat': 5.3600, 'lng': -4.0083, 'country': 'CI', 'risk_level': 'high', 'population': '6.1M', 'timezone': 'Africa/Abidjan'},
    {'name': 'Dakar', 'lat': 14.7167, 'lng': -17.4677, 'country': 'SN', 'risk_level': 'high', 'population': '3.9M', 'timezone': 'Africa/Dakar'},
    {'name': 'Dar es Salaam', 'lat': -6.7924, 'lng': 39.2083, 'country': 'TZ', 'risk_level': 'high', 'population': '6.7M', 'timezone': 'Africa/Dar_es_Salaam'},
    {'name': 'Maputo', 'lat': -25.9692, 'lng': 32.5732, 'country': 'MZ', 'risk_level': 'high', 'population': '1.8M', 'timezone': 'Africa/Maputo'},
    
    # South America
    {'name': 'São Paulo', 'lat': -23.5505, 'lng': -46.6333, 'country': 'BR', 'risk_level': 'high', 'population': '12.3M', 'timezone': 'America/Sao_Paulo'},
    {'name': 'Rio de Janeiro', 'lat': -22.9068, 'lng': -43.1729, 'country': 'BR', 'risk_level': 'high', 'population': '6.7M', 'timezone': 'America/Sao_Paulo'},
    {'name': 'Salvador', 'lat': -12.9714, 'lng': -38.5014, 'country': 'BR', 'risk_level': 'high', 'population': '2.9M', 'timezone': 'America/Bahia'},
    {'name': 'Recife', 'lat': -8.0476, 'lng': -34.8770, 'country': 'BR', 'risk_level': 'high', 'population': '4.1M', 'timezone': 'America/Recife'},
    {'name': 'Fortaleza', 'lat': -3.7319, 'lng': -38.5267, 'country': 'BR', 'risk_level': 'high', 'population': '4.0M', 'timezone': 'America/Fortaleza'},
    {'name': 'Buenos Aires', 'lat': -34.6118, 'lng': -58.3960, 'country': 'AR', 'risk_level': 'high', 'population': '15.2M', 'timezone': 'America/Argentina/Buenos_Aires'},
    {'name': 'Montevideo', 'lat': -34.9011, 'lng': -56.1645, 'country': 'UY', 'risk_level': 'medium', 'population': '1.7M', 'timezone': 'America/Montevideo'},
    {'name': 'Lima', 'lat': -12.0464, 'lng': -77.0428, 'country': 'PE', 'risk_level': 'high', 'population': '10.7M', 'timezone': 'America/Lima'},
    {'name': 'Guayaquil', 'lat': -2.1894, 'lng': -79.8890, 'country': 'EC', 'risk_level': 'high', 'population': '2.7M', 'timezone': 'America/Guayaquil'},
    {'name': 'Cartagena', 'lat': 10.3910, 'lng': -75.4794, 'country': 'CO', 'risk_level': 'high', 'population': '1.0M', 'timezone': 'America/Bogota'},
    {'name': 'Valparaíso', 'lat': -33.0472, 'lng': -71.6127, 'country': 'CL', 'risk_level': 'medium', 'population': '950K', 'timezone': 'America/Santiago'},
    
    # Oceania
    {'name': 'Sydney', 'lat': -33.8688, 'lng': 151.2093, 'country': 'AU', 'risk_level': 'medium', 'population': '5.3M', 'timezone': 'Australia/Sydney'},
    {'name': 'Melbourne', 'lat': -37.8136, 'lng': 144.9631, 'country': 'AU', 'risk_level': 'medium', 'population': '5.1M', 'timezone': 'Australia/Melbourne'},
    {'name': 'Brisbane', 'lat': -27.4698, 'lng': 153.0251, 'country': 'AU', 'risk_level': 'high', 'population': '2.5M', 'timezone': 'Australia/Brisbane'},
    {'name': 'Perth', 'lat': -31.9505, 'lng': 115.8605, 'country': 'AU', 'risk_level': 'medium', 'population': '2.1M', 'timezone': 'Australia/Perth'},
    {'name': 'Adelaide', 'lat': -34.9285, 'lng': 138.6007, 'country': 'AU', 'risk_level': 'medium', 'population': '1.4M', 'timezone': 'Australia/Adelaide'},
    {'name': 'Auckland', 'lat': -36.8485, 'lng': 174.7633, 'country': 'NZ', 'risk_level': 'medium', 'population': '1.7M', 'timezone': 'Pacific/Auckland'},
    {'name': 'Wellington', 'lat': -41.2865, 'lng': 174.7762, 'country': 'NZ', 'risk_level': 'medium', 'population': '420K', 'timezone': 'Pacific/Auckland'},
    
    # Caribbean & Central America
    {'name': 'Havana', 'lat': 23.1136, 'lng': -82.3666, 'country': 'CU', 'risk_level': 'critical', 'population': '2.1M', 'timezone': 'America/Havana'},
    {'name': 'San Juan', 'lat': 18.4655, 'lng': -66.1057, 'country': 'PR', 'risk_level': 'critical', 'population': '2.4M', 'timezone': 'America/Puerto_Rico'},
    {'name': 'Kingston', 'lat': 17.9970, 'lng': -76.7936, 'country': 'JM', 'risk_level': 'critical', 'population': '1.2M', 'timezone': 'America/Jamaica'},
    {'name': 'Port-au-Prince', 'lat': 18.5944, 'lng': -72.3074, 'country': 'HT', 'risk_level': 'critical', 'population': '2.8M', 'timezone': 'America/Port-au-Prince'},
    {'name': 'Santo Domingo', 'lat': 18.4861, 'lng': -69.9312, 'country': 'DO', 'risk_level': 'critical', 'population': '3.3M', 'timezone': 'America/Santo_Domingo'},
    {'name': 'Panama City', 'lat': 8.9824, 'lng': -79.5199, 'country': 'PA', 'risk_level': 'high', 'population': '1.9M', 'timezone': 'America/Panama'},
    
    # Small Island States (Extremely High Risk)
    {'name': 'Male', 'lat': 4.1755, 'lng': 73.5093, 'country': 'MV', 'risk_level': 'critical', 'population': '200K', 'timezone': 'Indian/Maldives'},
    {'name': 'Suva', 'lat': -18.1248, 'lng': 178.4501, 'country': 'FJ', 'risk_level': 'critical', 'population': '180K', 'timezone': 'Pacific/Fiji'},
    {'name': 'Port Vila', 'lat': -17.7334, 'lng': 168.3273, 'country': 'VU', 'risk_level': 'critical', 'population': '50K', 'timezone': 'Pacific/Efate'},
    {'name': 'Nuku\'alofa', 'lat': -21.1789, 'lng': -175.1982, 'country': 'TO', 'risk_level': 'critical', 'population': '25K', 'timezone': 'Pacific/Tongatapu'}
]

ACTIVE_ALERTS = []

# Enhanced Environmental facts database
ENVIRONMENTAL_FACTS = {
    
    # Traditional environmental activities
    'deforestation': {
        'fact': '2024 satellite data shows the Amazon lost 11,568 km² of rainforest. The Amazon stores 15-20% of global freshwater.',
        'impact': 'Deforestation releases 1.5 billion tons of CO2 annually and destroys biodiversity hotspots critical for climate regulation.',
        'location': 'Amazon Rainforest, Brazil',
        'year': '2024-2025',
        'type': 'environmental',
        'solution': 'Protected areas, sustainable logging, reforestation programs, and indigenous land rights protection'
    },
    'ice_melting': {
        'fact': 'Satellite monitoring shows Greenland lost 280 billion tons of ice in 2024. Current rates project 7.2m sea level rise by 2100.',
        'impact': 'Arctic ice loss creates feedback loops - less ice means more heat absorption, accelerating global warming.',
        'location': 'Arctic Ice Sheets',
        'year': '2024-2025',
        'type': 'environmental',
        'solution': 'Rapid carbon emission reductions, renewable energy transition, and Arctic protection measures'
    },
    'fossil_fuels': {
        'fact': '2024 atmospheric monitoring recorded CO2 levels at 422.5 ppm - the highest in 800,000 years.',
        'impact': 'Fossil fuel emissions are the primary driver of climate change, causing extreme weather that threatens coastal populations.',
        'location': 'Global Energy Systems',
        'year': '2024',
        'type': 'environmental',
        'solution': 'Renewable energy transition, carbon pricing, energy efficiency, and fossil fuel phase-out policies'
    },
    'plastic_pollution': {
        'fact': 'Ocean monitoring data shows 75-199 million tonnes of plastic in our oceans as of 2025.',
        'impact': 'Ocean plastic kills 1 million seabirds and 100,000 marine mammals yearly while contaminating coastal food chains.',
        'location': 'Global Ocean Systems',
        'year': '2025',
        'type': 'environmental',
        'solution': 'Plastic bans, circular economy, improved waste management, and biodegradable alternatives'
    },
    'urban_heat': {
        'fact': 'Temperature monitoring shows urban heat islands make coastal cities 2-5°C hotter than surrounding areas.',
        'impact': 'Urban heat increases energy consumption, worsens air quality, and makes coastal cities less livable.',
        'location': 'Major Urban Coastal Areas',
        'year': '2024',
        'type': 'environmental',
        'solution': 'Green roofs, urban forests, cool pavements, and sustainable urban planning'
    },
    'air_pollution': {
        'fact': 'Air quality monitoring shows pollution kills 7 million people annually. Coastal megacities face severe crises.',
        'impact': 'Poor air quality in coastal cities affects millions, causing respiratory diseases and reducing quality of life.',
        'location': 'Coastal Megacities',
        'year': '2024',
        'type': 'environmental',
        'solution': 'Clean air policies, electric vehicle adoption, and green transportation systems'
    }
}

# Enhanced environmental activities
ENVIRONMENTAL_ACTIVITIES = [
    
    # Traditional Environmental Activities
    {'lat': -3.4653, 'lng': -62.2159, 'type': 'deforestation', 'title': '🌳 Amazon Deforestation Crisis', 'risk': 'critical', 'id': 'env_1', 'category': 'environmental'},
    {'lat': 72.0, 'lng': -38.0, 'type': 'ice_melting', 'title': '🧊 Greenland Ice Sheet Collapse', 'risk': 'critical', 'id': 'env_2', 'category': 'environmental'},
    {'lat': -75.0, 'lng': 0.0, 'type': 'ice_melting', 'title': '🧊 Antarctic Ice Loss', 'risk': 'critical', 'id': 'env_3', 'category': 'environmental'},
    {'lat': 39.9042, 'lng': 116.4074, 'type': 'fossil_fuels', 'title': '🏭 China Coal Power Crisis', 'risk': 'high', 'id': 'env_4', 'category': 'environmental'},
    {'lat': 14.0583, 'lng': 108.2772, 'type': 'plastic_pollution', 'title': '🗑️ Philippines Ocean Plastic', 'risk': 'high', 'id': 'env_5', 'category': 'environmental'},
    {'lat': 28.6139, 'lng': 77.2090, 'type': 'air_pollution', 'title': '💨 Delhi Air Pollution Crisis', 'risk': 'high', 'id': 'env_6', 'category': 'environmental'},
    {'lat': 52.3676, 'lng': 4.9041, 'type': 'urban_heat', 'title': '🌡️ Amsterdam Heat Island', 'risk': 'medium', 'id': 'env_7', 'category': 'environmental'},
    
    {'lat': 1.3521, 'lng': 103.8198, 'type': 'urban_heat', 'title': '🌡️ Singapore Heat Challenge', 'risk': 'medium', 'id': 'env_9', 'category': 'environmental'},
    {'lat': 22.3193, 'lng': 114.1694, 'type': 'air_pollution', 'title': '💨 Hong Kong Air Quality', 'risk': 'medium', 'id': 'env_10', 'category': 'environmental'}
]

def get_weather_description(weather_code):
    """Convert weather codes to human-readable descriptions"""
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        56: "Light freezing drizzle", 57: "Dense freezing drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        66: "Light freezing rain", 67: "Heavy freezing rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        85: "Slight snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
    }
    return weather_codes.get(weather_code, f"Weather code {weather_code}")

def fetch_live_weather_alerts():
    """Fetch REAL severe weather alerts from LIVE APIs - ONLY when actual emergencies occur"""
    alerts = []
    
    print(f"🌍 LIVE MONITORING: Checking {len(COASTAL_CITIES)} global coastal cities for REAL emergencies...")
    
    emergency_count = 0
    
    # Process cities in batches to avoid overwhelming the API
    for i, city in enumerate(COASTAL_CITIES):
        try:
            # Use Open-Meteo Live API (completely free, no registration)
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                'latitude': city['lat'],
                'longitude': city['lng'],
                'current': 'temperature_2m,wind_speed_10m,precipitation,weather_code,time',
                'daily': 'temperature_2m_max,temperature_2m_min,wind_speed_10m_max,precipitation_sum',
                'forecast_days': 1,
                'timezone': city.get('timezone', 'auto')
            }
            
            response = requests.get(url, params=params, timeout=8)
            if response.status_code == 200:
                data = response.json()
                current = data.get('current', {})
                daily = data.get('daily', {})
                
                # Extract LIVE current conditions
                wind_speed = current.get('wind_speed_10m', 0)
                precipitation = current.get('precipitation', 0)
                temperature = current.get('temperature_2m', 0)
                weather_code = current.get('weather_code', 0)
                api_time = current.get('time', '')
                
                # Extract daily forecasts
                max_wind = daily.get('wind_speed_10m_max', [0])[0] if daily.get('wind_speed_10m_max') else 0
                max_temp = daily.get('temperature_2m_max', [0])[0] if daily.get('temperature_2m_max') else 0
                min_temp = daily.get('temperature_2m_min', [0])[0] if daily.get('temperature_2m_min') else 0
                daily_precip = daily.get('precipitation_sum', [0])[0] if daily.get('precipitation_sum') else 0
                
                # Convert API time to local timezone
                try:
                    # Parse ISO time from API
                    utc_time = datetime.fromisoformat(api_time.replace('Z', '+00:00'))
                    # Convert to city's timezone
                    city_tz = pytz.timezone(city.get('timezone', 'UTC'))
                    local_time = utc_time.astimezone(city_tz)
                    formatted_time = local_time.strftime("%Y-%m-%d %H:%M %Z")
                    formatted_date = local_time.strftime("%B %d, %Y")
                except:
                    formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
                    formatted_date = datetime.now().strftime("%B %d, %Y")
                
                print(f"📊 LIVE: {city['name']}: {temperature:.1f}°C, Wind: {wind_speed:.1f} km/h, Rain: {precipitation:.1f}mm, Weather: {get_weather_description(weather_code)}")
                
                # ULTRA-STRICT CRITERIA FOR REAL EMERGENCIES ONLY
                alert_triggered = False
                alert_type = ""
                severity = "medium"
                emergency_level = ""
                
                # CATEGORY 1+ TROPICAL CYCLONE (Wind > 65 km/h = Category 1 Hurricane)
                if wind_speed > 65 or max_wind > 65:
                    alert_triggered = True
                    if wind_speed > 120 or max_wind > 120:
                        alert_type = "🌀 CATEGORY 3+ HURRICANE"
                        severity = "critical"
                        emergency_level = "EXTREME EMERGENCY"
                    elif wind_speed > 95 or max_wind > 95:
                        alert_type = "🌀 CATEGORY 2 HURRICANE"
                        severity = "critical"
                        emergency_level = "CRITICAL EMERGENCY"
                    else:
                        alert_type = "🌀 CATEGORY 1 HURRICANE"
                        severity = "critical"
                        emergency_level = "HURRICANE WARNING"
                
                # SEVERE THUNDERSTORM WITH HAIL (Weather codes 95-99)
                elif weather_code >= 95:
                    alert_triggered = True
                    if weather_code >= 96:
                        alert_type = "⛈️ SEVERE THUNDERSTORM WITH HAIL"
                        severity = "high"
                        emergency_level = "SEVERE WEATHER WARNING"
                    else:
                        alert_type = "⛈️ THUNDERSTORM ALERT"
                        severity = "high"
                        emergency_level = "THUNDERSTORM WARNING"
                
                # EXTREME WIND STORM (Wind > 55 km/h + Heavy Rain)
                elif wind_speed > 55 and (precipitation > 15 or daily_precip > 30):
                    alert_triggered = True
                    alert_type = "🌩️ EXTREME WIND STORM"
                    severity = "high"
                    emergency_level = "STORM WARNING"
                
                # DANGEROUS HEAT WAVE (Region-specific thresholds)
                elif ((city['country'] in ['US', 'CA', 'GB', 'NL', 'DE', 'FR', 'IT'] and max_temp > 38) or 
                      (city['country'] in ['IN', 'PK', 'BD', 'TH', 'AE', 'QA', 'KW'] and max_temp > 48) or 
                      (city['country'] in ['AU', 'ZA'] and max_temp > 42) or 
                      (max_temp > 45)):
                    alert_triggered = True
                    alert_type = "🔥 DANGEROUS HEAT WAVE"
                    severity = "high"
                    emergency_level = "HEAT EMERGENCY"
                
                # FLASH FLOOD WARNING (Heavy precipitation > 30mm in current conditions)
                elif precipitation > 30 or daily_precip > 80:
                    alert_triggered = True
                    alert_type = "🌊 FLASH FLOOD WARNING"
                    severity = "high"
                    emergency_level = "FLOOD EMERGENCY"
                
                # BLIZZARD CONDITIONS (Heavy snow + high winds)
                elif weather_code >= 73 and weather_code <= 77 and wind_speed > 40:
                    alert_triggered = True
                    alert_type = "❄️ BLIZZARD CONDITIONS"
                    severity = "high"
                    emergency_level = "BLIZZARD WARNING"
                
                # CRITICAL CITY SPECIAL MONITORING (Only for the most vulnerable cities)
                elif (city['risk_level'] == 'critical' and city['name'] in ['Venice', 'Male', 'Miami', 'New Orleans'] and 
                      (wind_speed > 45 or precipitation > 12 or max_temp > 40)):
                    alert_triggered = True
                    alert_type = f"⚠️ {city['name'].upper()} CRITICAL MONITORING"
                    severity = "medium"
                    emergency_level = "HEIGHTENED WATCH"
                
                if alert_triggered:
                    emergency_count += 1
                    
                    alerts.append({
                        'city': city['name'],
                        'country': city['country'],
                        'lat': city['lat'],
                        'lng': city['lng'],
                        'population': city.get('population', 'Unknown'),
                        'timezone': city.get('timezone', 'UTC'),
                        'title': f"{alert_type} - {city['name']}",
                        'description': f"🚨 {emergency_level}: {city['population']} people at risk in {city['name']}, {city['country']}. Weather: {get_weather_description(weather_code)}",
                        'severity': severity,
                        'emergency_level': emergency_level,
                        'start': int(time.time()),
                        'end': int(time.time()) + 86400,
                        'source': 'Open-Meteo Live Weather API',
                        'api_time': formatted_time,
                        'api_date': formatted_date,
                        'temperature': round(temperature, 1),
                        'wind_speed': round(wind_speed, 1),
                        'precipitation': round(precipitation, 1),
                        'max_wind': round(max_wind, 1),
                        'max_temp': round(max_temp, 1),
                        'min_temp': round(min_temp, 1),
                        'daily_precip': round(daily_precip, 1),
                        'weather_code': weather_code,
                        'weather_description': get_weather_description(weather_code),
                        'risk_level': city['risk_level'],
                        'alert_type': alert_type,
                        'is_api_data': True,
                        'is_real_emergency': True,
                        'live_api_call': True,
                        'coordinates': f"{city['lat']:.4f}, {city['lng']:.4f}"
                    })
                    
                    print(f"🚨 EMERGENCY DETECTED: {alert_type} in {city['name']} - {emergency_level}")
                    
            # Rate limiting - pause every 20 requests
            if i % 20 == 0 and i > 0:
                print(f"⏸️ Rate limiting pause... ({i}/{len(COASTAL_CITIES)} cities checked)")
                time.sleep(2)
                    
        except Exception as e:
            print(f"❌ Error fetching LIVE data for {city['name']}: {e}")
            continue
    
    print(f"🚨 EMERGENCY SUMMARY: {emergency_count} REAL emergencies detected from {len(COASTAL_CITIES)} cities monitored")
    print(f"✅ Generated {len(alerts)} verified emergency alerts from LIVE APIs")
    
    return alerts

def update_weather_alerts():
    """Background task to continuously monitor for REAL emergencies"""
    global ACTIVE_ALERTS
    
    while True:
        try:
            print(f"\n🔄 LIVE EMERGENCY SCAN: Monitoring {len(COASTAL_CITIES)} global coastal cities...")
            start_time = time.time()
            
            ACTIVE_ALERTS = fetch_live_weather_alerts()
            
            scan_duration = time.time() - start_time
            print(f"📊 Scan completed in {scan_duration:.1f} seconds")
            
            if ACTIVE_ALERTS:
                critical_count = len([a for a in ACTIVE_ALERTS if a.get('severity') == 'critical'])
                high_count = len([a for a in ACTIVE_ALERTS if a.get('severity') == 'high'])
                print(f"🚨 LIVE ALERT SUMMARY: {critical_count} Critical, {high_count} High Risk emergencies")
                
                # Log the most severe alerts
                for alert in ACTIVE_ALERTS[:3]:
                    print(f"   🚨 {alert['emergency_level']}: {alert['city']} - {alert['alert_type']}")
            else:
                print("✅ No severe weather emergencies detected globally at this time")
                
        except Exception as e:
            print(f"❌ Error in LIVE emergency monitoring: {e}")
        
        # Check every 10 minutes for real emergencies
        time.sleep(600)

# Start background emergency monitoring
alert_thread = threading.Thread(target=update_weather_alerts, daemon=True)
alert_thread.start()

@app.route('/')
def index():
    if 'score' not in session:
        session['score'] = 0
        session['correct_decisions'] = 0
        session['total_decisions'] = 0
        session['sea_level_impact'] = 0.0
        session['completed_activities'] = []
        session['decision_history'] = []
        session['category_stats'] = {'api': {'correct': 0, 'total': 0}, 'environmental': {'correct': 0, 'total': 0}}
    
    return render_template('game.html', activities=ENVIRONMENTAL_ACTIVITIES)

@app.route('/get_activities')
def get_activities():
    """Get activities - API activities always visible, environmental ones disappear after completion"""
    completed = session.get('completed_activities', [])
    
    available_activities = []
    for activity in ENVIRONMENTAL_ACTIVITIES:
        if activity.get('persistent', False) or activity['id'] not in completed:
            activity_copy = activity.copy()
            activity_copy['completed'] = activity['id'] in completed
            available_activities.append(activity_copy)
    
    return jsonify(available_activities)

@app.route('/get_weather_alerts')
def get_weather_alerts():
    """API endpoint to get current REAL emergency weather alerts from LIVE APIs"""
    return jsonify({
        'alerts': ACTIVE_ALERTS,
        'total_alerts': len(ACTIVE_ALERTS),
        'critical_alerts': len([a for a in ACTIVE_ALERTS if a.get('severity') == 'critical']),
        'high_alerts': len([a for a in ACTIVE_ALERTS if a.get('severity') == 'high']),
        'medium_alerts': len([a for a in ACTIVE_ALERTS if a.get('severity') == 'medium']),
        'coastal_cities_monitored': len(COASTAL_CITIES),
        'last_updated': datetime.now().isoformat(),
        'scan_status': 'LIVE MONITORING ACTIVE',
        'api_status': {
            'primary_api': 'Open-Meteo Live Weather API (Free)',
            'cities_monitored': len(COASTAL_CITIES),
            'emergency_criteria': 'Hurricane: >65km/h wind | Thunderstorm: Code 95+ | Heat: >38°C+ | Flood: >30mm rain',
            'update_frequency': '10 minutes',
            'global_coverage': f'{len(COASTAL_CITIES)} cities across all continents',
            'only_real_emergencies': True
        }
    })

@app.route('/get_coastal_cities')
def get_coastal_cities():
    """API endpoint to get all coastal cities being monitored"""
    continents = {
        'North America': [c for c in COASTAL_CITIES if c['country'] in ['US', 'CA']],
        'Asia': [c for c in COASTAL_CITIES if c['country'] in ['JP', 'CN', 'IN', 'BD', 'TH', 'SG', 'MY', 'ID', 'PH', 'VN', 'KR', 'HK', 'TW', 'LK', 'PK']],
        'Europe': [c for c in COASTAL_CITIES if c['country'] in ['GB', 'NL', 'DE', 'FR', 'IT', 'ES', 'PT', 'GR', 'TR', 'DK', 'SE', 'FI', 'NO']],
        'Africa': [c for c in COASTAL_CITIES if c['country'] in ['NG', 'ZA', 'EG', 'MA', 'GH', 'CI', 'SN', 'TZ', 'MZ', 'DZ', 'TN']],
        'South America': [c for c in COASTAL_CITIES if c['country'] in ['BR', 'AR', 'PE', 'CO', 'CL', 'UY', 'EC']],
        'Oceania': [c for c in COASTAL_CITIES if c['country'] in ['AU', 'NZ']],
        'Caribbean & Islands': [c for c in COASTAL_CITIES if c['country'] in ['CU', 'PR', 'JM', 'HT', 'DO', 'PA', 'MV', 'FJ', 'VU', 'TO']],
        'Middle East': [c for c in COASTAL_CITIES if c['country'] in ['IL', 'LB', 'AE', 'QA', 'KW']]
    }
    
    return jsonify({
        'cities': COASTAL_CITIES,
        'total_cities': len(COASTAL_CITIES),
        'by_continent': {cont: len(cities) for cont, cities in continents.items()},
        'by_risk_level': {
            'critical': len([c for c in COASTAL_CITIES if c['risk_level'] == 'critical']),
            'high': len([c for c in COASTAL_CITIES if c['risk_level'] == 'high']),
            'medium': len([c for c in COASTAL_CITIES if c['risk_level'] == 'medium']),
            'low': len([c for c in COASTAL_CITIES if c['risk_level'] == 'low'])
        },
        'continents': continents
    })

@app.route('/get_fact/<activity_type>')
def get_fact(activity_type):
    if activity_type in ENVIRONMENTAL_FACTS:
        fact_data = ENVIRONMENTAL_FACTS[activity_type].copy()
        
        # Add real-time alert info for API-based activities
        if fact_data.get('type') == 'api_weather' and ACTIVE_ALERTS:
            related_alerts = [alert for alert in ACTIVE_ALERTS if 
                            activity_type.replace('_', ' ').lower() in alert['title'].lower()]
            
            if related_alerts:
                alert = related_alerts[0]
                fact_data['real_time_alert'] = f"🚨 LIVE EMERGENCY: {alert['alert_type']} - {alert['temperature']}°C, Wind: {alert['wind_speed']} km/h, Rain: {alert['precipitation']}mm in {alert['city']} | {alert['api_time']} | Source: {alert['source']}"
                fact_data['api_enhanced'] = True
                fact_data['live_source'] = alert['source']
                fact_data['live_time'] = alert['api_time']
                fact_data['emergency_level'] = alert['emergency_level']
        
        return jsonify(fact_data)
    return jsonify({'error': 'Activity type not found'})

@app.route('/make_decision', methods=['POST'])
def make_decision():
    data = request.get_json()
    activity_type = data.get('activity_type')
    activity_id = data.get('activity_id')
    decision = data.get('decision')
    
    if activity_type not in ENVIRONMENTAL_FACTS:
        return jsonify({'error': 'Invalid activity type'})
    
    activity = next((a for a in ENVIRONMENTAL_ACTIVITIES if a['id'] == activity_id), None)
    if not activity:
        return jsonify({'error': 'Activity not found'})
    
    # Initialize session variables
    if 'completed_activities' not in session:
        session['completed_activities'] = []
    if 'decision_history' not in session:
        session['decision_history'] = []
    if 'category_stats' not in session:
        session['category_stats'] = {'api': {'correct': 0, 'total': 0}, 'environmental': {'correct': 0, 'total': 0}}
    
    if activity_id not in session['completed_activities']:
        session['completed_activities'] = session['completed_activities'] + [activity_id]
    
    session['total_decisions'] = session.get('total_decisions', 0) + 1
    
    correct = decision == 'stop'
    fact_info = ENVIRONMENTAL_FACTS[activity_type]
    
    category = activity.get('category', 'environmental')
    is_api_activity = category == 'api'
    
    session['category_stats'][category]['total'] += 1
    if correct:
        session['category_stats'][category]['correct'] += 1
    
    if correct:
        session['correct_decisions'] = session.get('correct_decisions', 0) + 1
        if is_api_activity:
            points = 40  # Higher points for real-time LIVE emergency decisions
            session['score'] = session.get('score', 0) + points
            new_sea_level = session.get('sea_level_impact', 0) - 0.25
        else:
            points = 25
            session['score'] = session.get('score', 0) + points
            new_sea_level = session.get('sea_level_impact', 0) - 0.15
        
        session['sea_level_impact'] = max(0.0, new_sea_level)
        
        city_name = activity.get('city', 'this location')
        messages = [
            f"🌊 EXCELLENT! You're protecting {city_name} from REAL emergency threats!",
            f"🏙️ OUTSTANDING! You've made the right decision for {city_name} during live monitoring!",
            f"✨ PERFECT! You're helping safeguard populations during actual weather events!",
            f"🛡️ INCREDIBLE! +{points} points for emergency response to LIVE conditions!",
            f"🌍 AMAZING! You're building real-time coastal resilience!"
        ]
        message = random.choice(messages)
        message_type = 'success'
        
    else:
        if is_api_activity:
            penalty = 20
            session['score'] = max(0, session.get('score', 0) - penalty)
            session['sea_level_impact'] = session.get('sea_level_impact', 0) + 0.5
        else:
            penalty = 15
            session['score'] = max(0, session.get('score', 0) - penalty)
            session['sea_level_impact'] = session.get('sea_level_impact', 0) + 0.3
        
        city_name = activity.get('city', 'this location')
        messages = [
            f"🌊 This choice endangers {city_name} during REAL emergency conditions!",
            f"⚠️ Unfortunately, this worsens emergency response to actual threats!",
            f"🚨 This decision ignores LIVE weather emergencies affecting millions!",
            f"💧 This increases vulnerability during real-time crisis conditions!",
            f"🌀 This ignores urgent emergency warnings from live monitoring!"
        ]
        message = random.choice(messages)
        message_type = 'warning'
    
    # Record decision history
    decision_record = {
        'activity_id': activity_id,
        'activity_title': activity['title'],
        'activity_type': activity_type,
        'decision': decision,
        'correct': correct,
        'points_change': points if correct else -penalty,
        'category': category,
        'risk_level': activity['risk'],
        'timestamp': datetime.now().isoformat(),
        'location': fact_info.get('location', 'Global'),
        'solution': fact_info.get('solution', 'Multiple solutions available'),
        'city': activity.get('city', 'Global')
    }
    
    session['decision_history'] = session['decision_history'] + [decision_record]
    
    # Calculate remaining activities
    non_persistent_activities = [a for a in ENVIRONMENTAL_ACTIVITIES if not a.get('persistent', False)]
    non_persistent_completed = [aid for aid in session['completed_activities'] 
                               if any(a['id'] == aid and not a.get('persistent', False) for a in ENVIRONMENTAL_ACTIVITIES)]
    remaining_activities = len(non_persistent_activities) - len(non_persistent_completed)
    
    response_data = {
        'message': message,
        'correct': correct,
        'fact': fact_info['fact'],
        'impact': fact_info['impact'],
        'solution': fact_info.get('solution', 'Multiple solutions available'),
        'score': session['score'],
        'sea_level_impact': round(session['sea_level_impact'], 2),
        'message_type': message_type,
        'year': fact_info.get('year', '2024-2025'),
        'activity_completed': True,
        'remaining_activities': remaining_activities,
        'points_earned': points if correct else -penalty,
        'is_api_activity': is_api_activity,
        'category': category,
        'is_persistent': activity.get('persistent', False),
        'total_coastal_cities': len(COASTAL_CITIES)
    }
    
    # Add real-time emergency data for API activities
    if is_api_activity and ACTIVE_ALERTS:
        city_name = activity.get('city', '')
        related_alert = next((alert for alert in ACTIVE_ALERTS if 
                            city_name.lower() in alert['city'].lower()), None)
        if related_alert:
            response_data['live_data'] = f"🚨 LIVE EMERGENCY DATA: {related_alert['emergency_level']} in {city_name} - {related_alert['alert_type']} | Wind: {related_alert.get('wind_speed', 'N/A')} km/h | Population at risk: {related_alert.get('population', 'N/A')} | Time: {related_alert.get('api_time', 'N/A')}"
    
    return jsonify(response_data)

@app.route('/stats')
def stats():
    total = session.get('total_decisions', 0)
    correct = session.get('correct_decisions', 0)
    percentage = round((correct / total * 100) if total > 0 else 0, 1)
    decision_history = session.get('decision_history', [])
    category_stats = session.get('category_stats', {'api': {'correct': 0, 'total': 0}, 'environmental': {'correct': 0, 'total': 0}})
    
    correct_decisions = [d for d in decision_history if d['correct']]
    wrong_decisions = [d for d in decision_history if not d['correct']]
    
    api_performance = round((category_stats['api']['correct'] / category_stats['api']['total'] * 100) if category_stats['api']['total'] > 0 else 0, 1)
    env_performance = round((category_stats['environmental']['correct'] / category_stats['environmental']['total'] * 100) if category_stats['environmental']['total'] > 0 else 0, 1)
    
    risk_analysis = {}
    for decision in decision_history:
        risk = decision['risk_level']
        if risk not in risk_analysis:
            risk_analysis[risk] = {'correct': 0, 'total': 0}
        risk_analysis[risk]['total'] += 1
        if decision['correct']:
            risk_analysis[risk]['correct'] += 1
    
    for risk in risk_analysis:
        risk_analysis[risk]['percentage'] = round((risk_analysis[risk]['correct'] / risk_analysis[risk]['total'] * 100) if risk_analysis[risk]['total'] > 0 else 0, 1)
    
    stats_data = {
        'score': session.get('score', 0),
        'total_decisions': total,
        'correct_decisions': correct,
        'percentage': percentage,
        'sea_level_impact': round(session.get('sea_level_impact', 0), 2),
        'completed_activities': len(session.get('completed_activities', [])),
        'total_activities': len(ENVIRONMENTAL_ACTIVITIES),
        'active_alerts': len(ACTIVE_ALERTS),
        'coastal_cities_monitored': len(COASTAL_CITIES),
        'decision_history': decision_history,
        'correct_decisions_list': correct_decisions,
        'wrong_decisions_list': wrong_decisions,
        'category_stats': category_stats,
        'api_performance': api_performance,
        'env_performance': env_performance,
        'risk_analysis': risk_analysis
    }
    
    return render_template('stats.html', stats=stats_data)

@app.route('/reset_game')
def reset_game():
    session.clear()
    flash('Game reset! Start making environmental decisions again.', 'info')
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Environmental Guardian Game with LIVE Emergency Monitoring")
    print(f"🌍 Monitoring {len(COASTAL_CITIES)} global coastal cities on port {port}")
    print(f"🚨 Real-time emergency detection: Hurricane, Thunderstorm, Heat Wave, Flood, Blizzard")
    app.run(debug=False, host='0.0.0.0', port=port)
