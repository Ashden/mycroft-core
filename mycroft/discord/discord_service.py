import discord
import os
import asyncio
import threading
from dotenv import load_dotenv
from mycroft.configuration import Configuration
from mycroft.messagebus import Message
from mycroft.util.log import LOG

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

token = os.getenv("DISCORD_TOKEN")
client = discord.Client()


async def start():
    await client.start(os.getenv('DISCORD_TOKEN'))


def run_it_forever(loop):
    loop.run_forever()


def init(messagebus):
    """Start discord related handlers.

    Arguments:
        messagebus: Connection to the Mycroft messagebus
    """

    global bus
    global config

    # Saving a reference to the message bus and listening for speak
    bus = messagebus
    bus.on('speak', handle_speak)

    # Get configuration
    Configuration.set_config_update_handlers(bus)
    config = Configuration.get()

    # Start event loop task for discord
    asyncio.get_child_watcher()
    loop = asyncio.get_event_loop()
    loop.create_task(start())

    thread = threading.Thread(target=run_it_forever, args=(loop,))
    thread.start()


@client.event
async def on_ready():
    LOG.info('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    message_split = message.content.split()
    if message.author == client.user:
        return
    command = ' '.join(message_split[1:])

    if f'<@!{client.user.id}>' == message_split[0]:
        # Handle mention of bot without any utterance
        if len(message_split) == 1:
            await message.channel.send(f'{message.author.name}, did you need something?')
            bus.emit(Message('speak', data={'utterance': f'{message.author.name}, did you need something?',
                                            'listen': False}))
        else:
            bus.emit(Message('recognizer_loop:utterance', {"utterances": [command]},
                             {"discord_message_id": message.id}))


def handle_speak(event):
    if event.context is not None and 'discord_message_id' in event.context:
        utterance = event.data.get('utterance')
        cached_message = discord.utils.get(client.cached_messages, id=event.context['discord_message_id'])
        send_msg = asyncio.run_coroutine_threadsafe(cached_message.channel.send(utterance), client.loop)
        send_msg.result()
