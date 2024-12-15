import smtplib
from email.mime.text import MIMEText

def send_email_with_sendgrid(email, security_key):
    sender_email = "tucorreo@tudominio.com"
    sendgrid_password = "API_KEY_DE_SENDGRID"  # Genera en tu cuenta SendGrid
    subject = "Llave de Seguridad - Portal de Vinos"
    body = f"Hola,\n\nTu llave de seguridad es: {security_key}\n\nGracias por registrarte."

    msg = MIMEText(body)
    msg["From"] = sender_email
    msg["To"] = email
    msg["Subject"] = subject

    try:
        with smtplib.SMTP("smtp.sendgrid.net", 587) as server:
            server.starttls()
            server.login("apikey", sendgrid_password)  # Usuario fijo: "apikey"
            server.sendmail(sender_email, email, msg.as_string())
            print(f"Correo enviado a {email}")
    except Exception as e:
        print(f"Error al enviar correo con SendGrid: {e}")
