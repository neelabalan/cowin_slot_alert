import time
import datetime 
import requests
import json
import random
import click
import sys
import inquirer
import requests

DATE_FORMAT = '%d-%m-%Y'
URL = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={district_id}&date={date}'
headers = {
    'User-Agent'     : 'Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0',
    'Accept'         : 'application/json',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer'        : 'https://apisetu.gov.in/public/api/cowin',
    'Origin'         : 'https://apisetu.gov.in',
}

def get_preferred_info(response, preference):
    pass


def ping(preference):
    # try and raise for status
    # add vaccine preference
    resp = requests.get(
       URL.format(
           district_id=preference['district'],
           date = preference['start'].strftime(DATE_FORMAT)
        ), 
        headers=headers
    )
    headers.update({
        'If-None-Match': resp.headers['ETag']
    })

    if resp.status_code == 200:
        get_preferred_info(resp.json(), preference)
 


def update_district(district):
    ''' update district if not provided in args '''
    if type(district) == bool:  
        district_map = json.load(open('assets/district_codes.json'))
        which_state = inquirer.prompt([
            inquirer.List(
                'state',
                message="Select State",
                choices=district_map.keys(),
            )
        ]).get('state')

        which_district = inquirer.prompt([
            inquirer.List(
                'district',
                message = 'Select district',
                choices=district_map.get(which_state).keys(),
            ),
        ]).get('district')

        district = district_map[which_state][which_district] 
        click.secho(
            'Your district code for {}, {} is {}'.format(
                which_district, 
                which_state, 
                district
            ), 
            fg='green'
        )
    return district



@click.command()
@click.option(
    '--start', 
    type         = click.DateTime(formats=[DATE_FORMAT]),
    default      = datetime.date.today().strftime(DATE_FORMAT),
    show_default = True,
    help         = 'Date format - DD-MM-YY'
)
@click.option(
    '--end', 
    type         = click.DateTime(formats=[DATE_FORMAT]),
    default      = datetime.date.today().strftime(DATE_FORMAT),
    show_default = True,
    help         = 'Date format - DD-MM-YY'
)
@click.option(
    '--interval', 
    type         = int,
    default      = 120,
    show_default = True,
    help         = 'Set the referesh interval'
)
@click.option(
    '--age',      
    type       = click.IntRange(18, 150),
    required   = True,
    prompt     = True,
    help       = 'Set age preference'
)
@click.option(
    '--vaccine', 
    type         = str,
    default      = 'ALL',
    show_default = True,
    prompt       = True,
    help         = 'COVAXIN/COVISHIELD/SPUTNIK/ALL'
)
@click.option("--district", is_flag=False,  flag_value=True, default=True, help='To find district code keep the argument empty')
@click.option('--alert',    is_flag=True,   help='Sound alert if new slot is found')
def run(**kwargs):
    kwargs.update({'district': update_district(kwargs.get('district'))})
    ping(kwargs) 
    # print(kwargs)


if __name__ == '__main__':
    run()

