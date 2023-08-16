import subprocess

class WiFiConfigurator:
    WPA_SUPPLICANT_FILE = "/etc/wpa_supplicant/wpa_supplicant.conf"
    HOSTAPD_CONF_FILE = "/etc/hostapd/hostapd.conf"

    @staticmethod
    def switch_to_ap_mode():
        # Disable WiFi client mode
        subprocess.run(["sudo", "systemctl", "stop", "wpa_supplicant"])

        # Start the access point
        subprocess.run(["sudo", "systemctl", "start", "hostapd"])

    @staticmethod
    def switch_to_wifi_mode(ssid, password):
        # Stop the access point
        subprocess.run(["sudo", "systemctl", "stop", "hostapd"])

        # Update wpa_supplicant.conf with WiFi credentials
        wpa_config = f"network={{\n    ssid=\"{ssid}\"\n    psk=\"{password}\"\n}}"
        with open(WiFiConfigurator.WPA_SUPPLICANT_FILE, "w") as wpa_file:
            wpa_file.write(wpa_config)

        # Enable WiFi client mode
        subprocess.run(["sudo", "systemctl", "start", "wpa_supplicant"])

    @staticmethod
    def restart_pi():
        subprocess.run(["sudo", "reboot"])
