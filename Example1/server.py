import os
from http.server import SimpleHTTPRequestHandler, HTTPServer

class MyHandle(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        try:
            # Tenta abrir o arquivo 'index.html' no caminho solicitado.
            with open(os.path.join(path, 'index.html'), 'r', encoding='utf-8') as f:
                self.send_response(200) # Se o arquivo for encontrado, uma resposta 200 é enviada.
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(f.read().encode('utf-8')) # O conteúdo do arquivo é lido e enviado na resposta.
            return None
        
        # Caso dê errado:
        except FileNotFoundError:
            return super().list_directory(path)

    # Lida com as requisições do tipo GET.
    def do_GET(self):
        # Um dicionário de rodas para encaminhar aos HTMLs específicos.
        routes = {
            "/login": "login.html",
            "/cadastro": "cadastro.html",
            "/listar_filmes": "listar_filmes.html",
        }

        # Verifica se o caminho da requisição está presente no dicionário de rotas.
        if self.path in routes:
            file_path = os.path.join(os.getcwd(), routes[self.path])
            try:
                # Tenta abrir e ler o arquivo HTML especificado pela rota.
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))
            except FileNotFoundError:
                # Caso o arquivo não seja encontrado, envia uma resposta de erro 404.
                self.send_error(404, "File not found")
        else:
            super().do_GET()

# Função que cofigura e inicia o servidor.
def main():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MyHandle)
    print("Server running in http://localhost:8000")
    httpd.serve_forever()

# Garante que a função `main()` seja chamada apenas quando o script é executado.
if __name__ == "__main__":
    main()