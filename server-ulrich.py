import socket, os

# Coleta os dados dos clientes válidos
with open('users.txt','r') as file: # Abre o arquivo de users em modo de leitura
    dados_usuarios = file.readlines() # Faz a leitura das linhas do arquivo

clientes_validos = [line.strip() for line in dados_usuarios] # Segmenta os dados dos usuários na lista clientes_validos

# Função para iniciar o servidor
def start_server(host='0.0.0.0', port=11550): # Delimita o IP e a Porta utilizada para o servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Define o uso de TCP e IPv4
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Servidor PTA ouvindo em -> {host}:{port}")
    
    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Conexão aceita de -> {addr}")
            handle_client(client_socket)
    except KeyboardInterrupt:
        print("\nDesligando servidor...")
    finally:
        print("Servidor desligado.")
        server_socket.close()

def handle_client(client_socket):
    try:
        while True:
            request = client_socket.recv(2048).decode('utf-8').strip().split() # Recebe a mensagem do cliente
            seq_num = request[0]
            command = request[1]

            if len(request) < 2:
                client_socket.send(b'NOK\n')
                client_socket.close()

            elif command == "CUMP":
                if len(request) > 2 and request[2] in clientes_validos: # Verifica se o cliente é válido
                    client_socket.send(f"{seq_num} OK".encode('utf-8'))
                else:
                    client_socket.send(f"{seq_num} NOK".encode('utf-8'))
                    client_socket.close()
                    break # Fecha a conexão se o cliente não for válido

            elif command == "LIST":
                files = os.listdir("files") # Diretório "Files" contendo os arquivos
                if files:
                    files_str = ",".join(files)
                    response = f"{seq_num} ARQS {len(files)} {files_str}\n"
                else:
                    response = f"{seq_num} NOK"
                client_socket.send(response.encode('utf-8'))

            elif command == "PEGA":
                if len(request) > 2:
                    filename = request[2]
                    file_path = os.path.join("files", filename)
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        client_socket.send(f"{seq_num} ARQ {file_size} {file_size}".encode('utf-8'))
                        
                        with open(file_path, 'rb') as f: # Envia o arquivo em pedaços
                            chunk = f.read(1024)
                            while chunk:
                                client_socket.send(chunk)
                                chunk = f.read(1024)
                    else:
                        client_socket.send(f"{seq_num} NOK".encode('utf-8'))
                else:
                    client_socket.send(f"{seq_num} NOK".encode('utf-8'))

            elif command == "TERM":
                client_socket.send(f"{seq_num} OK".encode('utf-8'))
                break

            else:
                client_socket.send(f"{seq_num} NOK".encode('utf-8'))
                client_socket.close()
                break
            
    except Exception as e:
        print(f"Erro ao processar o cliente: {e}")
    finally:
        client_socket.close()



# Inicia o servidor
if __name__ == "__main__":
    start_server()