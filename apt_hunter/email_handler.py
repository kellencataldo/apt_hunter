import smtplib
import email.mime.multipart
import email.mime.text

import SECRETS


def send_emails(email_blob, email_str, start_time):
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(SECRETS.EMAIL_ADDRESS, SECRETS.EMAIL_PASSWORD)
    for name, address in email_blob.items():
        message = email.mime.multipart.MIMEMultipart()
        message['From'] = SECRETS.EMAIL_ADDRESS
        message['To'] = address
        message['Subject'] = f'crawl result for {start_time.strftime("%Y-%m-%d")}'
        message['Reply-to'] = SECRETS.EMAIL_ADDRESS
        formatted_email = f'Hello {name} here are the matches:\n\n{email_str}'
        email_body = email.mime.text.MIMEText(formatted_email, 'plain')
        message.attach(email_body)
        server.sendmail(SECRETS.EMAIL_ADDRESS, address, message.as_string())
    server.quit()
