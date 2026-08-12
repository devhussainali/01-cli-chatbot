
import smtplib, os
from dotenv import load_dotenv
load_dotenv()

email = os.getenv('SENDER_EMAIL')
pwd = os.getenv('SENDER_APP_PASSWORD')

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email, pwd)
    print('LOGIN SUCCESSFUL')
    server.quit()
except Exception as e:
    print('LOGIN FAILED')
    print(e)
