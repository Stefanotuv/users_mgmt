# import datetime
#
# # Specify the file name
# file_name = "/home/stefano/Documents/my_file.txt"
#
# # Open the file in 'a' mode (append) to create it if it doesn't exist or append to it if it does
# with open(file_name, 'a') as file:
#     # Get the current date and time
#     current_datetime = datetime.datetime.now()
#     # Create a string with the generic text and the date/time
#     data = "Generic Text - {}".format(current_datetime)
#     # Write the data to the file
#     file.write(data + '\n')
#
# print(f"Data written to {file_name}")

# !/usr/bin/python3

import subprocess
import os
import time
import datetime
import re
import threading

NETWORK_MODE_FILE = "/etc/network_mode.conf"
DHCPD_CONF_FILE = "/etc/dhcpcd.conf"  # Update this path
LOG_FILE = "/home/stefano/log_pi.txt"  # Update this path


def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{timestamp} - {message}\n")


def start_hostapd():
    update_dhcpd_conf("ap")
    subprocess.run(["sudo", "systemctl", "stop", "wpa_supplicant"])
    subprocess.run(["sudo", "systemctl", "restart", "dhcpcd"])
    subprocess.run(["sudo", "systemctl", "restart", "hostapd"])
    subprocess.run(["sudo", "systemctl", "restart", "dnsmasq"])
    subprocess.run(["sudo", "systemctl", "restart", "dhcpcd"])


def start_wpa_supplicant():
    update_dhcpd_conf("wifi")

    subprocess.run(["sudo", "systemctl", "stop", "hostapd"])
    subprocess.run(["sudo", "systemctl", "stop", "dnsmasq"])
    subprocess.run(["sudo", "systemctl", "restart", "dhcpcd"])
    subprocess.run(["sudo", "systemctl", "start", "wpa_supplicant"])


def update_dhcpd_conf(network_mode):
    try:
        with open(DHCPD_CONF_FILE, "r") as dhcpd_file:
            lines = dhcpd_file.readlines()

        # Toggle the comments based on the network mode
        if network_mode == "wifi":
            #   if "#hostname\n" in lines:
            #       lines[lines.index("#hostname\n")] = "hostname\n"
            #   if "pi_zero\n" in lines:
            #       lines[lines.index("pi_zero\n")] = "#pi_zero\n"
            if "interface wlan0\n" in lines:
                lines[lines.index("interface wlan0\n")] = "#interface wlan0\n"
            if "static ip_address=192.168.4.1/24\n" in lines:
                lines[lines.index("static ip_address=192.168.4.1/24\n")] = "#static ip_address=192.168.4.1/24\n"
            if "nohook wpa_supplicant\n" in lines:
                lines[lines.index("nohook wpa_supplicant\n")] = "#nohook wpa_supplicant\n"
        elif network_mode == "ap":
            #    if "hostname\n" in lines:
            #        lines[lines.index("hostname\n")] = "#hostname\n"
            #    if "#pi_zero\n" in lines:
            #        lines[lines.index("#pi_zero\n")] = "pi_zero\n"
            if "#interface wlan0\n" in lines:
                lines[lines.index("#interface wlan0\n")] = "interface wlan0\n"
            if "#static ip_address=192.168.4.1/24\n" in lines:
                lines[lines.index("#static ip_address=192.168.4.1/24\n")] = "static ip_address=192.168.4.1/24\n"
            if "#nohook wpa_supplicant\n" in lines:
                lines[lines.index("#nohook wpa_supplicant\n")] = "nohook wpa_supplicant\n"

        # Write the modified lines back to the file
        with open(DHCPD_CONF_FILE, "w") as dhcpd_file:
            dhcpd_file.writelines(lines)

        log("dhcpd.conf file updated successfully")
    except Exception as e:
        log(f"Error updating dhcpd.conf: {e}")


# def get_current_ip():
# try:
# ip_output = subprocess.check_output(["ip", "route"]).decode()
# log(f"ip_output: {ip_output}")
# default_route = next(line for line in ip_output.splitlines() if "default" in line)
# log(f"default_route: {default_route}")
# match = re.search(r'src (\d+\.\d+\.\d+\.\d+)', default_route)
# log(f"match: {match}")
# if match:
# return match.group(1)
# except (subprocess.CalledProcessError, StopIteration):
# log(f"error on get_current_ip function")
# pass
# return None

def get_current_ip():
    try:
        ip_output = subprocess.check_output(["ip", "route"]).decode()
        log(f"ip_output: {ip_output}")

        # Check for a default route, or if in AP mode, the src address
        default_route_line = next((line for line in ip_output.splitlines() if "default" in line), None)
        ap_mode_line = next((line for line in ip_output.splitlines() if "src" in line and "192.168.4.1" in line), None)

        if default_route_line:
            log(f"default_route_line: {default_route_line}")
            match = re.search(r'src (\d+\.\d+\.\d+\.\d+)', default_route_line)
            if match:
                return match.group(1)

        if ap_mode_line:
            log(f"ap_mode_line: {ap_mode_line}")
            match = re.search(r'src (\d+\.\d+\.\d+\.\d+)', ap_mode_line)
            if match:
                return match.group(1)

    except subprocess.CalledProcessError:
        log(f"error on get_current_ip function")
        pass
    return None


def wait_for_ip(timeout_seconds=1):
    start_time = time.time()
    log(f"wait for ip start time: {start_time}")
    while True:
        current_ip = get_current_ip()
        log(f"looping for the current ip: {current_ip} at time: {time.time()}")
        if current_ip:
            return current_ip

        # if time.time() - start_time >= timeout_seconds:
        # return None

        time.sleep(.1)  # Wait for .1 second before checking again


class IPThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.current_ip = None
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            self.current_ip = wait_for_ip()
            if self.current_ip:
                log("IP address obtained.")
                break
            time.sleep(1)

    def stop(self):
        self._stop_event.set()


def update_nginx_thread():
    ip_thread = IPThread()
    ip_thread.start()
    ip_thread.join()  # Wait for IP address to be obtained
    if ip_thread.current_ip:
        update_nginx(ip_thread.current_ip)
        log("Nginx configuration updated.")


def update_nginx(current_ip):
    log("update nginx")
    nginx_config_path = "/etc/nginx/sites-available/users_mgmt"
    try:
        with open(nginx_config_path, 'r') as config_file:
            config_lines = config_file.readlines()

        with open(nginx_config_path, 'w') as config_file:
            for line in config_lines:
                if "server_name" in line:
                    line = f"    server_name {current_ip};\n"
                config_file.write(line)

        subprocess.run(["sudo", "systemctl", "reload", "nginx"])
        return True
    except Exception as e:
        log(f"Error updating nginx configuration: {e}")
        return False


def main():
    try:
        log("")
        log("--------------------------------------------------------")
        log("Script started")

        with open(NETWORK_MODE_FILE, "r") as mode_file:
            network_mode = mode_file.read().strip()
            log(f'network_mode ={network_mode}')
            if network_mode == "ap":
                log(f'pre hostapd')
                start_hostapd()
                # update_nginx()
                log("Switched to AP mode")
            elif network_mode == "wifi":
                log(f'pre start_wpa_supplicant')
                start_wpa_supplicant()
                # update_nginx()
                log("Switched to WiFi mode")
            else:
                log("Unknown network mode:", network_mode)

        # Start the nginx_update_background thread
        nginx_update_t = threading.Thread(target=update_nginx_thread)
        nginx_update_t.start()

    except Exception as e:
        log(f"Error: {e}")


if __name__ == "__main__":
    subprocess.run(["sudo", "systemctl", "start", "wpa_supplicant"])
    main()
