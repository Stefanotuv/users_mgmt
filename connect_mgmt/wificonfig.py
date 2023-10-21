# sudo chmod 777 /etc/wpa_supplicant/wpa_supplicant.conf
# sudo chmod 777 /etc/network_mode.conf
# sudo chmod 777 /etc/hostapd/hostapd.conf

# wificonfig.py
import subprocess
import os
import datetime

class WiFiConfigurator:
    WPA_SUPPLICANT_FILE = "/etc/wpa_supplicant/wpa_supplicant.conf"
    HOSTAPD_CONF_FILE = "/etc/hostapd/hostapd.conf"
    NETWORK_MODE_FILE = "/etc/network_mode.conf"
    LOG_FILE = "/home/stefano/log_pi.txt"  # Update this path

    @classmethod
    def log(cls,message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.LOG_FILE, "a") as log_file:
            log_file.write(f"{timestamp} - {message}\n")
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

    @classmethod
    def write_network_mode(cls, mode):
        with open(cls.NETWORK_MODE_FILE, "w") as mode_file:
            mode_file.write(mode)

    @staticmethod
    def switch_to_ap_mode(ap_ssid, ap_password):
        current_mode = WiFiConfigurator.get_current_mode()
        WiFiConfigurator.log("wificonfig -> switch_to_ap_mode")
        if current_mode == "ap":
            # Disable AP mode
            WiFiConfigurator.log("wificonfig -> current mode ap")
            subprocess.run(["sudo", "systemctl", "stop", "hostapd"])

        else:
            # Disable WiFi client mode
            WiFiConfigurator.log("wificonfig -> current mode wifi")
            subprocess.run(["sudo", "systemctl", "stop", "wpa_supplicant"])

        # Start the access point
        subprocess.run(["sudo", "systemctl", "start", "hostapd"])
        # Update hostapd.conf with new AP SSID and password
        if (ap_ssid == "" or ap_ssid == None):
            ap_ssid = "pi_zero"
        if (ap_password == "" or ap_password == None):
            ap_password = "pi_zer0!"
        hostapd_config = (f"#Set wireless interface\n" \
                          f"interface=wlan0\n" \
                          f"#driver\n"
                          f"driver=nl80211\n"
                          f"hw_mode=g\n"
                          f"channel=6\n"
                          f"ieee80211n=1\n"
                          f"wmm_enabled=0\n"
                          f"macaddr_acl=0\n"
                          f"ignore_broadcast_ssid=0\n"
                          f"auth_algs=1\n"
                          f"wpa=2\n"
                          f"wpa_key_mgmt=WPA-PSK\n"
                          f"wpa_pairwise=TKIP\n"
                          f"rsn_pairwise=CCMP\n"
                          f"#Set network name\n" \
                          f"ssid={ap_ssid}\nwpa_passphrase={ap_password}\n")

        with open(WiFiConfigurator.HOSTAPD_CONF_FILE, "w") as hostapd_file:
            hostapd_file.write(hostapd_config)

        WiFiConfigurator.log("wificonfig -> modified hostapd_config")

        # Write the network mode to the configuration file
        WiFiConfigurator.write_network_mode("ap")

    @staticmethod
    def switch_to_wifi_mode(ssid, password):
        current_mode = WiFiConfigurator.get_current_mode()
        WiFiConfigurator.log("wificonfig -> switch_to_wifi_mode")
        if current_mode == "ap":
            # Disable AP mode
            WiFiConfigurator.log("wificonfig ->  current mode ap")
            subprocess.run(["sudo", "systemctl", "stop", "hostapd"])
        else:
            # Disable WiFi client mode
            WiFiConfigurator.log("wificonfig ->  current mode wifi")
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
                WiFiConfigurator.log("wificonfig ->  wpa_file.write(wpa_config)")
                pass
        except Exception as e:
            print("Error:", e)
            WiFiConfigurator.log("wificonfig -> " + e)
            print("Current working directory:", os.getcwd())
            print("File path:", WiFiConfigurator.WPA_SUPPLICANT_FILE)

        # Write the network mode to the configuration file
        WiFiConfigurator.write_network_mode("wifi")

        subprocess.run(["sudo", "systemctl", "start", "wpa_supplicant"])

    @staticmethod
    def restart_pi():
        subprocess.run(["sudo", "reboot"])
