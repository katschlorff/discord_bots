import os
from datetime import datetime

import arrow
import requests
from ics import Calendar

cozi_ics_url = os.getenv('COZI_ICS_URL')


def get_the_state_of_the_world_from_cozi():
    cal = Calendar(requests.get(url=cozi_ics_url).text)
    for event in cal.events:
        print(event.name)
        print(arrow.get(event.begin).replace(year=datetime.now().year).humanize())
                  # .date().replace(year=datetime.now().year))


if __name__ == '__main__':
    get_the_state_of_the_world_from_cozi()
