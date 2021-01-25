import threading
from django.core.mail import send_mail
from django.conf import settings


class SendMail(threading.Thread):
    def __init__(self, subject, text, email=[], fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            self.subject,
            self.text,
            settings.DEFAULT_FROM_EMAIL,
            self.email,
            fail_silently=self.fail_silently
        )
