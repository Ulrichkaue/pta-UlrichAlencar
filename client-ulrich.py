import socket

# Função para conectar ao servidor
def connect_to_server(host='127.0.0.1', port=11550):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print(f"Conectado ao servidor {host}:{port}")
    return client_socket

# Função para enviar uma mensagem ao servidor
def send_message(client_socket, seq_num, command, args=None):
    message = f"{seq_num} {command}"
    if args:
        message += f" {args}"
    client_socket.send(message.encode('utf-8'))

# Função para receber a resposta do servidor
def receive_response(client_socket):
    response = client_socket.recv(4096).decode('utf-8').strip()
    return response

# Função principal para rodar o cliente
def run_client():
    host = '127.0.0.1'  # IP do servidor
    port = 11550  # Porta do servidor
    client_socket = connect_to_server(host, port)
    
    try:
        seq_num = 1  # Número de sequência inicial
        
        # Etapa 1: Apresentação (CUMP)
        client_name = input("Informe o seu nome: ")
        send_message(client_socket, seq_num, 'CUMP', client_name)
        response = receive_response(client_socket)
        print(f"{response}")
        
        # Verifica se o cliente foi aceito
        if 'NOK' in response:
            print("Cliente não aceito. Encerrando...")
            return
        
        seq_num += 1
        
        # Loop de interação com o servidor
        while True:
            print("\nComandos disponíveis: LIST, PEGA <arquivo>, TERM")
            command_input = input("Digite o comando: ").strip().split()
            
            if len(command_input) == 0:
                print("Comando inválido.")
                continue
            
            command = command_input[0]
            args = command_input[1] if len(command_input) > 1 else None
            
            # Envia o comando para o servidor
            send_message(client_socket, seq_num, command, args)
            response = receive_response(client_socket)
            print(f"{response}")
            
            # Se o comando for LIST, mostrar os arquivos disponíveis
            if command == 'LIST' and 'ARQS' in response:
                _, _, num_files, file_list = response.split(maxsplit=3)
            
            # Se o comando for PEGA, baixar o arquivo
            elif command == 'PEGA' and 'ARQ' in response:
                _, _, file_size, _ = response.split(maxsplit=4)
                file_size = int(file_size)
                print(f"Baixando arquivo de {file_size} bytes...")
                
                # Receber o arquivo em blocos
                with open(args, 'wb') as f:
                    bytes_received = 0
                    while bytes_received < file_size:
                        chunk = client_socket.recv(4096)
                        if not chunk:
                            break
                        f.write(chunk)
                        bytes_received += len(chunk)
                    print(f"Arquivo {args} recebido com sucesso!")
            
            # Se o comando for TERM, encerrar a conexão
            elif command == 'TERM':
                print("Encerrando a conexão...")
                break
            
            # Incrementar o número de sequência
            seq_num += 1
    
    except Exception as e:
        print(f"Erro: {e}")
    
    finally:
        client_socket.close()

# Rodar o cliente
if __name__ == "__main__":
    run_client()