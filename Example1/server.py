import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import json # Para salvar o cadastro dos filmes

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

    #Verificação simples de usuário logado ou não logado
    def accont_user(self, login,password):
        loga = "yasminnovaisvieira@gmail.com"
        senha = "1234"
 
        if login == loga and senha == password:
            # Redireciona para a página de cadastro de filmes
            self.send_response(303)
            self.send_header("Location", "/cadastro_filmes")
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("Usuário Não Existe")

    # Lida com as requisições do tipo GET.
    def do_GET(self):
        if self.path == '/api/filmes':
            try:
                with open("filmes.json", "r", encoding="utf-8") as f:
                    data = f.read()

            except FileNotFoundError:
                data = "[]"
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(data.encode("utf-8"))
            return

        # Um dicionário de rodas para encaminhar aos HTMLs específicos.
        routes = {
            "/login": "login.html",
            "/cadastro_filmes": "cadastro_filmes.html",
            "/listar_filmes": "listar_filmes.html",
            "/editar_filme": "editar_filme.html",
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

    def do_POST(self):
        if self.path == '/send_login':
            #Tamanho da requisição que está sendo mandada
            content_length = int(self.headers['Content-length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body)

            login = form_data.get('email',[""])[0]
            password = form_data.get('senha',[""])[0]
            logou = self.accont_user(login, password)
 
            print("Data Form:")
            print("Email:", form_data.get('email',[""])[0])
            print("Senha:", form_data.get("senha",[""])[0])
           
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(logou.encode('utf-8'))
            return # Para encerrar a operação
        
         # Cadastrar Filmes
        elif self.path == '/cadastro_filme':
            #Tamanho da requisição que está sendo mandada
            content_length = int(self.headers['Content-length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body)

            titulo = form_data.get('titulo', [""])[0]
            atores = form_data.get('atores', [""])[0]
            diretor = form_data.get('diretor', [""])[0]
            ano = form_data.get('ano', [""])[0]
            genero = form_data.get('genero', [""])[0]
            produtora = form_data.get('produtora', [""])[0]
            sinopse = form_data.get('sinopse', [""])[0]

            filme = {"titulo": titulo, "atores": atores, "diretor": diretor, "ano": ano, "genero": genero, "produtora": produtora, "sinopse": sinopse}

            # Se o arquivo existir, carrega os filmes. Se não, começa com lista vazia.
            if os.path.exists("filmes.json"):
                with open("filmes.json", "r", encoding="utf-8") as f:
                    filmes = json.load(f)
            else:
                filmes = []

            filmes.append(filme)

            with open("filmes.json", "w", encoding="utf-8") as f:
                json.dump(filmes, f, ensure_ascii=False, indent=4)

            
            self.send_response(303)
            self.send_header("Location", "/listar_filmes")
            self.end_headers()
        
        # Deletar Filme
        elif self.path == '/delete_filme':
            content_length = int(self.headers['Content-length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body)

            titulo = form_data.get('titulo', [""])[0]

            try:
                with open("filmes.json", "r", encoding="utf-8") as f:
                    filmes = json.load(f)
            except FileNotFoundError:
                filmes = []

            filmes = [f for f in filmes if f['titulo'] != titulo]

            with open("filmes.json", "w", encoding="utf-8") as f:
                json.dump(filmes, f, ensure_ascii=False, indent=4)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Filme deletado')
            return

        # Editar Filme
        elif self.path == '/edit_filme':
            content_length = int(self.headers['Content-length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body)

            titulo_antigo = form_data.get('titulo_antigo', [""])[0]
            novo_filme = {
                "titulo": form_data.get('titulo', [""])[0],
                "atores": form_data.get('atores', [""])[0],
                "diretor": form_data.get('diretor', [""])[0],
                "ano": form_data.get('ano', [""])[0],
                "genero": form_data.get('genero', [""])[0],
                "produtora": form_data.get('produtora', [""])[0],
                "sinopse": form_data.get('sinopse', [""])[0],
            }

            try:
                with open("filmes.json", "r", encoding="utf-8") as f:
                    filmes = json.load(f)
            except FileNotFoundError:
                filmes = []

            filmes = [novo_filme if f['titulo'] == titulo_antigo else f for f in filmes]

            with open("filmes.json", "w", encoding="utf-8") as f:
                json.dump(filmes, f, ensure_ascii=False, indent=4)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Filme editado')
            return
        else:
            super(MyHandle, self).do_POST()
            return

# Função que cofigura e inicia o servidor.
def main():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MyHandle)
    print("Server running in http://localhost:8000")
    httpd.serve_forever()

# Garante que a função `main()` seja chamada apenas quando o script é executado.
if __name__ == "__main__":
    main()