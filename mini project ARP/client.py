import socket
import threading
from getmac import get_mac_address
import queue


def get_ip_and_mac():
    """Retrieve the local IP address and MAC address of the device."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
    except Exception:
        ip_address = "127.0.0.1"

    mac_address = get_mac_address()
    return ip_address, mac_address


# def get_ip_and_mac():
#     # Specify the client IP manually for testing
#     ip_address = "192.168.1.101"  # Change this for each client instance
#     mac_address = "02:00:00:00:00:01"  # Placeholder MAC for testing
#     return ip_address, mac_address

def listen_for_notifications(sock, notification_queue):
    """Thread to listen for incoming notifications from the server."""
    while True:
        try:
            data = sock.recv(1024).decode('utf-8')
            if data.startswith("PINGED"):
                notification_queue.put(data)  # Add notifications to the queue
        except Exception as e:
            notification_queue.put(f"ERROR|{e}")
            break


def display_notifications(notification_queue):
    """Display any queued notifications without interrupting user input."""
    while not notification_queue.empty():
        data = notification_queue.get()
        if data.startswith("PINGED"):
            source_ip, source_mac = data.split('|')[1:]
            print(f"\n[Notification] You have been pinged by IP={source_ip}, MAC={source_mac}")
        elif data.startswith("ERROR"):
            print(f"\n[Error] {data.split('|')[1]}")


def main():
    server_ip = '192.168.29.13'  # Change to your server's IP
    server_port = 12345

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    # Automatically register IP and MAC address
    ip_address, mac_address = get_ip_and_mac()
    message = f"REGISTER|{ip_address}|{mac_address}"
    client_socket.send(message.encode('utf-8'))
    response = client_socket.recv(1024).decode('utf-8')
    print(f"Registration Status: {response}")

    # Queue for notifications
    notification_queue = queue.Queue()

    # Start a thread to listen for notifications
    threading.Thread(target=listen_for_notifications, args=(client_socket, notification_queue), daemon=True).start()

    try:
        while True:
            # Display any notifications before showing the menu
            display_notifications(notification_queue)

            # User menu
            print("\nOptions:")
            print("1. Ping another client")
            print("2. Show ARP Table")
            print("3. Exit")
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                target_ip = input("Enter target IP address: ").strip()
                if not target_ip:
                    print("Target IP address is required.")
                    continue
                message = f"PING|{ip_address}|{mac_address}|{target_ip}"
                client_socket.send(message.encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                if response.startswith("PING_SUCCESS"):
                    _, target_ip, target_mac = response.split('|')
                    print(f"Ping successful! Target IP: {target_ip}, MAC: {target_mac}")
                elif response.startswith("PING_FAILURE"):
                    print(f"Ping failed: {response.split('|')[1]}")
                else:
                    print("Unexpected response: " + response)

            elif choice == "2":
                client_socket.send("ARP_TABLE|".encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                print("ARP Table:\n" + response)

            elif choice == "3":
                print("Exiting.")
                break

            else:
                print("Invalid choice. Try again.")

    finally:
        client_socket.close()


if __name__ == "__main__":
    main()
