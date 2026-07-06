from email_alert import send_alert

send_alert(
    transaction_id="TXN001",
    amount=50000,
    fraud_probability=98.5
)   