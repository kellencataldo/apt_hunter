import smtplib
# from email.mime.multipart import MIMEMultipart
import email
import SETTINGS


def send_emails(email_blob, email_str):
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(SETTINGS.EMAIL_ADDRESS, SETTINGS.EMAIL_PASSWORD)
    for name, address in email_blob.items():
        message = email.mime.multipart.MIMEMultipart()
        message['From'] = SETTINGS.EMAIL_ADDRESS
        message['To'] = address
        message['Subject'] = 'crawl result'
        formatted_email = f'Hello {name} here are the matches:\n\n{email_str}'
        email_body = email.mime.text.MIMEText(formatted_email, 'plain')
        message.attach(email_body)
        server.sendmail(SETTINGS.EMAIL_ADDRESS, address, "this message is from python")
    server.quit()
