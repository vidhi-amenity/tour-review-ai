from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
import stripe


class HelloView(APIView):

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)


class ExampleSuccessView(APIView):

    def get(self, request):
        content = {'message': 'Payment successful!'}
        return Response(content)

class ExampleCancelView(APIView):

    def get(self, request):
        content = {'message': 'Payment cancelled!'}
        return Response(content)


class CostsView(APIView):

    def get(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        content = {
            "plans": {
                'SMALL': str(stripe.Price.retrieve(settings.STRIPE_SMALL_PRICE_ID)['unit_amount']),
                'MEDIUM': str(stripe.Price.retrieve(settings.STRIPE_MEDIUM_PRICE_ID)['unit_amount']),
                'LARGE': str(stripe.Price.retrieve(settings.STRIPE_LARGE_PRICE_ID)['unit_amount']),
            }
        }
        return Response(content)

