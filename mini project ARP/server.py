import socket
import threading

# ARP Table format: {IP: MAC}
arp_table = {}

# Connected clients: {IP: connection_object}
connected_clients = {}


def handle_client(conn, addr):
    print(f"Client connected: {addr}")
    client_ip = None
    try:
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break

            command = data.split('|')[0]
            if command == "REGISTER":
                ip, mac = data.split('|')[1:]
                arp_table[ip] = mac
                connected_clients[ip] = conn  # Track the client's connection
                client_ip = ip
                print(f"Registered: IP={ip}, MAC={mac}")
                conn.send("REGISTERED".encode('utf-8'))

            elif command == "PING":
                source_ip, source_mac, target_ip = data.split('|')[1:]
                # Ensure the source IP/MAC are in the ARP table
                if source_ip not in arp_table:
                    arp_table[source_ip] = source_mac

                # Notify the target client if they are connected
                if target_ip in connected_clients:
                    target_conn = connected_clients[target_ip]
                    try:
                        target_conn.send(
                            f"PINGED|{source_ip}|{source_mac}".encode('utf-8'))
                        response = f"PING_SUCCESS|{target_ip}|{arp_table[target_ip]}"
                    except Exception as e:
                        response = f"PING_FAILURE|Unable to notify target: {e}"
                else:
                    response = "PING_FAILURE|Target client not connected"

                conn.send(response.encode('utf-8'))

            elif command == "ARP_TABLE":
                table = "\n".join(
                    [f"{ip} -> {mac}" for ip, mac in arp_table.items()])
                conn.send(table.encode('utf-8'))
    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        if client_ip in connected_clients:
            del connected_clients[client_ip]
        conn.close()
        print(f"Client disconnected: {addr}")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 12345))
    server.listen(5)
    print("ARP Server running on port 12345")
    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()
    except KeyboardInterrupt:
        print("\nShutting down server.")
    finally:
        server.close()


if __name__ == "__main__":
    main()
