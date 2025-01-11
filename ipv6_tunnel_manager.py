import os
import subprocess
import json
import logging
from tabulate import tabulate

def setup_logging():
    logging.basicConfig(
        filename='logs/script.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

# Load servers configuration from a JSON file
def load_servers(config_path="config/servers.json"):
    try:
        with open(config_path, "r") as file:
            servers = json.load(file)
        return servers
    except FileNotFoundError:
        logging.error("Configuration file not found.")
        print("Configuration file not found.")
        return []

# Check server status using ping
def check_server_status(server_ip):
    try:
        subprocess.check_output(["ping", "-c", "1", server_ip], stderr=subprocess.DEVNULL)
        return "Online"
    except subprocess.CalledProcessError:
        return "Offline"

# Display status of all servers
def display_status(servers):
    data = []
    for server in servers:
        status = check_server_status(server["remote_ip"])
        data.append([server["name"], server["tunnel_type"], server["remote_ip"], status])
    print(tabulate(data, headers=["Server Name", "Tunnel Type", "Remote IP", "Status"], tablefmt="grid"))

# Set up a tunnel based on the specified type
def setup_tunnel(server, local_tunnel):
    tunnel_type = server["tunnel_type"]
    remote_ip = server["remote_ip"]
    
    try:
        if tunnel_type == "6TO4":
            os.system(f"sudo ip tunnel add {local_tunnel} mode sit remote {remote_ip} ttl 255")
        elif tunnel_type == "GRE6":
            os.system(f"sudo ip tunnel add {local_tunnel} mode gre6 remote {remote_ip} ttl 255")
        elif tunnel_type == "IP6IP6":
            os.system(f"sudo ip tunnel add {local_tunnel} mode ip6ip6 remote {remote_ip} ttl 255")
        elif tunnel_type == "ANYCAST":
            print("ANYCAST tunnel setup is not fully implemented yet.")
        else:
            print(f"Unsupported tunnel type: {tunnel_type}")
            return

        os.system(f"sudo ip link set {local_tunnel} up")
        print(f"Tunnel {local_tunnel} configured for server {server['name']}.")
        logging.info(f"Tunnel {local_tunnel} configured for server {server['name']}.")
    except Exception as e:
        logging.error(f"Failed to configure tunnel: {e}")
        print(f"Error: {e}")

# Delete a tunnel
def delete_tunnel(tunnel_name):
    try:
        os.system(f"sudo ip tunnel del {tunnel_name}")
        print(f"Tunnel {tunnel_name} deleted successfully.")
        logging.info(f"Tunnel {tunnel_name} deleted successfully.")
    except Exception as e:
        logging.error(f"Failed to delete tunnel: {e}")
        print(f"Error deleting tunnel: {e}")

# Update the script from the GitHub repository
def update_script():
    repo_dir = "/opt/ipv6-tunnel-script"
    try:
        if os.path.exists(repo_dir):
            os.chdir(repo_dir)
            subprocess.run(["git", "pull"], check=True)
            print("Script updated successfully!")
            logging.info("Script updated successfully!")
        else:
            print("Repository not found. Please clone it first.")
            logging.error("Repository not found. Please clone it first.")
    except Exception as e:
        logging.error(f"Update failed: {e}")
        print(f"Update failed: {e}")

# Main menu
def main():
    setup_logging()
    servers = load_servers()

    while True:
        print("\n1. Display Server Status")
        print("2. Configure Tunnel")
        print("3. Delete Tunnel")
        print("4. Update Script")
        print("5. Exit")
        
        choice = input("Choose an option: ").strip()
        
        if choice == "1":
            display_status(servers)
        elif choice == "2":
            print("\nAvailable Servers:")
            for i, server in enumerate(servers, start=1):
                print(f"{i}. {server['name']} ({server['tunnel_type']})")
            server_choice = int(input("Select a server: ")) - 1
            if 0 <= server_choice < len(servers):
                local_tunnel = input("Enter a name for the local tunnel interface: ").strip()
                setup_tunnel(servers[server_choice], local_tunnel)
            else:
                print("Invalid choice!")
        elif choice == "3":
            tunnel_name = input("Enter the tunnel name to delete: ").strip()
            delete_tunnel(tunnel_name)
        elif choice == "4":
            update_script()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid option! Please try again.")

if __name__ == "__main__":
    main()
