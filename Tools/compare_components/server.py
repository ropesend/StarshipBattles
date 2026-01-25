import http.server
import socketserver
import json
import os
import shutil
from urllib.parse import urlparse, parse_qs
from PIL import Image

PORT = 8000
BASE_DIR = r"C:\Developer\StarshipBattles\assets\Images\Components"
INPUT_DIR = os.path.join(BASE_DIR, "New Component images")
OUTPUT_DIR = os.path.join(BASE_DIR, "Processed Components")
FLAGGED_DIR = os.path.join(BASE_DIR, "Flagged_For_Review")

class ComparisonHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/api/list":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            pairs = []
            for f in files:
                stem = os.path.splitext(f)[0]
                processed = f"{stem}_no_bg.png"
                pairs.append({
                    "original": f,
                    "processed": processed if os.path.exists(os.path.join(OUTPUT_DIR, processed)) else None
                })
            
            self.wfile.write(json.dumps(pairs).encode())
            return
        
        # Serve images from their specific directories
        if url.path.startswith("/img/original/"):
            filename = url.path.replace("/img/original/", "")
            self.serve_file(os.path.join(INPUT_DIR, filename))
            return
        if url.path.startswith("/img/processed/"):
            filename = url.path.replace("/img/processed/", "")
            self.serve_file(os.path.join(OUTPUT_DIR, filename))
            return

        return super().do_GET()

    def do_POST(self):
        url = urlparse(self.path)
        if url.path == "/api/action":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            action = data.get("action")
            filename = data.get("filename") # original filename (e.g. comp_000.jpg)
            stem = os.path.splitext(filename)[0]
            processed_name = f"{stem}_no_bg.png"
            
            orig_path = os.path.join(INPUT_DIR, filename)
            proc_path = os.path.join(OUTPUT_DIR, processed_name)
            flag_path = os.path.join(FLAGGED_DIR, filename)

            success = False
            message = ""

            if action == "restore":
                try:
                    # Convert original to PNG and overwrite processed
                    with Image.open(orig_path) as img:
                        img.save(proc_path, "PNG")
                    success = True
                    message = f"Restored {filename} to {processed_name}"
                except Exception as e:
                    message = str(e)
            
            elif action == "flag":
                try:
                    shutil.copy2(orig_path, flag_path)
                    success = True
                    message = f"Flagged {filename} for review"
                except Exception as e:
                    message = str(e)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": success, "message": message}).encode())
            return

    def serve_file(self, path):
        if not os.path.exists(path):
            self.send_error(404)
            return
        
        content_type = "image/jpeg" if path.lower().endswith((".jpg", ".jpeg")) else "image/png"
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()
        with open(path, 'rb') as f:
            self.wfile.write(f.read())

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with socketserver.TCPServer(("", PORT), ComparisonHandler) as httpd:
        print(f"Server started at http://localhost:{PORT}")
        httpd.serve_forever()
