import os
import threading
import logging
import argparse
import sys
from flask import Flask
from flask_cors import CORS
from flask_sock import Sock
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from gtfs_server import GtfsServer

# --- Flask setup ---
app = Flask(__name__, static_folder="../static")

if os.environ.get("ZET_DEV") == "1":
    CORS(app, origins=["https://zet-6shc.onrender.com"])

sock = Sock(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Argument parser setup ---
def create_parser():
    parser = argparse.ArgumentParser(
        description="GTFS Realtime Coordinate Server"
    )
    add = parser.add_argument
    add("--file", help="Path to the GTFS protobuf file")
    add("--url", help="URL to fetch the GTFS protobuf file",
        default="https://www.zet.hr/gtfs-rt-protobuf")
    add("--fetcher-url", type=str, default="ws://localhost:8765",
        help="URL of the fetcher server (default: ws://localhost:8765)")
    add("--port", type=int, default=5000,
        help="Port to run the server on (default: 5000)")
    add("--host", default="localhost",
        help="Host to run the server on (default: localhost)")
    return parser


# --- Main function ---
def main():
    parser = create_parser()
    args = parser.parse_args()

    global gtfs_server
    gtfs_server = GtfsServer(fetcher_url=args.fetcher_url)

    if args.url:
        update_thread = threading.Thread(
            target=gtfs_server.update_feed_continuously, daemon=True
        )
        update_thread.start()
    else:
        gtfs_server.update_feed_from_file(args.file)

    # Render traži da koristiš port iz env varijable PORT
    port = int(os.environ.get("PORT", args.port))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
