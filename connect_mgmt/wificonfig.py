# wificonfig.py
import subprocess
import os

class WiFiConfigurator:
    WPA_SUPPLICANT_FILE = "/etc/wpa_supplicant/wpa_supplicant.conf"
    HOSTAPD_CONF_FILE = "/etc/hostapd/hostapd.conf"

    @classmethod
    def get_current_mode(cls):
        # Check if the hostapd service is running
        hostapd_status = subprocess.run(["sudo", "systemctl", "is-active", "hostapd"], capture_output=True, text=True)
        if hostapd_status.stdout.strip() == "active":
            return "ap"

        # Check if the wpa_supplicant service is running
        wpa_supplicant_status = subprocess.run(["sudo", "systemctl", "is-active", "wpa_supplicant"],
                                               capture_output=True, text=True)
        if wpa_supplicant_status.stdout.strip() == "active":
            return "wifi"

        return None  # Return None if neither service is active
    @staticmethod
    def switch_to_ap_mode(ap_ssid, ap_password):
        current_mode = WiFiConfigurator.get_current_mode()

        if current_mode == "ap":
            # Disable AP mode
            subprocess.run(["sudo", "systemctl", "stop", "hostapd"])
        else:
            # Disable WiFi client mode
            subprocess.run(["sudo", "systemctl", "stop", "wpa_supplicant"])


        # Start the access point
        subprocess.run(["sudo", "systemctl", "start", "hostapd"])
        # Update hostapd.conf with new AP SSID and password
        hostapd_config = f"ssid={ap_ssid}\nwpa_passphrase={ap_password}\n"
        with open(WiFiConfigurator.HOSTAPD_CONF_FILE, "w") as hostapd_file:
            hostapd_file.write(hostapd_config)

    @staticmethod
    def switch_to_wifi_mode(ssid, password):
        current_mode = WiFiConfigurator.get_current_mode()

        if current_mode == "ap":
            # Disable AP mode
            subprocess.run(["sudo", "systemctl", "stop", "hostapd"])
        else:
            # Disable WiFi client mode
            subprocess.run(["sudo", "systemctl", "stop", "wpa_supplicant"])

        # Start WiFi client mode
        subprocess.run(["sudo", "systemctl", "stop", "wpa_supplicant"])
        # Update wpa_supplicant.conf with WiFi credentials
        wpa_config = f"country=GB\n" \
                     f"update_config=1\n" \
                     f"ctrl_interface=/var/run/wpa_supplicant\n" \
                     f"network={{\n    scan_ssid=1\n    ssid=\"{ssid}\"\n    psk=\"{password}\"\n}}"
        try:
            with open(WiFiConfigurator.WPA_SUPPLICANT_FILE, "w") as wpa_file:
                wpa_file.write(wpa_config)
                pass
        except Exception as e:
            print("Error:", e)
            print("Current working directory:", os.getcwd())
            print("File path:", WiFiConfigurator.WPA_SUPPLICANT_FILE)


        # Enable WiFi client mode
        # subprocess.run(["sudo", "echo", "your content here", ">", WiFiConfigurator.WPA_SUPPLICANT_FILE], shell=True)

        subprocess.run(["sudo", "systemctl", "start", "wpa_supplicant"])
    @staticmethod
    def restart_pi():
        subprocess.run(["sudo", "reboot"])
