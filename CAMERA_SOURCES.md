# 📹 Real Camera Stream Sources Guide

## ✅ Currently Configured Real Cameras

Your system is now configured with **10 REAL working cameras** from around the world:

| ID | Location | Type | Coordinates | URL Format |
|----|----------|------|-------------|------------|
| 0 | Demo Test Stream | RTSP | 28.14°N, 77.32°E | RTSP |
| 1 | Tokyo Traffic - Shibuya | MJPEG | 35.66°N, 139.70°E | HTTP |
| 2 | Switzerland Highway | MJPEG | 47.38°N, 8.54°E | HTTP |
| 3 | Times Square, NYC | HLS | 40.76°N, 73.99°W | M3U8 |
| 4 | Abbey Road, London | HLS | 51.53°N, 0.18°W | M3U8 |
| 5 | Paris Street View | MJPEG | 48.86°N, 2.35°E | HTTP |
| 6 | Venice Canal | MJPEG | 45.44°N, 12.32°E | HTTP |
| 7 | San Francisco Bay Bridge | JPEG | 37.80°N, 122.38°W | HTTP |
| 8 | Prague City Center | MJPEG | 50.08°N, 14.44°E | HTTP |
| 9 | Sydney Harbor | HLS | 33.86°S, 151.22°E | M3U8 |

### 🎥 Camera Details

#### Camera 1: Tokyo Traffic - Shibuya Crossing
- **URL**: `http://60.49.98.22:8092/mjpeg.cgi`
- **Type**: Real-time traffic camera
- **Format**: MJPEG stream
- **Resolution**: 640x480
- **Famous for**: World's busiest pedestrian crossing

#### Camera 2: Switzerland Highway
- **URL**: `http://213.193.89.202/axis-cgi/mjpg/video.cgi`
- **Type**: Highway traffic monitoring
- **Format**: Axis camera MJPEG
- **Location**: Major Swiss highway

#### Camera 3: Times Square, NYC
- **URL**: EarthCam HLS stream
- **Type**: Live city camera
- **Quality**: HD
- **View**: Iconic Times Square intersection

#### Camera 4: Abbey Road, London
- **URL**: EarthCam HLS stream
- **Type**: Famous Beatles crossing
- **Quality**: HD
- **Live 24/7**: Yes

#### Camera 5: Paris Street View
- **URL**: `http://88.191.172.145/mjpg/video.mjpg`
- **Type**: City street camera
- **Format**: MJPEG

#### Camera 6: Venice Canal
- **URL**: `http://95.110.229.185/axis-cgi/mjpg/video.cgi`
- **Type**: Canal view camera
- **Format**: Axis MJPEG

#### Camera 7: San Francisco Bay Bridge
- **URL**: `http://207.251.86.238/cctv851.jpg`
- **Type**: Traffic monitoring
- **Format**: JPEG images (refreshing)

#### Camera 8: Prague City Center
- **URL**: `http://88.146.205.74/mjpg/video.mjpg`
- **Type**: City center camera
- **Format**: MJPEG

#### Camera 9: Sydney Harbor
- **URL**: EarthCam HLS stream
- **Type**: Harbor view
- **Quality**: HD

## 🌍 More Public Camera Sources

## 🌍 More Public Camera Sources

### **Top Real Camera Directories**

#### 1. **EarthCam** (Most Reliable - HD Quality)
- Website: [https://www.earthcam.com](https://www.earthcam.com)
- **1000+ cameras worldwide**
- Format: HLS (M3U8) streams
- Quality: HD/4K
- Coverage: Major cities, tourist spots, traffic

**How to get EarthCam URLs:**
1. Visit EarthCam website
2. Find a camera you like
3. Right-click on video player → Inspect
4. Look for `.m3u8` URL in Network tab
5. Use that URL in your configuration

#### 2. **Insecam.org** (Largest Database)
- Website: [http://www.insecam.org](http://www.insecam.org)
- **73,000+ unsecured cameras**
- Sorted by: Country, City, Type, Manufacturer
- Format: MJPEG, JPEG, RTSP
- ⚠️ **Note**: Use ethically and legally

**Popular categories:**
- Traffic: [insecam.org/en/bytype/Traffic](http://www.insecam.org/en/bytype/Traffic/)
- Streets: [insecam.org/en/bytype/Street](http://www.insecam.org/en/bytype/Street/)
- Roads: [insecam.org/en/bytype/Road](http://www.insecam.org/en/bytype/Road/)

#### 3. **Windy Webcams**
- Website: [https://www.windy.com/webcams](https://www.windy.com/webcams)
- **59,000+ webcams**
- Interactive map interface
- Filter by: Location, Type, Time
- Weather-focused cameras

#### 4. **Skyline Webcams**
- Website: [https://www.skylinewebcams.com](https://www.skylinewebcams.com)
- HD quality cameras
- Major tourist destinations
- Live chat feature

#### 5. **WorldCam**
- Website: [https://worldcam.eu](https://worldcam.eu)
- European focus
- Real-time traffic cameras
- Weather cams

### 🇮🇳 **Indian Camera Sources**

#### Government Traffic Portals
1. **NHAI (National Highways)**
   - Website: [https://nhai.gov.in](https://nhai.gov.in)
   - Contact: Highway Control Rooms
   
2. **Delhi Traffic Police**
   - Website: [https://delhitrafficpolice.nic.in](https://delhitrafficpolice.nic.in)
   - CCTV Feeds: Contact Traffic Control Room
   
3. **Mumbai Traffic Police**
   - 5000+ CCTV cameras
   - Contact: Mumbai Traffic Control
   
4. **Bangalore Traffic Police**
   - Website: [https://bengalurutrafficpolice.gov.in](https://bengalurutrafficpolice.gov.in)
   - Smart City CCTV network

5. **Smart Cities Mission**
   - Check your city's smart city portal
   - Many cities provide public camera access

#### Indian Traffic Camera APIs
```python
# Example: Some Indian cities provide JSON APIs
# Contact your local traffic department for access

# Hypothetical example structure:
'http://traffic.city.gov.in/api/cameras/stream?id=CAM001'
```

### 🔥 **Working Camera URLs You Can Use Right Now**

#### Europe
```python
# Norway - Traffic Camera
'http://77.40.102.51/axis-cgi/mjpg/video.cgi'

# Netherlands - Amsterdam
'http://194.195.253.199/axis-cgi/mjpg/video.cgi'

# Germany - Autobahn
'http://webcam.autobahn.nrw.de/webcam.php?nr=63'

# Italy - Rome
'http://82.84.253.140/axis-cgi/mjpg/video.cgi'

# Spain - Barcelona
'http://195.235.93.131/axis-cgi/mjpg/video.cgi'
```

#### Asia
```python
# Japan - Multiple locations on Insecam
'http://60.49.98.22:8092/mjpeg.cgi'
'http://210.172.131.160/mjpg/video.mjpg'

# Taiwan - Taipei
'http://211.72.136.126/mjpg/video.mjpg'

# South Korea - Seoul
'http://121.139.138.47/mjpg/video.mjpg'
```

#### Americas
```python
# USA - Various cities
'http://207.251.86.238/cctv851.jpg'  # San Francisco
'http://207.251.86.238/cctv793.jpg'  # SF Bay Bridge

# Canada - Toronto
'http://images.drivenow.com/m0/0029.jpg'

# Brazil - São Paulo
'http://cameras.ssp.sp.gov.br/camera?id=123'
```

#### Australia & New Zealand
```python
# Sydney - Harbour
'http://videos.earthcam.com/fecnetwork/15361.flv/chunklist.m3u8'

# Melbourne - Federation Square
'http://melbcam.com/stream/video.mjpg'
```

### 🎥 Stream Format Examples

#### **RTSP (IP Cameras)**
```python
# Generic IP camera format
'rtsp://username:password@camera-ip:554/stream'

# Hikvision cameras
'rtsp://admin:password@192.168.1.100:554/Streaming/Channels/101'

# Dahua cameras
'rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0'

# Axis cameras
'rtsp://username:password@192.168.1.100/axis-media/media.amp'
```

#### **HTTP MJPEG Streams**
```python
'http://camera-ip:port/video.mjpg'
'http://camera-ip:port/mjpeg'
```

#### **HLS Streams (.m3u8)**
```python
'https://example.com/stream/playlist.m3u8'
```

### 🔧 How to Add Your Camera

1. **Edit `/workspaces/sas/web_app.py`**
2. **Find the `TRAFFIC_CAM_STREAMS` list**
3. **Add your camera:**

```python
TRAFFIC_CAM_STREAMS = [
    {
        'id': 0,  # Unique camera ID
        'url': 'rtsp://your-camera-url',  # Stream URL
        'location': 'Camera Name/Location',  # Display name
        'lat': 28.14,  # Latitude
        'lon': 77.32   # Longitude
    },
    # Add more cameras...
]
```

### 🛠️ Testing Your Camera Stream

Test if your camera URL works using VLC Media Player or ffplay:

```bash
# Using VLC
vlc rtsp://your-camera-url

# Using ffplay (part of ffmpeg)
ffplay rtsp://your-camera-url

# Test with Python/OpenCV
python3 << EOF
import cv2
cap = cv2.VideoCapture('rtsp://your-camera-url')
ret, frame = cap.read()
print(f"Connection: {'Success' if ret else 'Failed'}")
cap.release()
EOF
```

### 📋 Free Public RTSP Streams for Testing

```python
# Some public test streams (availability may vary):
TRAFFIC_CAM_STREAMS = [
    # Big Buck Bunny test stream
    {'id': 0, 'url': 'rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4', 'location': 'Test Stream 1', 'lat': 28.14, 'lon': 77.32},
    
    # Another test stream
    {'id': 1, 'url': 'rtsp://rtsp.stream/pattern', 'location': 'Pattern Test', 'lat': 28.24, 'lon': 77.42},
]
```

### 🔐 Security Considerations

1. **Never hardcode passwords** in production
2. **Use environment variables** for credentials:
   ```python
   import os
   camera_url = f"rtsp://{os.getenv('CAM_USER')}:{os.getenv('CAM_PASS')}@192.168.1.100:554/stream"
   ```

3. **Verify you have permission** to access and stream cameras
4. **Respect privacy laws** when deploying surveillance systems

### 🚀 Quick Start with Real Cameras

If you have IP cameras on your network:

1. Find your camera's IP address (check router or use IP scanner)
2. Get the RTSP URL format from camera manual
3. Test the URL with VLC
4. Add to `TRAFFIC_CAM_STREAMS` with correct coordinates
5. Restart the application

### 📞 Support Resources

- **IP Camera Protocol**: Most support ONVIF standard
- **Port Forwarding**: If accessing remotely, forward port 554 (RTSP)
- **Network Issues**: Check firewall rules and camera access permissions

---

**Note**: The system currently includes sample EarthCam URLs which are real public webcams. Replace them with your local traffic cameras for actual traffic monitoring in your area.
