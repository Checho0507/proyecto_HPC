import pika
import smtplib
from email.mime.text import MIMEText
from sender import password

# Función para enviar un correo con la llave de seguridad
def send_email(email, security_key):
    sender_email = "genetica.vinos@gmail.com"
    sender_password = password  # Sustituye con la contraseña generada
    subject = "Llave de Seguridad - Portal de Vinos"
    body = f"Hola,\n\nTu llave de seguridad es: {security_key}\n\nGracias por registrarte."

    msg = MIMEText(body, _charset='utf-8')  # Aseguramos que el mensaje esté en UTF-8
    msg["From"] = sender_email
    msg["To"] = email
    msg["Subject"] = subject

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            # Aseguramos que la contraseña esté en formato UTF-8
            server.login(sender_email, sender_password)  # Codificar en UTF-8
            server.sendmail(sender_email, email, msg.as_string())
            print(f"Correo enviado a {email}")
    except smtplib.SMTPException as e:
        print(f"Error al enviar correo: {e}")
        
# Configuración de RabbitMQ
def consume_messages():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='user_registration')  # Asegura que la cola existe

    # Callback para procesar los mensajes
    def callback(ch, method, properties, body):
        message = eval(body.decode())  # Convierte el mensaje a un diccionario
        email = message.get("email")
        security_key = message.get("security_key")
        send_email(email, security_key)

    channel.basic_consume(queue='user_registration', on_message_callback=callback, auto_ack=True)
    print("Esperando mensajes...")
    channel.start_consuming()

# Función para publicar el mensaje en RabbitMQ
def publish_message(email, security_key):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='user_registration')  # Declara la cola si no existe
    message = {"email": email, "security_key": security_key}
    channel.basic_publish(exchange='', routing_key='user_registration', body=str(message))
    connection.close()