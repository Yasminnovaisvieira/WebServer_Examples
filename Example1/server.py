import os
from http.server import SimpleHTTPRequestHandler, HTTPServer

class MyHandle(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        try:
            with open(os.path.join(path, 'index.html'), 'r', encoding='utf-8') as f:
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(f.read().encode('utf-8'))
            return None
        except FileNotFoundError:
            return super().list_directory(path)

    def do_GET(self):
        routes = {
            "/login": "login.html",
            "/cadastro": "cadastro.html",
            "/listar_filmes": "listar_filmes.html",
        }

        if self.path in routes:
            file_path = os.path.join(os.getcwd(), routes[self.path])
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))
            except FileNotFoundError:
                self.send_error(404, "File not found")
        else:
            super().do_GET()

def main():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MyHandle)
    print("Server running in http://localhost:8000")
    httpd.serve_forever()

if __name__ == "__main__":
    main()