import os
import string
import random
import time
import json
from dataclasses import dataclass, field
from dotenv import load_dotenv
from models.wapi import WAPI
from models.flow import FlowActionType

load_dotenv()

@dataclass
class Instance:
    id: int
    active: bool
    mature: bool
    name: str
    phone: str
    instance_id: int
    instance_token: int
    block_instances_ids: list[str] = field(default_factory=list)
    sender: list[str] = field(default=True)

DELAY_BETWEEN_INTERACTIONS: int = random.randint(30, 60)
NUMBER_OF_INTERACTIONS: int = 300
with open(f'configs/instances.json', 'r') as f:
    INSTANCES: list[Instance] = [
        Instance(**instance) for instance in json.load(f)
        if instance.get('mature') 
    ]
   
ACTIONS: list[dict] = [
    {
        'type': FlowActionType.SEND_MESSAGE,
        'prob': 0.7
    },
    {
        'type': FlowActionType.SEND_AUDIO,
        'prob': 0.25
    },
    {
        'type': FlowActionType.SEND_IMAGE,
        'prob': 0.05
    }
]

AUDIOS: list[str] = [
    'https://res.cloudinary.com/dg0nvnjqw/video/upload/v1767726360/tagarela_4_secs_clapku.ogg',
    'https://res.cloudinary.com/dg0nvnjqw/video/upload/v1767726359/tagarela_5_secs_cyhygd.ogg',
    'https://res.cloudinary.com/dg0nvnjqw/video/upload/v1767726358/tagarela_6_secs_ejuglr.ogg',
    'https://res.cloudinary.com/dg0nvnjqw/video/upload/v1767726358/tagarela_7_secs_wmakxo.ogg',
    'https://res.cloudinary.com/dg0nvnjqw/video/upload/v1767726358/tagarela_8_secs_bxyamk.ogg',
    'https://res.cloudinary.com/dg0nvnjqw/video/upload/v1767726358/tagarela_9_secs_smegzs.ogg',
    'https://res.cloudinary.com/dg0nvnjqw/video/upload/v1767726358/tagarela_10_secs_lryspe.ogg',
    'https://res.cloudinary.com/dg0nvnjqw/video/upload/v1767726358/tagarela_11_secs_b1poes.ogg',
    'https://res.cloudinary.com/dg0nvnjqw/video/upload/v1767726357/tagarela_12_secs_oapknw.ogg',
    'https://res.cloudinary.com/dg0nvnjqw/video/upload/v1767726357/tagarela_13_secs_ed554e.ogg',
    'https://res.cloudinary.com/dg0nvnjqw/video/upload/v1767726357/tagarela_14_secs_nxpcxn.ogg',
    'https://res.cloudinary.com/dg0nvnjqw/video/upload/v1767726218/tagarela_15_secs_bd0qoz.ogg'
]

IMAGES: list[str] = [
    'https://res.cloudinary.com/dg0nvnjqw/image/upload/v1764680916/main-sample.png',
    'https://res.cloudinary.com/dg0nvnjqw/image/upload/v1764680916/cld-sample-5.jpg',
    'https://res.cloudinary.com/dg0nvnjqw/image/upload/v1764680915/cld-sample-4.jpg',
    'https://res.cloudinary.com/dg0nvnjqw/image/upload/v1764680915/cld-sample-3.jpg',
    'https://res.cloudinary.com/dg0nvnjqw/image/upload/v1764680914/cld-sample.jpg',
    'https://res.cloudinary.com/dg0nvnjqw/image/upload/v1764680915/cld-sample-2.jpg',
    'https://res.cloudinary.com/dg0nvnjqw/image/upload/v1764680914/samples/waves.png',
]

def generate_random_text(chars=string.ascii_lowercase + string.ascii_uppercase + string.digits + '!?-.'):
    number_of_words: int = random.randint(2, 10)
    size_of_word: int = random.randint(2, 10)
    text: list = []
    for _ in range(number_of_words):
        text.append(''.join(random.choices(chars, k=size_of_word)))
    return ' '.join(text)

last_sender_id: int = None
messages_received: list = []
for _ in range(NUMBER_OF_INTERACTIONS):

    sender_instance: Instance = random.choice(
        seq=[instance for instance in INSTANCES if instance.sender]
    )

    receiver_instances: list[Instance] = [
        instance for instance in INSTANCES 
        if instance.id != sender_instance.id
        and instance.id not in sender_instance.block_instances_ids
    ]

    receiver_instances: list[Instance] = random.sample(
        population=receiver_instances, 
        k=random.randint(1, 2)
    )
    w_api: WAPI = WAPI(
        instance_id=os.getenv(sender_instance.instance_id),
        instance_token=os.getenv(sender_instance.instance_token),
    )

    for receiver_instance in receiver_instances:
        number_of_random_actions: int = random.randint(1, 3)
        print(
            f'Interaction started ' 
            f'from {sender_instance.name} ({sender_instance.phone}) '
            f'to {receiver_instance.name} ({receiver_instance.phone}) '
            f'({number_of_random_actions} actions):'
        )
        for _ in range(number_of_random_actions):
            action: FlowActionType = random.choices(
                population=[action['type'] for action in ACTIONS],
                weights=[action['prob'] for action in ACTIONS],
            )[0]

            delay: int = random.randint(1, 15)

            print(f'-- sending {action}, waiting for {delay} seconds...')

            message_id: str = None
            if random.random() <= 0.3:
                valid_messages: list = [
                    msg for msg in messages_received 
                    if msg['phone_sender'] == receiver_instance.phone 
                    and msg['phone_receiver'] == sender_instance.phone
                ]
                if valid_messages:
                    chosen_message: dict = valid_messages.pop()
                    message_id: str = chosen_message.get('message_id')
                    messages_received.remove(chosen_message)

            if action == FlowActionType.SEND_MESSAGE:
                request: dict = w_api.send_message(
                    phone=receiver_instance.phone,
                    message=generate_random_text(),
                    delay=delay,
                    message_id=message_id if message_id else None
                )

            elif action == FlowActionType.SEND_AUDIO:
                request: dict = w_api.send_audio(
                    phone=receiver_instance.phone,
                    audio_url=random.choice(AUDIOS),
                    delay=delay,
                    message_id=message_id if message_id else None
                )

            elif action == FlowActionType.SEND_IMAGE:
                request: dict = w_api.send_image(
                    phone=receiver_instance.phone,
                    image_url=random.choice(IMAGES),
                    delay=delay,
                    message_id=message_id if message_id else None
                )

            messages_received.append({
                'phone_sender': sender_instance.phone,
                'phone_receiver': receiver_instance.phone,
                'message_id': request.get('messageId')
            })

            time.sleep(delay)

    time.sleep(DELAY_BETWEEN_INTERACTIONS)
    
