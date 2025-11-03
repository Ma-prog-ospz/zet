import os
import sys
import threading
import logging
import argparse
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sock import Sock

# --- Dodaj parent direktorij u sys.path da se može importati fetcher ---
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# --- Uvoz Fetcher klase ---
from fetcher import Fetcher

# --- Flask setup ---
app = Flask(__name__, static_folder="../static")
if os.environ.get("ZET_DEV") == "1":
    CORS(app, origins=["https://zet-6shc.onrender.com"])
else:
    CORS(app)

sock = Sock(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fetcher_instance = None


# --- Argument parser setup ---
def create_parser():
    parser = argparse.ArgumentParser(description="GTFS Realtime Coordinate Server")
    add = parser.add_argument
    add("--realtime-url", help="URL to fetch the GTFS protobuf file",
        default="https://www.zet.hr/gtfs-rt-protobuf")
    add("--static-url", help="URL to fetch the GTFS static data",
        default="https://www.zet.hr/gtfs-scheduled/latest")
    add("--realtime-dt", type=float, default=10,
        help="Interval between realtime fetches (seconds)")
    add("--static-dt", type=float, default=3600,
        help="Interval between static fetches (seconds)")
    add("--dir", default=".",
        help="Directory to store snapshots")
    add("--ws-port", type=int, default=8765,
        help="WebSocket server port (default: 8765)")
    add("--port", type=int, default=5000,
        help="Flask server port (default: 5000)")
    return parser


# --- Main function ---
def main():
    parser = create_parser()
    args = parser.parse_args()

    global fetcher_instance
    fetcher_instance = Fetcher(
        realtime_url=args.realtime_url,
        static_url=args.static_url,
        realtime_dt=args.realtime_dt,
        static_dt=args.static_dt,
        db_dir=args.dir,
        ws_port=args.ws_port,
    )

    # Pokreni Fetcher u pozadini
    fetch_thread = threading.Thread(target=fetcher_instance.run, daemon=True)
    fetch_thread.start()

    # Render traži da koristiš port iz env varijable PORT
    port = int(os.environ.get("PORT", args.port))
    app.run(host="0.0.0.0", port=port)


# --- Jednostavan endpoint za provjeru ---
@app.route("/")
def index():
    return jsonify({"status": "✅ GTFS Fetcher running!", "ws_port": 8765})


if __name__ == "__main__":
    main()
