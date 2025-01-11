import os
import subprocess
import json
import logging
from tabulate import tabulate
from colorama import Fore, Style
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

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
        print(f"Loaded servers: {servers}")  # Debugging
        return servers
    except FileNotFoundError:
        logging.error("Configuration file not found.")
        print("Configuration file not found.")
        return []

# Check server status using ping
def check_server_status(server_ip):
    print(f"Checking status for: {server_ip}")  # Debugging
    try:
        subprocess.check_output(["ping", "-c", "1", server_ip], stderr=subprocess.DEVNULL)
        return "Online"
    except subprocess.CalledProcessError:
        return "Offline"

# Display status of all servers using Rich tables
def display_status_rich(servers):
    console = Console()
    table = Table(title="Server Status")

    table.add_column("Server Name", style="cyan", justify="left")
    table.add_column("Tunnel Type", style="green", justify="center")
    table.add_column("Remote IP", style="magenta", justify="center")
    table.add_column("Status", style="bold red", justify="center")

    for server in servers:
        status = check_server_status(server["remote_ip"])
        table.add_row(server["name"], server["tunnel_type"], server["remote_ip"], status)

    console.print(table)

# Show messages with Rich panels
def show_message(message, message_type="info"):
    console = Console()
    if message_type == "info":
        console.print(Panel(f"[cyan]{message}[/cyan]", title="[bold green]Info[/bold green]"))
    elif message_type == "error":
        console.print(Panel(f"[red]{message}[/red]", title="[bold red]Error[/bold red]"))
    elif message_type == "success":
        console.print(Panel(f"[green]{message}[/green]", title="[bold blue]Success[/bold blue]"))

# Set up a tunnel based on the specified type
def setup_tunnel(server, local_tunnel):
    tunnel_type = server["tunnel_type"]
    remote_ip = server["remote_ip"]
    local_ip = input("Enter the local IP for this server: ").strip()
    
    try:
        if tunnel_type == "6TO4":
            os.system(f"sudo ip tunnel add {local_tunnel} mode sit remote {remote_ip} ttl 255")
        elif tunnel_type == "GRE6":
            os.system(f"sudo ip tunnel add {local_tunnel} mode gre remote {remote_ip} local {local_ip} ttl 255")
        elif tunnel_type == "IP6IP6":
            os.system(f"sudo ip tunnel add {local_tunnel} mode ip6ip6 remote {remote_ip} ttl 255")
        elif tunnel_type == "ANYCAST":
            print("ANYCAST tunnel setup is not fully implemented yet.")
        else:
            print(f"Unsupported tunnel type: {tunnel_type}")
            return

        # تنظیم IP برای اینترفیس تونل
        os.system(f"sudo ip addr add {local_ip}/30 dev {local_tunnel}")
        os.system(f"sudo ip link set {local_tunnel} up")
        
        show_message(f"Tunnel {local_tunnel} configured for server {server['name']} with local IP {local_ip}.", "success")
        logging.info(f"Tunnel {local_tunnel} configured for server {server['name']} with local IP {local_ip}.")
    except Exception as e:
        logging.error(f"Failed to configure tunnel: {e}")
        show_message(f"Error: {e}", "error")

# Delete a tunnel
def delete_tunnel(tunnel_name):
    try:
        os.system(f"sudo ip tunnel del {tunnel_name}")
        show_message(f"Tunnel {tunnel_name} deleted successfully.", "success")
        logging.info(f"Tunnel {tunnel_name} deleted successfully.")
    except Exception as e:
        logging.error(f"Failed to delete tunnel: {e}")
        show_message(f"Error deleting tunnel: {e}", "error")

# Update the script from the GitHub repository
def update_script():
    repo_dir = "/opt/ipv6-tunnel-script"
    try:
        if os.path.exists(repo_dir):
            os.chdir(repo_dir)
            subprocess.run(["git", "pull"], check=True)
            show_message("Script updated successfully!", "success")
            logging.info("Script updated successfully!")
        else:
            show_message("Repository not found. Please clone it first.", "error")
            logging.error("Repository not found. Please clone it first.")
    except Exception as e:
        logging.error(f"Update failed: {e}")
        show_message(f"Update failed: {e}", "error")

# Main menu
def main_menu():
    print(Fore.CYAN + "\n1. Display Server Status" + Style.RESET_ALL)
    print(Fore.GREEN + "2. Configure Tunnel" + Style.RESET_ALL)
    print(Fore.RED + "3. Delete Tunnel" + Style.RESET_ALL)
    print(Fore.YELLOW + "4. Update Script" + Style.RESET_ALL)
    print(Fore.MAGENTA + "5. Exit" + Style.RESET_ALL)

def main():
    setup_logging()
    servers = load_servers()

    while True:
        print(Fore.CYAN + "\nIPv6 Tunnel Manager" + Style.RESET_ALL)
        main_menu()
        
        choice = input(Fore.YELLOW + "Choose an option: " + Style.RESET_ALL).strip()
        
        if choice == "1":
            display_status_rich(servers)
        elif choice == "2":
            show_message("Configuring Tunnel...", "info")
            print("\nAvailable Servers:")
            for i, server in enumerate(servers, start=1):
                print(f"{i}. {server['name']} ({server['tunnel_type']})")
            server_choice = int(input("Select a server: ")) - 1
            if 0 <= server_choice < len(servers):
                local_tunnel = input("Enter a name for the local tunnel interface: ").strip()
                setup_tunnel(servers[server_choice], local_tunnel)
            else:
                show_message("Invalid choice!", "error")
        elif choice == "3":
            tunnel_name = input("Enter the tunnel name to delete: ").strip()
            delete_tunnel(tunnel_name)
        elif choice == "4":
            update_script()
        elif choice == "5":
            show_message("Exiting...", "success")
            break
        else:
            show_message("Invalid option! Please try again.", "error")

if __name__ == "__main__":
    main()
