import smtplib
from email.mime.text import MIMEText

SENDER_EMAIL = "momdad.775533@gmail.com"
APP_PASSWORD = "kpqr rcfn jmaa dhws"

RECEIVER_EMAIL = "momdad.775533@gmail.com"

def send_alert(
    transaction_id,
    amount,
    fraud_probability
):

    subject = "FRAUD ALERT"

    body = f"""
Fraud Transaction Detected

Transaction ID : {transaction_id}

Amount : {amount}

Fraud Probability : {fraud_probability}
"""

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    server = smtplib.SMTP(
        "smtp.gmail.com",
        587
    )

    server.starttls()

    server.login(
        SENDER_EMAIL,
        APP_PASSWORD
    )

    server.sendmail(
        SENDER_EMAIL,
        RECEIVER_EMAIL,
        msg.as_string()
    )

    server.quit()

    print(
        "EMAIL ALERT SENT"
    )