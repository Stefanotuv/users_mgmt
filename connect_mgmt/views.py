from django.shortcuts import render
from .forms import WiFiForm  # Replace with your form
from .wificonfig import WiFiConfigurator
import subprocess
import re



def wifi_config_view(request):
    if request.method == 'POST':
        if request.POST['ap_wifi'] == 'ap':
            ap_ssid = request.POST['ap_ssid']
            ap_password = request.POST['ap_password']
            wifi_configurator = WiFiConfigurator()
            wifi_configurator.switch_to_ap_mode(ap_ssid, ap_password)
            wifi_configurator.restart_pi()
            pass
        elif request.POST['ap_wifi'] == 'wifi':
            wifi_ssid = request.POST['wifi_ssid']
            wifi_password = request.POST['wifi_password']
            wifi_configurator = WiFiConfigurator()
            wifi_configurator.switch_to_wifi_mode(wifi_ssid, wifi_password)
            wifi_configurator.restart_pi()
            pass
        pass

        return render(request, 'connect_mgmt/wifi_config.html')

    else:
        wifi_configurator = WiFiConfigurator()

        # Scan for available WiFi networks
        scan_output = subprocess.run(["sudo", "iwlist", "wlan0", "scan"], capture_output=True, text=True)
        networks = re.findall(r"ESSID:\"(.+)\"", scan_output.stdout)

        # Populate the form with scan results
        network_choices = [network for network in networks]
        initial_data = {'ssid': '', 'password': ''}

    return render(request, 'connect_mgmt/wifi_config.html', {'initial_data':initial_data,'network_choices':network_choices })

