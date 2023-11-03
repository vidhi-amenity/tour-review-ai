from rest_framework.views import APIView
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.http.response import JsonResponse
from api.serializers import CreateCheckoutSessionSerializer
from api.models import Payment, Company


@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'public_key': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


class CreateCheckoutSessionView(APIView):
    def post(self, request):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        serializer = CreateCheckoutSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        test = False
        if 'test' in serializer.data:
            if serializer.data['test']:
                test = True
                if 'success_url' not in serializer.data or 'cancel_url' not in serializer.data:
                    return JsonResponse({'error': 'Please provide a success_url and a cancel_url'})

        if serializer.data['plan'] == 'SMALL':
            price = settings.STRIPE_SMALL_PRICE_ID
        elif serializer.data['plan'] == 'MEDIUM':
            price = settings.STRIPE_MEDIUM_PRICE_ID
        elif serializer.data['plan'] == 'LARGE':
            price = settings.STRIPE_LARGE_PRICE_ID

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

            checkout_session = stripe.checkout.Session.create(
                client_reference_id=self.request.user.id,
                customer_email=self.request.user.email,
                success_url=success_url,
                cancel_url=cancel_url,
                payment_method_types=['card'],
                mode='subscription',
                metadata={'company_id': company.id},
                line_items=[
                    {
                        'price': price,
                        'quantity': 1
                    }
                ],
            )

            return JsonResponse({
                'sessionId': checkout_session['id'],
                'url': checkout_session['url']
            })
        except Exception as e:
            return JsonResponse({'error': str(e)})


class DeleteSubscriptionView(APIView):
    def post(self, request):
        companies = Company.objects.filter(related_users=self.request.user)
        if companies.exists():
            company = companies.first()
        else:
            return JsonResponse({'error': 'No company'})
        try:
            payment = Payment.objects.filter(company=company).last()

            if payment.payment_intent_id.startswith('evt_'):
                # Stripe
                if not payment.subscription_id:
                    return JsonResponse({'error': 'No active subscription found.'}, status=400)

                stripe.api_key = settings.STRIPE_SECRET_KEY
                stripe.Subscription.delete(payment.subscription_id)

            else:
                # Paypal
                pass

            # Sets the subscription renewal to false
            company.subscription_renewal = False
            company.save()

            return JsonResponse({'status': 'Subscription cancelled successfully.'})
        except Payment.DoesNotExist:
            return JsonResponse({'error': 'Payment not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class UpgradeSubscriptionView(APIView):
    def post(self, request):
        # Recupero la compagnia dell'utente corrente.
        companies = Company.objects.filter(related_users=self.request.user)
        if not companies.exists():
            return JsonResponse({'error': 'No company'})
        company = companies.first()

        # Recupero la sottoscrizione corrente.
        payment = Payment.objects.filter(company=company).last()
        if not payment.subscription_id:
            return JsonResponse({'error': 'No active subscription found.'}, status=400)

        # Identifica il nuovo piano dall'input dell'utente.
        plan = request.data.get('plan')
        if plan == 'SMALL':
            price = settings.STRIPE_SMALL_PRICE_ID
        elif plan == 'MEDIUM':
            price = settings.STRIPE_MEDIUM_PRICE_ID
        elif plan == 'LARGE':
            price = settings.STRIPE_LARGE_PRICE_ID
        else:
            return JsonResponse({'error': 'Invalid plan provided.'}, status=400)

        try:
            if payment.payment_intent_id.startswith('evt_'):
                # Stripe
                stripe.api_key = settings.STRIPE_SECRET_KEY
                subscription = stripe.Subscription.retrieve(payment.subscription_id)
                subscription_item_id = subscription['items']['data'][0]['id']
                stripe.Subscription.modify(
                    payment.subscription_id,
                    items=[{
                        'id': subscription_item_id,
                        'price': price,
                    }]
                )

            else:
                # Paypal
                pass

            if plan == 'SMALL':
                company.plan = settings.SMALL
            elif plan == 'MEDIUM':
                company.plan = settings.MEDIUM
            elif plan == 'LARGE':
                company.plan = settings.LARGE
            company.save()

            return JsonResponse({'status': 'Subscription upgraded successfully.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
