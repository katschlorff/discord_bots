import asyncio
import os
from datetime import datetime

import discord
import requests
from ics import Calendar, Event

intents = discord.Intents.default()
intents.messages = True

cozi_bot_client = discord.Client(intents=intents)

channel_name = os.getenv('DISCORD_BOT_CHANNEL_NAME')
cozi_ics_url = os.getenv('COZI_ICS_URL')
discord_token = os.getenv('DISCORD_TOKEN')


def build_embeds(past_events: [Event], near_future_events: [Event],
                 far_future_events: [Event]) -> [discord.Embed]:
    near_future_embed, far_future_embed, past_embed = discord.Embed(), discord.Embed(), discord.Embed()
    near_future_embed.author.name, far_future_embed.author.name, past_embed.author.name = 'CoziBot', 'CoziBot', 'CoziBot'
    near_future_embed.colour, far_future_embed.colour, past_embed.colour = discord.Colour.from_str(
        '#ff58eb'), discord.Colour.from_str('#ff58eb'), discord.Colour.from_str('#ff58eb')  # this is a nice pink

    near_future_embed.title = 'Events coming up this week!'
    if near_future_events:
        [near_future_embed.add_field(name=event.name,
                                     value=f'{event.begin.humanize()}, on {event.begin.date()}.', inline=True) for
         event in near_future_events]
    else:
        near_future_embed.add_field(name='No events this week!', value='Make sure to make time to see your loves!')

    far_future_embed.title = 'Events in the future!'
    if far_future_events:
        [far_future_embed.add_field(name=event.name,
                                    value=f'{event.begin.humanize()}, on {event.begin.date()}.') for
         event in far_future_events]
    else:
        far_future_embed.add_field(name='No events on the horizon!', value='Maybe get a game night on the books :)')

    past_embed.title = 'Events in the past, just for nostalgia (and testing purposes)'
    if past_events:
        [past_embed.add_field(name=event.name,
                              value=f'{event.begin.humanize()}, on {event.begin.date()}.') for
         event in past_events]
    else:
        past_embed.add_field(name='We have fucked the timeline', value='Time has never existed.')

    return [past_embed, near_future_embed, far_future_embed]


def get_the_state_of_the_world_from_cozi() -> [[Event], [Event], [Event]]:
    cal = Calendar(requests.get(url=cozi_ics_url).text)
    near_future_events = []
    far_future_events = []
    past_events = []
    for event in cal.events:
        if 'birthday' in event.name:
            event.end = event.end.replace(year=9999)
            event.begin = event.begin.replace(year=datetime.now().year)
        if 'ago' in event.begin.humanize():
            past_events.append(event)
        elif 'a week' in event.begin.humanize() or 'day' in event.begin.humanize():
            near_future_events.append(event)
        elif 'in' in event.begin.humanize():
            far_future_events.append(event)

        else:
            print("this wasn't supposed to happen")
            print(event.begin.humanize())

    return [sorted(past_events), sorted(near_future_events), sorted(far_future_events)]


@cozi_bot_client.event
async def on_ready():  # Called when internal cache is loaded
    all_events = get_the_state_of_the_world_from_cozi()
    past_events = all_events[0]
    near_future_events = all_events[1]
    far_future_events = all_events[2]
    channel = discord.utils.get(cozi_bot_client.get_all_channels(),
                                name=channel_name)  # Gets channel from internal cache
    embeds = build_embeds(past_events=past_events, near_future_events=near_future_events,
                          far_future_events=far_future_events)
    # ensure order because async can run out of order
    # cozi_digest_thread = channel.create_thread(name=f'Cozi Digest for {arrow.now().date()}')
    # await channel.send(embed=embeds[0]) #  past
    await channel.send(embed=embeds[1])  # soon
    # await cozi_digest_thread.send(embed=embeds[2]) # future
    await cozi_bot_client.close()


if __name__ == '__main__':
    asyncio.run(cozi_bot_client.run(token=discord_token))
