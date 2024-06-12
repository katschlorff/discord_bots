import os
from datetime import datetime

import discord
import requests
from ics import Calendar

intents = discord.Intents.default()
intents.messages = True

cozi_bot_client = discord.Client(intents=intents)

channel_name = os.getenv('DISCORD_BOT_CHANNEL_NAME')
cozi_ics_url = os.getenv('COZI_ICS_URL')
discord_token = os.getenv('DISCORD_TOKEN')


def get_the_state_of_the_world_from_cozi() -> [[], []]:
    cal = Calendar(requests.get(url=cozi_ics_url).text)
    future_events = []
    past_events = []
    for event in cal.events:
        if 'birthday' in event.name:
            event.end = event.end.replace(year=9999)
            event.begin = event.begin.replace(year=datetime.now().year)
        if 'in' in event.begin.humanize():
            future_events.append(event)
        elif 'ago' in event.begin.humanize():
            past_events.append(event)

        else:
            print("this wasn't supposed to happen")
            print(event.begin.humanize())

    return [past_events, future_events]

    # print('past events:\n\n')
    # for pe in past_events:
    #     print(pe.name)
    #     print(pe.begin.humanize())
    # print('\n')
    # print('future events:\n\n')
    # for fe in future_events:
    #     print(fe.name)
    #     print(fe.begin.humanize())


@cozi_bot_client.event
async def on_ready():  # Called when internal cache is loaded
    all_events = get_the_state_of_the_world_from_cozi()
    future_events = all_events[1]
    channel = discord.utils.get(cozi_bot_client.get_all_channels(),
                                name=channel_name)  # Gets channel from internal cache
    await channel.send('Upcoming events!\n')
    for event in future_events:
        await channel.send(event.name)
        await channel.send(event.begin.humanize())


if __name__ == '__main__':
    cozi_bot_client.run(token=discord_token)
    cozi_bot_client.close()
    # # get_the_state_of_the_world_from_cozi()
    # channel.send('hello world!')
