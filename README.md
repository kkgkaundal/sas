# 🛰️ Real-Time Situational Awareness System (SAS)

Advanced real-time monitoring system that tracks aircraft, satellites, and live traffic cameras with collision detection and alert capabilities.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## ✨ Features

- **🛩️ Live Aircraft Tracking**: Real-time aircraft monitoring via OpenSky Network API
- **🛰️ Satellite Tracking**: Track satellites using TLE data from CelesTrak
- **📹 Live Camera Feeds**: 10 real working cameras from around the world
- **⚠️ Collision Detection**: Automated proximity alerts for planes and satellites
- **🗺️ Interactive Map**: Real-time visualization with Folium
- **🌤️ Weather Integration**: Live weather data for monitored areas
- **🚦 Traffic Monitoring**: Traffic status and congestion data
- **📊 Historical Analytics**: Charts and trends of tracked objects
- **🔴 LIVE Streaming**: Real-time MJPEG video streaming from cameras

## 📹 Real Camera Locations

The system includes **10 verified working cameras**:

1. 🇷🇴 **Demo Test Stream** - Test RTSP feed
2. 🇯🇵 **Tokyo Traffic - Shibuya** - Famous crossing (MJPEG)
3. 🇨🇭 **Switzerland Highway** - Traffic monitoring (MJPEG)
4. 🇺🇸 **Times Square, NYC** - Live city camera (HD/HLS)
5. 🇬🇧 **Abbey Road, London** - Beatles crossing (HD/HLS)
6. 🇫🇷 **Paris Street View** - City camera (MJPEG)
7. 🇮🇹 **Venice Canal** - Canal view (MJPEG)
8. 🇺🇸 **San Francisco Bay Bridge** - Bridge traffic (JPEG)
9. 🇨🇿 **Prague City Center** - City view (MJPEG)
10. 🇦🇺 **Sydney Harbor** - Harbor view (HD/HLS)

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Internet connection

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/kkgkaundal/sas.git
cd sas
```

2. **Create virtual environment** (recommended)
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running the Application

1. **Test your cameras** (optional but recommended)
```bash
python test_cameras.py
```

2. **Start the web application**
```bash
python web_app.py
```

3. **Open your browser**
```
http://localhost:5000
```

## 📸 Adding Your Own Cameras

Edit `web_app.py` and add your camera to the `TRAFFIC_CAM_STREAMS` list:

```python
TRAFFIC_CAM_STREAMS = [
    {
        'id': 10,  # Unique ID
        'url': 'rtsp://your-camera-ip:554/stream',  # Camera URL
        'location': 'My Camera Location',  # Display name
        'lat': 28.14,  # Latitude
        'lon': 77.32   # Longitude
    },
    # Add more cameras...
]
```

### Supported Camera Formats

- **RTSP**: `rtsp://camera-ip:port/stream`
- **HTTP MJPEG**: `http://camera-ip/mjpeg`
- **HLS (M3U8)**: `http://server.com/stream.m3u8`
- **JPEG**: `http://camera-ip/image.jpg`

See [CAMERA_SOURCES.md](CAMERA_SOURCES.md) for detailed camera configuration guide and more sources.

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Web Dashboard (Flask)                  │
│  ┌───────────┬──────────┬────────────┬───────────────┐ │
│  │   Map     │  Alerts  │  Weather   │   Traffic     │ │
│  └───────────┴──────────┴────────────┴───────────────┘ │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                   │
┌───────▼────────┐  ┌─────▼──────┐  ┌────────▼────────┐
│  OpenSky API   │  │  CelesTrak │  │  Camera Streams │
│   (Aircraft)   │  │ (Satellites)│  │  (RTSP/MJPEG)  │
└────────────────┘  └────────────┘  └─────────────────┘
```

## 🛠️ Configuration

### Bounding Box (Monitoring Area)
Edit in `web_app.py`:
```python
BOUNDING_BOX = {
    'min_lat': 27.0,
    'min_lon': 76.0,
    'max_lat': 29.0,
    'max_lon': 78.0
}
```

### Update Interval
```python
UPDATE_INTERVAL_SEC = 30  # Refresh every 30 seconds
```

### Collision Thresholds
```python
PLANE_PLANE_HORIZ_THRESHOLD = 10000  # 10km
PLANE_PLANE_VERT_THRESHOLD = 1000    # 1km
```

## 📡 API Endpoints

- `GET /` - Main dashboard
- `GET /api/data` - Get current data (planes, satellites, cameras, alerts)
- `GET /api/map` - Get map HTML
- `GET /api/cameras/list` - List all cameras
- `GET /video_feed/<camera_id>` - Live video stream (MJPEG)
- `GET /api/camera/<camera_id>` - Camera information

## 🔧 Troubleshooting

### Cameras Not Loading

1. **Test individual camera**:
```bash
python test_cameras.py
```

2. **Test with VLC**:
```bash
vlc http://camera-url
```

3. **Check firewall**: Ensure ports 554 (RTSP) and 80/8080 (HTTP) are open

### No Aircraft Data

- Check internet connection
- OpenSky Network may have rate limits
- Verify bounding box includes active airspace

### Application Won't Start

```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check for errors
python web_app.py
```

## 📚 Documentation

- [CAMERA_SOURCES.md](CAMERA_SOURCES.md) - Complete guide to finding and adding real cameras
- [LICENSE](LICENSE) - MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenSky Network for aircraft data
- CelesTrak for satellite TLE data
- EarthCam for public webcam access
- All public camera providers

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check [CAMERA_SOURCES.md](CAMERA_SOURCES.md) for camera configuration help

## 🔮 Future Enhancements

- [ ] AI-powered object detection on camera feeds
- [ ] Mobile app version
- [ ] Email/SMS alerts for collisions
- [ ] Historical data analytics
- [ ] Multi-user support
- [ ] Custom alert rules
- [ ] Export data to CSV/JSON

---

**Made with ❤️ for aviation and space enthusiasts**