#! /bin/python3
import subprocess
import sys

# TODO: If password is changed of access point this script wont connect to it (fix it later)

def get_available_wifi():
    try:
        result = subprocess.run(['nmcli', '-f', 'SSID', 'dev', 'wifi', 'list'], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')[1:]
        available_wifi = [line.split()[0] for line in lines]
        
        return available_wifi
    except subprocess.CalledProcessError:
        print("Error: Unable to retrieve available Wi-Fi networks.")
        return []

def show_wifi_menu(available_wifi):
    menu_items = '\n'.join(available_wifi)
    
    rofi_cmd = ['rofi', '-dmenu', '-p', 'Select Wi-Fi network:', '-lines', str(len(available_wifi)) , '-theme' , "~/worksapce/code/dev-rofi-applets/network-manager/rofi-themes/wifi-list.rasi"]
    rofi_proc = subprocess.Popen(rofi_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    selected_wifi, _ = rofi_proc.communicate(input=menu_items)
    
    return selected_wifi.strip()

def get_connected_wifi_info():
    
    try:
        result = subprocess.run(['nmcli', '-t', '-f', 'active,ssid,SIGNAL', 'dev', 'wifi'], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if line.startswith('yes'):
                connected_info = line.split(":")
                connected_ssid = connected_info[1]
                signal_strength = int(connected_info[2])
        
                if 0 <= signal_strength <= 30:
                    return f'󰤟 {connected_ssid}'
                if 30 < signal_strength <= 50:
                    return f'󰤢 {connected_ssid}'
                elif 50 < signal_strength <= 80: 
                    return f'󰤥 {connected_ssid}'
                elif 80 < signal_strength <= 100: 
                    return f'󰤨 {connected_ssid}'
                else :
                    return f'󰤯 {connected_ssid}'
            
    except subprocess.CalledProcessError:
        print("Error: Unable to retrieve connected Wi-Fi network information.")
        return None, None

def is_wifi_saved(ssid):
    try:
        result = subprocess.run(['nmcli', 'connection', 'show', ssid], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        print("Error: Unable to check Wi-Fi connection status.")
        return False

def connect_to_new_wifi(ssid, password):
    try:
        connect_result = subprocess.run(['nmcli', 'device', 'wifi', 'connect', ssid, 'password', password], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if connect_result.returncode == 0:
            print("Successfully connected to Wi-Fi network:", ssid)
        else:
            print("Failed to connect to Wi-Fi network:", ssid)
    except subprocess.CalledProcessError:
        # Handle error if nmcli command fails
        print("Error: Unable to connect to Wi-Fi network.")
        
def connect_to_wifi(ssid):
    command = ["nmcli", "connection", "up", ssid]
    try:
        subprocess.run(command, check=True)
        print(f"Connected to Wi-Fi network: {ssid}")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to connect to Wi-Fi network {ssid}. Details: {e}")

def rofi_wifi_password(ssid):
    try:
        password = subprocess.check_output(['rofi', '-dmenu', '-p', f'Enter password for Wi-Fi network {ssid}:'], input='', text=True).strip()
        return password
    except subprocess.CalledProcessError:
        print("Error: Unable to prompt for password.")
        return None

args = sys.argv

if __name__ == "__main__":

    if args[1] == "--connected-wifi-ssid":
        print(get_connected_wifi_info())
        
    elif args[1] == "--wifi-list":
        available_wifi_list = get_available_wifi()
        if available_wifi_list:
        
            selected_wifi = show_wifi_menu(available_wifi_list)
            
            if selected_wifi:
                print("Selected Wi-Fi network:", selected_wifi)
                if is_wifi_saved(selected_wifi):
                    # If wifi is saved just fucking connect to it
                    print(f'{selected_wifi} is saved')
                    connect_to_wifi(selected_wifi)
                else :
                    print(f'{selected_wifi} is not saved')
                    password = rofi_wifi_password(selected_wifi)
                    connect_to_new_wifi(selected_wifi, password)
                #connect_to_wifi(selected_wifi)
            else:
                print("No Wi-Fi network selected.")
        else:
            print("No Wi-Fi networks available.")
    
