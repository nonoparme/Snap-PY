#!/usr/bin/env python3

import os
import requests
import websocket
from datetime import datetime

# ===================== CONFIG =====================

# IP address of the printer / Klipper host
# Use 127.0.0.1 if the script runs directly on the printer
PRINTER_IP = "127.0.0.1"

# Snapshot URL for MJPEG / USB camera
SNAPSHOT_URL = f"http://{PRINTER_IP}/webcam/?action=snapshot"

# Base directory where timelapse frames will be saved
BASE_DIR = "/home/cp/timelapse_frames"

# =================================================


def ensure_base_dir():
    """Create base directory if it does not exist."""
    os.makedirs(BASE_DIR, exist_ok=True)


def take_snapshot():
    """Capture a snapshot and save it with a timestamp-based filename."""
    now = datetime.now()

    # Timestamp format: YYYY-MM-DD_HH-MM-SS_milliseconds
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S_%f")[:-3]

    filename = f"frame_{timestamp}.jpg"
    filepath = os.path.join(BASE_DIR, filename)

    try:
        response = requests.get(SNAPSHOT_URL, timeout=5)
        if response.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"[Timelapse] Saved snapshot: {filename}")
        else:
            print("[Timelapse] Snapshot failed (HTTP error)")
    except Exception as e:
        print(f"[Timelapse] Snapshot exception: {e}")


def on_message(ws, message):
    """Listen for M118 SNAP commands from Klipper."""
    if "SNAP" in message:
        take_snapshot()


def on_open(ws):
    """Called when the WebSocket connection is established."""
    print("[Timelapse] Connected to Moonraker WebSocket")


def main():
    ensure_base_dir()

    # Moonraker WebSocket endpoint
    ws_url = f"ws://{PRINTER_IP}/websocket"

    ws = websocket.WebSocketApp(
        ws_url,
        on_message=on_message,
        on_open=on_open
    )

    ws.run_forever()


if __name__ == "__main__":
    main()
