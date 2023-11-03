from rest_framework.views import APIView
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import paypalrestsdk
from django.http.response import JsonResponse
from api.serializers import CreateCheckoutSessionSerializer
from api.models import Payment, Company
import requests
import json

@csrf_exempt
def paypal_config(request):
    if request.method == 'GET':
        paypal_config = {
            'client_id': settings.PAYPAL_CLIENT_ID,
            'client_secret': settings.PAYPAL_CLIENT_SECRET
        }
        return JsonResponse(paypal_config)


class CreateCheckoutSessionView(APIView):
    def post(self, request):

        serializer = CreateCheckoutSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        test = False
        if 'test' in serializer.data:
            if serializer.data['test']:
                test = True
                if 'success_url' not in serializer.data or 'cancel_url' not in serializer.data:
                    return JsonResponse({'error': 'Please provide a success_url and a cancel_url'})

        # To create product for sandbox you need to use endpoints, see readme here in views
        if serializer.data['plan'] == 'SMALL':
            price = settings.PAYPAL_SMALL_PRICE_ID
        elif serializer.data['plan'] == 'MEDIUM':
            price = settings.PAYPAL_MEDIUM_PRICE_ID
        elif serializer.data['plan'] == 'LARGE':
            price = settings.PAYPAL_LARGE_PRICE_ID

        try:
            success_url = settings.STRIPE_SUCCESS_URL
            cancel_url = settings.STRIPE_CANCEL_URL
            if test:
                success_url = serializer.data['success_url']
                cancel_url = serializer.data['cancel_url']
            companies = Company.objects.filter(related_users=self.request.user)
            if companies.exists():
                company = companies.first()
            else:
                return JsonResponse({'error': 'No company'})

            auth_response = requests.post('https://api.sandbox.paypal.com/v1/oauth2/token',
                                          auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
                                          headers={'Accept': 'application/json', 'Accept-Language': 'en_US'},
                                          data={'grant_type': 'client_credentials'})
            access_token = auth_response.json()['access_token']

            # Crea una nuova sottoscrizione
            subscription_data = {
                'plan_id': price,
                'subscriber': {
                    'email_address': request.user.email
                },
                'auto_renewal': True,
                'application_context': {
                    'return_url': success_url,
                    'cancel_url': cancel_url
                }
            }

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }

            response = requests.post('https://api.sandbox.paypal.com/v1/billing/subscriptions',
                                     headers=headers,
                                     data=json.dumps(subscription_data))

            if response.status_code == 201:
                plan = settings.PAYPAL_PRICES[price]
                Payment.objects.create(
                    payment_intent_id=response.json()['id'],
                    company=company,
                    status=Payment.PENDING,
                    plan=plan
                )
                return JsonResponse({
                    'sessionId': response.json()['id'],
                    'url': response.json()['links'][0]['href']
                })
            else:
                return JsonResponse({'error': 'Non è stato possibile creare la sottoscrizione'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)})