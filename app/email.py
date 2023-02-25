import sendgrid
from sendgrid.helpers.mail import Mail, Email, To
from flask import current_app, render_template, flash
from flask_login import current_user


def send_email(to, subject, template, multiple=False, **kwargs):
    """Send mail to an email address."""
    # Render the verify_admin template into a string
    message = render_template(f'{template}.html', **kwargs)
    # create a To object (recipient)
    recipient = To(
        email=Email(to),
        name=current_user.username
    )
    # create a sendgrid Mail object and populate dynamically
    message = Mail(
        from_email=Email(current_app.config['SENDGRID_EMAIL']),
        to_emails=recipient,
        subject=subject,
        html_content=message,
        is_multiple=multiple
    )
    # create our sendgrid object and return our response object
    try:
        sg = sendgrid.SendGridAPIClient(current_app.config['SENDGRID_API_KEY'])
        response = sg.send(message)
        if response.status_code == 202:
            flash('A confirmation email has been sent to you via email.')
    except Exception as e:
        flash(e.__str__, 'error')
