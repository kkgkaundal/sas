#!/usr/bin/env python3
"""
Camera Stream Tester
Tests all configured cameras to verify they're working
"""

import cv2
import sys
from web_app import TRAFFIC_CAM_STREAMS

def test_camera(cam_id, cam_config):
    """Test a single camera stream"""
    print(f"\n{'='*60}")
    print(f"Testing Camera {cam_id}: {cam_config['location']}")
    print(f"URL: {cam_config['url']}")
    print(f"Coordinates: {cam_config['lat']}, {cam_config['lon']}")
    print(f"{'='*60}")
    
    try:
        # Try to open video stream
        cap = cv2.VideoCapture(cam_config['url'], cv2.CAP_FFMPEG)
        
        # Try to read a frame
        ret, frame = cap.read()
        
        if ret and frame is not None:
            height, width = frame.shape[:2]
            print(f"✅ SUCCESS - Camera is working!")
            print(f"   Resolution: {width}x{height}")
            print(f"   Format: {cam_config['url'].split('.')[-1].upper()}")
            cap.release()
            return True
        else:
            print(f"❌ FAILED - Could not read frame")
            print(f"   The camera might be offline or URL invalid")
            cap.release()
            return False
            
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")
        return False

def main():
    """Test all cameras"""
    print("\n" + "="*60)
    print("Camera Stream Tester")
    print("Testing all configured cameras...")
    print("="*60)
    
    total_cameras = len(TRAFFIC_CAM_STREAMS)
    working_cameras = 0
    failed_cameras = []
    
    for cam in TRAFFIC_CAM_STREAMS:
        if test_camera(cam['id'], cam):
            working_cameras += 1
        else:
            failed_cameras.append(cam['id'])
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total Cameras: {total_cameras}")
    print(f"Working: {working_cameras} ✅")
    print(f"Failed: {len(failed_cameras)} ❌")
    
    if failed_cameras:
        print(f"\nFailed Camera IDs: {', '.join(map(str, failed_cameras))}")
        print("\nNote: Some cameras may be temporarily offline or require")
        print("specific network conditions. Try them in the web interface.")
    
    print("\n" + "="*60)
    
    if working_cameras > 0:
        print(f"\n✅ {working_cameras} camera(s) are working!")
        print("You can now run the web application:")
        print("   python web_app.py")
    else:
        print("\n⚠️  No cameras are currently accessible.")
        print("Please check your internet connection or try different camera URLs.")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTesting interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)
