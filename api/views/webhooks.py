from django.conf import settings
import stripe
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from api.models import Payment, Company, User
import datetime
import paypalrestsdk

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        intent = event['data']['object']

    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        payload = json.loads(payload)
        subscription_id = payload['data']['object']['subscription']

        # Now you can retrieve the subscription
        subscription = stripe.Subscription.retrieve(subscription_id)
        price_id = subscription['plan']['id']
        plan = settings.STRIPE_PRICES[price_id]
        # Get the start and end of the current billing period
        current_period_start = subscription['current_period_start']
        current_period_end = subscription['current_period_end']

        # These are Unix timestamps, so you might want to convert them to a more readable format
        current_period_start = datetime.datetime.fromtimestamp(current_period_start)
        current_period_end = datetime.datetime.fromtimestamp(current_period_end)
        company_id = payload['data']['object']['metadata']['company_id']

        company = Company.objects.get(id=company_id)
        company.subscription_ends = current_period_end
        company.plan = plan
        company.subscription_renewal = True
        company.save()
        Payment.objects.create(
            payment_intent_id=payload['id'],
            subscription_id=subscription_id,
            company=company,
            status=Payment.PAYED,
            plan=plan
        )



    else:
        return HttpResponse(status=200)

    return HttpResponse(status=200)


@csrf_exempt
def paypal_webhook(request):
    try:
        # print(request.META)
        auth_algo = request.META['HTTP_PAYPAL_AUTH_ALGO']
        cert_url = request.META['HTTP_PAYPAL_CERT_URL']
        transmission_id = request.META['HTTP_PAYPAL_TRANSMISSION_ID']
        transmission_sig = request.META['HTTP_PAYPAL_TRANSMISSION_SIG']
        transmission_time = request.META['HTTP_PAYPAL_TRANSMISSION_TIME']
        webhook_id = settings.PAYPAL_WEBHOOK_ID

        event_body = request.body.decode(request.encoding or "utf-8")

        valid = paypalrestsdk.notifications.WebhookEvent.verify(
            transmission_id=transmission_id,
            timestamp=transmission_time,
            webhook_id=webhook_id,
            event_body=event_body,
            cert_url=cert_url,
            actual_sig=transmission_sig,
            auth_algo=auth_algo,
        )

        if not valid:
            return HttpResponse(status=400)

        webhook_event = json.loads(event_body)

        event_type = webhook_event["event_type"]
        print(event_type)
        print(webhook_event)
        # payment completed
        if event_type == "BILLING.SUBSCRIPTION.ACTIVATED":
            payment = Payment.objects.get(payment_intent_id=webhook_event['resource']['id'])
            current_period_end = webhook_event['resource']['billing_info']['next_billing_time']
            payment.company.subscription_ends = datetime.datetime.strptime(current_period_end, "%Y-%m-%dT%H:%M:%SZ")
            payment.company.plan = payment.plan
            payment.company.save()

            payment.status = Payment.PAYED
            payment.save()


            # subscription = Subscriptions.objects.filter(subscriptionID=subscription_id).last()
            # if subscription:
            #     subscription.active = True
            #     subscription.active_billing = True
            #     subscription.next_billing_date = webhook_event['resource']['billing_info']['next_billing_time'][:10]
            #
            #     subscription.save()

        # # subscription cancelled
        # if event_type == "BILLING.SUBSCRIPTION.CANCELLED":
        #     subscription_id = webhook_event['resource']['id']
        #     subscription = Subscriptions.objects.filter(subscriptionID=subscription_id).last()
        #     if subscription:
        #         subscription.active_billing = False
        #         subscription.save()
        #
        # # subscription failed
        # if event_type == "BILLING.SUBSCRIPTION.PAYMENT.FAILED":
        #     subscription_id = webhook_event['resource']['id']
        #     subscription = Subscriptions.objects.filter(subscriptionID=subscription_id).last()
        #     if subscription:
        #         subscription.active = False
        #         subscription.active_billing = False
        #         subscription.save()
        #
        #         PaymentMethods.resub_free(subscription.user)

        return HttpResponse({"success": True}, status=200)

    except Exception as e:
        return HttpResponse({"error": e}, status=500)
