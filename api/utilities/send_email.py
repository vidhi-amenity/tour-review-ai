from tour_reviews_ai.settings import EMAIL_HOST_USER
from django.core.mail import EmailMessage
from datetime import date, timedelta


def send(subject, message, email_addresses, attachment=None):

    msg = EmailMessage(subject,
                       message,
                       EMAIL_HOST_USER,
                       email_addresses)
    print(email_addresses)
    msg.content_subtype = "html"

    if attachment:
        msg.attach_file(attachment)
    msg.send()
    print('sent')

