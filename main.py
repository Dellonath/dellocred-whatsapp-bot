import argparse
import datetime
from models import agendor, zapi

parser = argparse.ArgumentParser(description='Script to collect people information data from Agendor API and send messages via ZAPI')
parser.add_argument('--datetime', type=str, default=datetime.datetime.now().strftime('%Y-%m-%dT00:00:00Z'))
parser.add_argument('--category', type=str, default='Cliente em potencial')
args = parser.parse_args()

agendor_api = agendor.AgendorAPI()
people_data = agendor_api.get_people_stream(since=args.datetime, category=args.category)

chatbot = zapi.ZAPIChatbot()
chatbot_message = 'Hello, this is a test message from the chatbot.'
for person in people_data:
    response = chatbot.send_message(phone=person.get('phone'), message=chatbot_message)