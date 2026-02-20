"""
Real-Time Situational Awareness System - Web UI
Flask-based web interface for monitoring aircraft, satellites, and traffic cameras
with collision detection and real-time updates.
"""

from flask import Flask, render_template, jsonify, Response
import threading
import time
import json
import requests
import pandas as pd
import numpy as np
from skyfield.api import load, EarthSatellite, wgs84
import cv2
import torch
from transformers import AutoImageProcessor, Mask2FormerForUniversalSegmentation
from PIL import Image
import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
from shapely.geometry import Point
from scipy.spatial import KDTree
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime

app = Flask(__name__)

# Global config
BOUNDING_BOX = {'min_lat': 27.0, 'min_lon': 76.0, 'max_lat': 29.0, 'max_lon': 78.0}
UPDATE_INTERVAL_SEC = 30
SATELLITE_CATALOG_NUMBERS = [25544, 48274]

# Real Public Camera Streams - Using reliable sources accessible in most networks
# Mix of test streams and public cameras
TRAFFIC_CAM_STREAMS = [
    # Reliable Test Stream - Big Buck Bunny
    {'id': 0, 'url': 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4', 
     'location': 'Demo Test Stream 1', 'lat': 28.14, 'lon': 77.32},
    
    # Sample Video 2
    {'id': 1, 'url': 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4', 
     'location': 'Demo Test Stream 2', 'lat': 35.6595, 'lon': 139.7004},
    
    # Sample Video 3
    {'id': 2, 'url': 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4', 
     'location': 'Demo Test Stream 3', 'lat': 47.3769, 'lon': 8.5417},
    
    # Sample Video 4
    {'id': 3, 'url': 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4', 
     'location': 'Demo Test Stream 4', 'lat': 40.7580, 'lon': -73.9855},
    
    # Sample Video 5
    {'id': 4, 'url': 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4', 
     'location': 'Demo Test Stream 5', 'lat': 51.5319, 'lon': -0.1773},
    
    # Sample Video 6
    {'id': 5, 'url': 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4', 
     'location': 'Demo Test Stream 6', 'lat': 48.8566, 'lon': 2.3522},
]

# TO USE REAL CAMERAS:
# Replace the URLs above with your actual camera streams:
# - IP Cameras: 'rtsp://username:password@camera-ip:554/stream'
# - HTTP MJPEG: 'http://camera-ip/video.mjpg'
# - Check your city's traffic department for official camera feeds
# - Contact NHAI, state PWD, or local traffic police for access

# Collision thresholds (in meters)
PLANE_PLANE_HORIZ_THRESHOLD = 10000
PLANE_PLANE_VERT_THRESHOLD = 1000
SAT_SAT_HORIZ_THRESHOLD = 100000
SAT_SAT_VERT_THRESHOLD = 10000
PLANE_SAT_HORIZ_THRESHOLD = 50000

# Global data store
global_data = {
    'planes': pd.DataFrame(),
    'satellites': pd.DataFrame(),
    'cameras': pd.DataFrame(),
    'alerts': [],
    'last_update': None,
    'map_html': None,
    'weather': {},
    'traffic_info': {},
    'historical_data': {'planes': [], 'satellites': [], 'alerts': []},
    'location_info': {}
}

# Camera stream cache
camera_captures = {}

# Pre-load Mask2Former model
try:
    processor = AutoImageProcessor.from_pretrained("facebook/mask2former-swin-large-ade-panoptic")
    model = Mask2FormerForUniversalSegmentation.from_pretrained("facebook/mask2former-swin-large-ade-panoptic")
except Exception as e:
    print(f"Warning: Could not load Mask2Former model: {e}")
    processor = None
    model = None

def haversine(lon1, lat1, lon2, lat2):
    """Calculate horizontal distance in meters using Haversine formula."""
    R = 6371000
    dlon = radians(lon2 - lon1)
    dlat = radians(lat2 - lat1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

def fetch_weather():
    """Fetch weather data for the monitored area using OpenWeatherMap API."""
    try:
        # Using open-meteo.com (free, no API key required)
        lat, lon = 28.14, 77.32  # Palwal, Haryana
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,weather_code&timezone=Asia/Kolkata"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            current = data.get('current', {})
            weather_codes = {
                0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast',
                45: 'Foggy', 48: 'Foggy', 61: 'Rain', 63: 'Rain', 65: 'Heavy rain',
                71: 'Snow', 73: 'Snow', 75: 'Heavy snow', 95: 'Thunderstorm'
            }
            return {
                'temperature': current.get('temperature_2m', 'N/A'),
                'humidity': current.get('relative_humidity_2m', 'N/A'),
                'wind_speed': current.get('wind_speed_10m', 'N/A'),
                'wind_direction': current.get('wind_direction_10m', 'N/A'),
                'condition': weather_codes.get(current.get('weather_code', 0), 'Unknown'),
                'location': 'Palwal, Haryana'
            }
    except Exception as e:
        print(f"Error fetching weather: {e}")
    return {}

def get_location_info(lat, lon):
    """Get city/location information using reverse geocoding."""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        headers = {'User-Agent': 'SituationalAwarenessSystem/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            return {
                'city': address.get('city') or address.get('town') or address.get('village', 'Unknown'),
                'state': address.get('state', 'Unknown'),
                'country': address.get('country', 'Unknown'),
                'display_name': data.get('display_name', 'Unknown location')
            }
    except Exception as e:
        print(f"Error fetching location info: {e}")
    return {}

def fetch_traffic_info():
    """Get traffic information for the monitored area."""
    try:
        # Simulated traffic data - in production, integrate with real traffic APIs
        return {
            'status': 'moderate',
            'congestion_level': 45,  # 0-100
            'incidents': 2,
            'avg_speed': 42,  # km/h
            'roads_monitored': 15
        }
    except Exception as e:
        print(f"Error fetching traffic info: {e}")
    return {}

def fetch_planes():
    """Fetch live aircraft data via OpenSky Network API."""
    url = f"https://opensky-network.org/api/states/all?lamin={BOUNDING_BOX['min_lat']}&lomin={BOUNDING_BOX['min_lon']}&lamax={BOUNDING_BOX['max_lat']}&lomax={BOUNDING_BOX['max_lon']}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()['states']
            if data:
                selected_data = [[row[0], row[1], row[2], row[5], row[6], row[7], row[9], row[10], row[8]] 
                               for row in data if row[5] is not None and row[6] is not None]
                planes_df = pd.DataFrame(selected_data, columns=[
                    'icao24', 'callsign', 'origin_country', 'longitude', 'latitude', 
                    'baro_altitude', 'velocity', 'heading', 'vertical_rate'
                ])
                planes_df['source'] = 'planes'
                planes_df['altitude_m'] = planes_df['baro_altitude'].fillna(0)
                planes_df = planes_df.dropna(subset=['latitude', 'longitude'])
                
                # Add location info for first plane (to avoid rate limiting)
                if len(planes_df) > 0:
                    first_plane = planes_df.iloc[0]
                    loc_info = get_location_info(first_plane['latitude'], first_plane['longitude'])
                    planes_df['nearby_city'] = loc_info.get('city', 'Unknown')
                
                return planes_df
    except Exception as e:
        print(f"Error fetching planes: {e}")
    return pd.DataFrame()

def fetch_satellites():
    """Fetch and propagate satellite positions using Skyfield."""
    sats_df = pd.DataFrame()
    ts = load.timescale()
    t = ts.now()
    stations_url = 'https://celestrak.org/NORAD/elements/gp.php?FORMAT=TLE&CATNR='
    try:
        for catnr in SATELLITE_CATALOG_NUMBERS:
            tle_data = requests.get(stations_url + str(catnr), timeout=10).text.splitlines()
            if len(tle_data) >= 2:
                satellite = EarthSatellite(tle_data[1], tle_data[2], tle_data[0])
                geocentric = satellite.at(t)
                subpoint = wgs84.subpoint(geocentric)
                sat_data = {
                    'name': satellite.name,
                    'latitude': subpoint.latitude.degrees,
                    'longitude': subpoint.longitude.degrees,
                    'altitude_km': subpoint.elevation.km,
                    'source': 'satellites'
                }
                sats_df = pd.concat([sats_df, pd.DataFrame([sat_data])], ignore_index=True)
        sats_df['altitude_m'] = sats_df['altitude_km'] * 1000
    except Exception as e:
        print(f"Error fetching satellites: {e}")
    return sats_df

def fetch_traffic_cams():
    """Fetch frames from RTSP streams and apply detection."""
    cam_data = []
    for cam in TRAFFIC_CAM_STREAMS:
        try:
            cam_info = {
                'id': cam['id'],
                'location': cam['location'],
                'latitude': cam['lat'],
                'longitude': cam['lon'],
                'url': cam['url'],
                'source': 'cams',
                'altitude_m': 0,
                'status': 'active'
            }
            cam_data.append(cam_info)
        except Exception as e:
            print(f"Error fetching cam {cam['url']}: {e}")
    return pd.DataFrame(cam_data)

def generate_camera_frames(camera_id):
    """Generator function to stream camera frames with support for multiple formats."""
    if camera_id >= len(TRAFFIC_CAM_STREAMS):
        return
    
    cam_config = TRAFFIC_CAM_STREAMS[camera_id]
    url = cam_config['url']
    
    print(f"[Camera {camera_id}] Attempting to connect to: {cam_config['location']}")
    
    # Try to open video stream with specific options
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    
    # Set properties for better streaming
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FPS, 10)
    
    frame_count = 0
    retry_count = 0
    max_retries = 3
    last_frame = None
    
    while True:
        try:
            success, frame = cap.read()
            
            if not success:
                retry_count += 1
                print(f"[Camera {camera_id}] Failed to read frame, retry {retry_count}/{max_retries}")
                
                if retry_count >= max_retries:
                    # Create error frame
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(frame, 'Camera Offline', (150, 220), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                    cv2.putText(frame, cam_config['location'], (100, 270), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    cv2.putText(frame, 'Attempting reconnect...', (130, 320), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    time.sleep(3)
                    
                    # Try to reconnect
                    cap.release()
                    print(f"[Camera {camera_id}] Reconnecting...")
                    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    cap.set(cv2.CAP_PROP_FPS, 10)
                    retry_count = 0
                else:
                    # Use last frame if available
                    if last_frame is not None:
                        ret, buffer = cv2.imencode('.jpg', last_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                        frame_bytes = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    time.sleep(0.5)
                continue
            
            # Successfully read frame
            retry_count = 0
            frame_count += 1
            
            if frame_count % 100 == 0:
                print(f"[Camera {camera_id}] {cam_config['location']}: {frame_count} frames streamed")
            
            # Resize frame for better streaming performance
            h, w = frame.shape[:2]
            if w > 640:
                frame = cv2.resize(frame, (640, 480))
            
            # Add overlay information
            overlay_bg = frame.copy()
            cv2.rectangle(overlay_bg, (0, 0), (640, 90), (0, 0, 0), -1)
            frame = cv2.addWeighted(overlay_bg, 0.6, frame, 0.4, 0)
            
            cv2.putText(frame, cam_config['location'], (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"LIVE | Frame: {frame_count}", (10, 55), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            cv2.putText(frame, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), (10, 75), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Save for retry fallback
            last_frame = frame.copy()
            
            # Encode frame as JPEG with moderate quality
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
            frame_bytes = buffer.tobytes()
            
            # Yield frame in multipart format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # Control frame rate (~8-10 FPS for optimal performance)
            time.sleep(0.1)
            
        except GeneratorExit:
            print(f"[Camera {camera_id}] Client disconnected")
            break
        except Exception as e:
            print(f"[Camera {camera_id}] Error generating frame: {e}")
            # Create error frame
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, 'Stream Error', (180, 220), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            cv2.putText(frame, str(e)[:40], (50, 270), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(1)
    
    # Cleanup
    cap.release()
    print(f"[Camera {camera_id}] Stream ended")

def check_collisions(planes, sats):
    """Detect potential collisions or proximities."""
    alerts = []
    
    # Check if dataframes are empty
    if planes.empty and sats.empty:
        return alerts
    
    # Clean data - remove NaN values
    if not planes.empty:
        planes = planes.dropna(subset=['latitude', 'longitude', 'altitude_m']).reset_index(drop=True)
    if not sats.empty:
        sats = sats.dropna(subset=['latitude', 'longitude', 'altitude_m']).reset_index(drop=True)
    
    # Plane-Plane proximity
    if len(planes) > 1:
        for i in range(len(planes)):
            for j in range(i + 1, len(planes)):
                try:
                    horiz_dist = haversine(planes.iloc[i]['longitude'], planes.iloc[i]['latitude'],
                                         planes.iloc[j]['longitude'], planes.iloc[j]['latitude'])
                    vert_dist = abs(planes.iloc[i]['altitude_m'] - planes.iloc[j]['altitude_m'])
                    if horiz_dist < PLANE_PLANE_HORIZ_THRESHOLD and vert_dist < PLANE_PLANE_VERT_THRESHOLD:
                        alerts.append({
                            'type': 'CRITICAL',
                            'category': 'Plane-Plane Collision Risk',
                            'message': f"Potential collision between {planes.iloc[i]['icao24']} and {planes.iloc[j]['icao24']}",
                            'details': f"Horizontal: {horiz_dist:.0f}m, Vertical: {vert_dist:.0f}m",
                            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                except Exception as e:
                    print(f"Error checking plane-plane collision: {e}")
    
    # Sat-Sat proximity
    if len(sats) > 1:
        for i in range(len(sats)):
            for j in range(i + 1, len(sats)):
                try:
                    horiz_dist = haversine(sats.iloc[i]['longitude'], sats.iloc[i]['latitude'],
                                         sats.iloc[j]['longitude'], sats.iloc[j]['latitude'])
                    vert_dist = abs(sats.iloc[i]['altitude_m'] - sats.iloc[j]['altitude_m'])
                    if horiz_dist < SAT_SAT_HORIZ_THRESHOLD and vert_dist < SAT_SAT_VERT_THRESHOLD:
                        alerts.append({
                            'type': 'WARNING',
                            'category': 'Satellite-Satellite Conjunction',
                            'message': f"Proximity between {sats.iloc[i]['name']} and {sats.iloc[j]['name']}",
                            'details': f"Horizontal: {horiz_dist:.0f}m, Vertical: {vert_dist:.0f}m",
                            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                except Exception as e:
                    print(f"Error checking sat-sat collision: {e}")
    
    # Plane-Sat proximity
    if not planes.empty and not sats.empty:
        for pi in range(len(planes)):
            for si in range(len(sats)):
                try:
                    horiz_dist = haversine(planes.iloc[pi]['longitude'], planes.iloc[pi]['latitude'], 
                                         sats.iloc[si]['longitude'], sats.iloc[si]['latitude'])
                    if horiz_dist < PLANE_SAT_HORIZ_THRESHOLD:
                        alerts.append({
                            'type': 'INFO',
                            'category': 'Plane-Satellite Ground Track',
                            'message': f"Plane {planes.iloc[pi]['icao24']} under {sats.iloc[si]['name']} ground track",
                            'details': f"Horizontal distance: {horiz_dist:.0f}m",
                            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                except Exception as e:
                    print(f"Error checking plane-sat proximity: {e}")
    
    return alerts

def generate_map(planes, sats, cams):
    """Create Folium map with markers."""
    m = folium.Map(location=[28.14, 77.32], zoom_start=8)
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add planes (filter out NaN values)
    if not planes.empty:
        planes_clean = planes.dropna(subset=['latitude', 'longitude'])
        for idx, row in planes_clean.iterrows():
            try:
                popup_text = f"Aircraft: {row['icao24']}<br>Callsign: {row.get('callsign', 'N/A')}<br>Altitude: {row['altitude_m']:.0f}m"
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=popup_text,
                    icon=folium.Icon(color='blue', icon='plane', prefix='fa')
                ).add_to(marker_cluster)
            except Exception as e:
                print(f"Error adding plane marker: {e}")
    
    # Add satellites (filter out NaN values)
    if not sats.empty:
        sats_clean = sats.dropna(subset=['latitude', 'longitude'])
        for idx, row in sats_clean.iterrows():
            try:
                popup_text = f"Satellite: {row['name']}<br>Altitude: {row['altitude_m']:.0f}m"
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=popup_text,
                    icon=folium.Icon(color='red', icon='satellite', prefix='fa')
                ).add_to(marker_cluster)
            except Exception as e:
                print(f"Error adding satellite marker: {e}")
    
    # Add cameras (filter out NaN values)
    if not cams.empty:
        cams_clean = cams.dropna(subset=['latitude', 'longitude'])
        for idx, row in cams_clean.iterrows():
            try:
                popup_text = f"Camera: {row['location']}"
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=popup_text,
                    icon=folium.Icon(color='green', icon='video-camera', prefix='fa')
                ).add_to(marker_cluster)
            except Exception as e:
                print(f"Error adding camera marker: {e}")
    
    return m._repr_html_()

def update_data():
    """Background thread to update data periodically."""
    while True:
        try:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching data...")
            
            # Fetch all data sources
            planes = fetch_planes()
            sats = fetch_satellites()
            cams = fetch_traffic_cams()
            weather = fetch_weather()
            traffic = fetch_traffic_info()
            
            # Ensure we have valid dataframes
            if planes is None or not isinstance(planes, pd.DataFrame):
                planes = pd.DataFrame()
            if sats is None or not isinstance(sats, pd.DataFrame):
                sats = pd.DataFrame()
            if cams is None or not isinstance(cams, pd.DataFrame):
                cams = pd.DataFrame()
            
            alerts = check_collisions(planes, sats)
            
            map_html = generate_map(planes, sats, cams)
            
            # Update global data
            global_data['planes'] = planes
            global_data['satellites'] = sats
            global_data['cameras'] = cams
            global_data['alerts'] = alerts
            global_data['weather'] = weather
            global_data['traffic_info'] = traffic
            global_data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            global_data['map_html'] = map_html
            
            # Store historical data (keep last 10 updates)
            global_data['historical_data']['planes'].append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'count': len(planes)
            })
            global_data['historical_data']['satellites'].append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'count': len(sats)
            })
            global_data['historical_data']['alerts'].append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'count': len(alerts)
            })
            
            # Keep only last 10 entries
            for key in global_data['historical_data']:
                if len(global_data['historical_data'][key]) > 10:
                    global_data['historical_data'][key] = global_data['historical_data'][key][-10:]
            
            print(f"Updated: {len(planes)} planes, {len(sats)} satellites, {len(cams)} cameras, {len(alerts)} alerts")
            print(f"Weather: {weather.get('condition', 'N/A')}, Traffic: {traffic.get('status', 'N/A')}")
            
        except Exception as e:
            print(f"Error updating data: {e}")
            import traceback
            traceback.print_exc()
        
        time.sleep(UPDATE_INTERVAL_SEC)

# Flask routes
@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/data')
def get_data():
    """API endpoint to get current data."""
    planes = global_data['planes']
    sats = global_data['satellites']
    cams = global_data['cameras']
    
    # Ensure dataframes exist
    if planes is None or not isinstance(planes, pd.DataFrame):
        planes = pd.DataFrame()
    if sats is None or not isinstance(sats, pd.DataFrame):
        sats = pd.DataFrame()
    if cams is None or not isinstance(cams, pd.DataFrame):
        cams = pd.DataFrame()
    
    # Replace NaN with None for JSON serialization
    planes_data = planes.replace({np.nan: None}).to_dict('records') if not planes.empty else []
    sats_data = sats.replace({np.nan: None}).to_dict('records') if not sats.empty else []
    cams_data = cams.replace({np.nan: None}).to_dict('records') if not cams.empty else []
    
    data = {
        'planes': planes_data,
        'satellites': sats_data,
        'cameras': cams_data,
        'alerts': global_data.get('alerts', []),
        'weather': global_data.get('weather', {}),
        'traffic': global_data.get('traffic_info', {}),
        'historical': global_data.get('historical_data', {}),
        'last_update': global_data.get('last_update', 'Never'),
        'stats': {
            'total_planes': len(planes),
            'total_satellites': len(sats),
            'total_cameras': len(cams),
            'total_alerts': len(global_data.get('alerts', []))
        }
    }
    return jsonify(data)

@app.route('/api/map')
def get_map():
    """API endpoint to get map HTML."""
    if global_data.get('map_html'):
        return global_data['map_html']
    # Generate a default map if none exists
    m = folium.Map(location=[28.14, 77.32], zoom_start=8)
    return m._repr_html_()

@app.route('/api/camera/<int:camera_id>')
def get_camera_stream(camera_id):
    """API endpoint to get camera stream info."""
    if camera_id < len(TRAFFIC_CAM_STREAMS):
        return jsonify(TRAFFIC_CAM_STREAMS[camera_id])
    return jsonify({'error': 'Camera not found'}), 404

@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(generate_camera_frames(camera_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/cameras/list')
def list_cameras():
    """Get list of all available cameras."""
    return jsonify({
        'cameras': TRAFFIC_CAM_STREAMS,
        'total': len(TRAFFIC_CAM_STREAMS)
    })

@app.route('/api/object/<object_type>/<object_id>')
def get_object_details(object_type, object_id):
    """API endpoint to get detailed information about a specific object."""
    try:
        if object_type == 'plane':
            planes = global_data.get('planes', pd.DataFrame())
            if not planes.empty:
                plane = planes[planes['icao24'] == object_id]
                if not plane.empty:
                    plane_data = plane.iloc[0].to_dict()
                    # Add location info
                    loc = get_location_info(plane_data['latitude'], plane_data['longitude'])
                    plane_data['location_info'] = loc
                    return jsonify(plane_data)
        elif object_type == 'satellite':
            sats = global_data.get('satellites', pd.DataFrame())
            if not sats.empty:
                sat = sats[sats['name'] == object_id]
                if not sat.empty:
                    return jsonify(sat.iloc[0].to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Object not found'}), 404

if __name__ == '__main__':
    # Start background data update thread
    update_thread = threading.Thread(target=update_data, daemon=True)
    update_thread.start()
    
    # Give it a moment to fetch initial data
    time.sleep(2)
    
    print("\n" + "="*60)
    print("Real-Time Situational Awareness System - Web UI")
    print("="*60)
    print("\nStarting Flask server...")
    print("Access the dashboard at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
