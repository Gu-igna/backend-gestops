from .. import mailsender
from flask import current_app, render_template
from flask_mail import Message
from smtplib import SMTPException
import logging

def sendMail(to, subject, template, **kwargs):
    
    if not to or not subject or not template:
        raise ValueError("Parameters 'to', 'subject', and 'template' cannot be empty.")
    
    msg = Message(subject, sender=current_app.config['FLASKY_MAIL_SENDER'], recipients=to)
  
    try:
        msg.body = render_template(template + '.txt', **kwargs)
        msg.html = render_template(template + '.html', **kwargs)
        mailsender.send(msg)
    except SMTPException as e:
        logging.error(f"Mail delivery failed: {str(e)}")
        return "El envío del correo falló"
    return True