Create products paypal
____



```commandline
import requests
import base64

# Le tue credenziali da PayPal
client_id = settings.PAYPAL_CLIENT_ID
client_secret = settings.PAYPAL_CLIENT_SECRET

# Crea una stringa con le tue credenziali formattate come 'client_id:client_secret'
credentials = f'{client_id}:{client_secret}'

# Codifica le tue credenziali in base64
credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

headers = {
    'Authorization': f'Basic {credentials}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# URL per ottenere il token di accesso (sandbox)
url = 'https://api.sandbox.paypal.com/v1/oauth2/token'

# Parametri per la richiesta del token di accesso
params = {
    'grant_type': 'client_credentials'
}

response = requests.post(url, headers=headers, params=params)

# Il token di accesso è incluso nella risposta JSON
access_token = response.json()['access_token']

```


______
```commandline
import requests
import json

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {access_token}'  # sostituisci con il tuo access token
}

url = 'https://api.sandbox.paypal.com/v1/catalogs/products'
body = {
    'name': 'Packages',
    'description': 'packages',
    'type': 'SERVICE',
    'category': 'SOFTWARE'
}

response = requests.post(url, headers=headers, data=json.dumps(body))
product_id = response.json()['id']
print(product_id)
```


____

```commandline
import requests
import json
url = 'https://api.sandbox.paypal.com/v1/billing/plans'
body = {
    'product_id': product_id,
    'name': 'Nome del Piano di Sottoscrizione',
    'description': 'Descrizione del Piano di Sottoscrizione',
    'status': 'ACTIVE',
    'billing_cycles': [
        {
            'frequency': {
                'interval_unit': 'MONTH',  # oppure 'YEAR' per il piano annuale
                'interval_count': 1  # oppure 12 per il piano annuale
            },
            'tenure_type': 'REGULAR',
            'sequence': 1,
            'total_cycles': 0,
            'pricing_scheme': {
                'fixed_price': {
                    'value': '10',  # oppure '100' per il piano annuale
                    'currency_code': 'USD'
                }
            }
        }
    ],
    'payment_preferences': {
        'auto_bill_outstanding': True,
        'setup_fee': {
            'value': '0',
            'currency_code': 'USD'
        },
        'setup_fee_failure_action': 'CONTINUE',
        'payment_failure_threshold': 3
    },
    'taxes': {
        'percentage': '0',
        'inclusive': False
    }
}
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {access_token}'  # sostituisci con il tuo access token
}
response = requests.post(url, headers=headers, data=json.dumps(body))
plan_id = response.json()['id']

```