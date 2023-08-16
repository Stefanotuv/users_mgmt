from django.shortcuts import render
from .forms import WiFiForm  # Replace with your form
from .wificonfig import WiFiConfigurator
import subprocess
import re



def wifi_config_view(request):
    if request.method == 'POST':
        form = WiFiForm(request.POST)
        if form.is_valid():
            ssid = form.cleaned_data['ssid']
            password = form.cleaned_data['password']

            wifi_configurator = WiFiConfigurator()
            wifi_configurator.switch_to_wifi_mode(ssid, password)
            wifi_configurator.restart_pi()

    else:
        wifi_configurator = WiFiConfigurator()

        # Scan for available WiFi networks
        scan_output = subprocess.run(["sudo", "iwlist", "wlan0", "scan"], capture_output=True, text=True)
        networks = re.findall(r"ESSID:\"(.+)\"", scan_output.stdout)

        # Populate the form with scan results
        network_choices = [(network, network) for network in networks]
        initial_data = {'ssid': '', 'password': ''}
        form = WiFiForm(initial=initial_data, network_choices=network_choices)

    return render(request, 'connect_mgmt/wifi_config.html', {'form': form})

