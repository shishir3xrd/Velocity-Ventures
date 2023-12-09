from flask import render_template
from flask_mail import Message

def get_discount_price(price, discount):
    return price - (price*(discount/100))


def send_verification_email(mail, user, token):
    subject = "Two-Step Verification for Your Account" #changed 
    recipient = user['email'] 

    # Render the email body using a template
    body = render_template(
        "verification_email.html",
        user_email=recipient,
        token=token,
        user=user
    )
    # Create the email message
    message = Message(subject=subject, recipients=[recipient], html=body)

    # Send the email
    mail.send(message)

def send_servicing_email(mail, user, status, chasis_no):
    subject = "Servicing Request Confirmation"
    recipient = user['email']

    # Render the email body using a template
    body = render_template(
        "servicing_email.html",
        user_email=recipient,
        status=status,
        user=user,
        chasis_no=chasis_no,
    )

    # Create the email message
    message = Message(subject=subject, recipients=[recipient], html=body)

    # Send the email
    mail.send(message)