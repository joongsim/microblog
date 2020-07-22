from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
from app import mail


def send_async_email(app, msg):
    # app_context() gives access to application instance
    # b/c need to access config
    with app.app_context():
        mail.send(msg)


# current_app is context-dependent and tied to the thread running the client request
# Background thread wouldn't have value assigned to current_app, so can't pass directly
# to send_async_email
# Can't directly pass to Thread either since current_app is dynamically mapped
# to application instance
# Need to access real application instance (NOT proxy) using _get_current_object
# and pass to thread as argument
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()
