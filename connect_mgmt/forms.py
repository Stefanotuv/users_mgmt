from django import forms

class WiFiForm(forms.Form):
    MODE_CHOICES = [
        ('wifi', 'WiFi'),
        ('ap', 'Access Point'),
    ]

    mode = forms.ChoiceField(label='Select Mode', choices=MODE_CHOICES, required=True)
    ssid = forms.ChoiceField(label='Select WiFi Network', choices=[], required=True)
    password = forms.CharField(label='WiFi Password', widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        network_choices = kwargs.pop('network_choices', [])
        super(WiFiForm, self).__init__(*args, **kwargs)
        self.fields['ssid'].choices = network_choices

