import socket

def main():
    host = '0.0.0.0'  # Listen on all available interfaces
    start_port = 40010
    end_port = 40013

    for port in range(start_port, end_port + 1):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server_socket.bind((host, port))
            server_socket.listen(1)
            print(f"Listening for incoming connections on port {port}...")
            while True:
                try:
                    client_socket, client_address = server_socket.accept()
                    print(f"Connection from: {client_address}")
                    client_socket.send(b"Connection successful! Port forwarding is working.")
                    client_socket.close()
                except KeyboardInterrupt:
                    print("Server stopped.")
                    break
        except OSError:
            print(f"Port {port} is already in use or cannot be bound.")

if __name__ == "__main__":
    main()