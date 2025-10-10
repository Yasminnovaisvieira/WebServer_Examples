import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import json # Para salvar o cadastro dos filmes
import mysql.connector

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "senai",
    database = "locadora" # Database que vai puxar os dados
)

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
        
    def loadFilminhos(self):
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM locadora.diretor")
        result = cursor.fetchall()

        print("******************/n", result)

        for res in result:
            id_diretor = res[0]
            nome = res[1]
            sobrenome = res[2]
            genero = res[3]
            print(id_diretor, nome, sobrenome, genero)

    #Verificação simples de usuário logado ou não logado
    def accont_user(self, login,password):
        loga = "yasminnovaisvieira@gmail.com"
        senha = "1234"
        return login == loga and senha == password

    # Lida com as requisições do tipo GET.
    def do_GET(self):
        # Analisa a URL para separar o caminho dos parâmetros de consulta
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # ================================================
        # ROTA API FILMES -> agora puxa direto do MySQL
        # ================================================
        if self.path == '/api/filmes':
            try:
                cursor = mydb.cursor(dictionary=True)
                cursor.execute("""
                    SELECT 
                        id_filme,
                        titulo,
                        autor AS atores,   -- renomeia 'autor' para 'atores' pro front entender
                        diretor,
                        ano,
                        genero,
                        produtora,
                        sinopse
                    FROM filme
                """)
                filmes = cursor.fetchall()

                if not filmes:
                    filmes = []

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(filmes, ensure_ascii=False).encode("utf-8"))
            except mysql.connector.Error as err:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(err)}).encode("utf-8"))
            return
        
        # ================================================
        # ROTA EDITAR FILME (mantida, mas ainda usa JSON)
        # ================================================
        if path == '/editar_filme':
            query_params = parse_qs(parsed_path.query)
            titulo_para_editar = query_params.get('titulo', [None])[0]

            if not titulo_para_editar:
                self.send_error(400, "Título do filme não fornecido")
                return

            try:
                with open("filmes.json", "r", encoding="utf-8") as f:
                    filmes = json.load(f)
                
                # Encontra o filme específico para editar
                filme_encontrado = next((f for f in filmes if f['titulo'] == titulo_para_editar), None)

                if not filme_encontrado:
                    self.send_error(404, "Filme não encontrado")
                    return

                # Carrega o HTML de edição e preenche os campos do formulário
                with open("editar_filme.html", "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Preenche os valores do formulário
                content = content.replace('value=""', f'value="{filme_encontrado.get("titulo", "")}"', 1)
                content = content.replace('name="titulo"', f'name="titulo" value="{filme_encontrado.get("titulo", "")}"')
                content = content.replace('name="atores"', f'name="atores" value="{filme_encontrado.get("atores", "")}"')
                content = content.replace('name="diretor"', f'name="diretor" value="{filme_encontrado.get("diretor", "")}"')
                content = content.replace('name="ano"', f'name="ano" value="{filme_encontrado.get("ano", "")}"')
                content = content.replace('name="genero"', f'name="genero" value="{filme_encontrado.get("genero", "")}"')
                content = content.replace('name="produtora"', f'name="produtora" value="{filme_encontrado.get("produtora", "")}"')
                # Para o textarea (sinopse), o preenchimento é diferente
                content = content.replace('</textarea>', f'{filme_encontrado.get("sinopse", "")}</textarea>')
                # Adiciona um campo oculto com o título antigo para referência
                content = content.replace('</form>', f'<input type="hidden" name="titulo_antigo" value="{titulo_para_editar}"></form>')

                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))

            except FileNotFoundError:
                self.send_error(404, "Arquivo de filmes ou template de edição não encontrado")
            return

        # Um dicionário de rotas para encaminhar aos HTMLs específicos.
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
 
            if self.accont_user(login, password):
                # Sucesso no login
                self.send_response(303)
                self.send_header("Location", "/cadastro_filmes")
                self.end_headers()
            else:
                # Falha no login
                self.send_response(401)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write("Usuário ou senha inválidos".encode('utf-8'))
            return

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

            # ALTERADO: grava no banco MySQL em vez de JSON
            cursor = mydb.cursor()
            sql = """
                INSERT INTO filme (titulo, autor, diretor, ano, genero, produtora, sinopse)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            val = (titulo, atores, diretor, ano, genero, produtora, sinopse)
            cursor.execute(sql, val)
            mydb.commit()
            
            self.send_response(303)
            self.send_header("Location", "/listar_filmes")
            self.end_headers()
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
