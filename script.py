import time
import datetime 
import requests
import json
import random
import click
import sys
import inquirer
import requests
import pandas as pd
import playsound

DATE_FORMAT = '%d-%m-%Y'
URL = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={district_id}&date={date}'
headers = {
    'User-Agent'     : 'Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0',
    'Accept'         : 'application/json',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer'        : 'https://apisetu.gov.in/public/api/cowin',
    'Origin'         : 'https://apisetu.gov.in',
}

def build_query(preference):
    age_query = 'min_age_limit <= {}'.format(preference.get('age'))
    vaccine_qeury = 'vaccine == {}'.format(preference.get('vaccine')) if \
        not preference.get('vaccine') == 'ALL' else '' 
    date_query = 'date in {}'.format(str(get_date_range(preference.get('date_range'))))
    return ' and '.join(
        filter(None, [age_query, vaccine_qeury, date_query])
    )



def get_date_range(date_range):
    return [(datetime.date.today() + datetime.timedelta(i)).strftime(DATE_FORMAT) for i in range(date_range+1)]

def get_preferred_info(centers, preference):
    preferred_info = list()
    for center in centers:
        df = pd.DataFrame(center.get('sessions'))
        df.drop(['session_id', 'slots', 'available_capacity'], axis=1, inplace=True)
        df.rename(
            columns={
                'available_capacity_dose1': 'dose-I',
                'available_capacity_dose2': 'dose-II',
            }
        )

        query = build_query(preference)
        query_response = df.query(query)

        if not query_response.empty:
            query_response.drop(['min_age_limit'], axis=1, inplace=True)
            preferred_info.append(
                {', '.join([center['name'], center['address']]): query_response}
            )
            
    return preferred_info

def print_formatted_info(pref_info):
    for key, value in pref_info.iteritems():
        click.secho(key)
        click.secho(
            value.to_string(), fg='blue'
        )
        

def ping(preference):
    # try and raise for status
    try:
        while True:
            resp = requests.get(
            URL.format(
                district_id=preference['district'],
                date = datetime.datetime.today().strftime(DATE_FORMAT)
                ), 
                headers=headers
            )
            headers.update({
                'If-None-Match': resp.headers['ETag']
            })

            if resp.status_code == 200:
                pref_info = get_preferred_info(resp.json().get('centers'), preference)
                print_formatted_info(pref_info)


            time.sleep(preference['interval'])

    except (KeyboardInterrupt, SystemExit):
        print('exiting')
 


def update_district(district):
    ''' update district if not provided in args '''
    if district in ('True', 'False'):
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
    '--date-range', 
    type         = click.IntRange(0, 6),
    default      = 0,
    show_default = True,
    help         = 'By default checks availability for today, set from 1-6 to show availability from today to today+n'
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

