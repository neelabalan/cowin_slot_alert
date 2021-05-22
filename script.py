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

def build_query(age, vaccine, date_range, dose):
    age_query = 'min_age_limit <= {}'.format(age)
    vaccine_qeury = 'vaccine == {}'.format(vaccine) if \
        not vaccine == 'ALL' else None
    date_query = 'date in {}'.format(str(get_date_range(date_range)))
    if dose:
        dose_query = 'does-I > 0' if dose==1 else 'dose-II > 0' 

    return ' and '.join(
        filter(None, [age_query, vaccine_qeury, date_query, dose_query])
    )



def get_date_range(date_range):
    return [(datetime.date.today() + datetime.timedelta(i)).strftime(DATE_FORMAT) for i in range(date_range+1)]

def extract_preferences(preference):
    age        = preference.get('age')
    vaccine    = preference.get('vaccine')
    date_range = preference.get('date_range')
    dose       = preference.get('dose')
    return age, vaccine, date_range, dose

def get_preferred_info(centers, preference):
    preferred_info = list()
    age, vaccine, date_range, dose = extract_preferences(preference)

    for center in centers:
        df = pd.DataFrame(center.get('sessions'))
        df.rename(
            columns={
                'available_capacity_dose1': 'dose-I',
                'available_capacity_dose2': 'dose-II',
            }
        )

        query = build_query(age, vaccine, date_range, dose)
        query_response = df.query(query)

        if not query_response.empty:
            drop_list = ['min_age_limit', 'session_id', 'slots', 'available_capacity']
            if not dose:
                drop_list.append('dose-I') if dose==1 else drop_list.append('dose-II')
            

            filtered_query_response = query_response.drop(drop_list, axix=1)
            preferred_info.append(
                {', '.join([center['name'], center['address']]): filtered_query_response}
            )
            
    return preferred_info

def print_formatted_info(pref_info):
    for key, value in pref_info.iteritems():
        playsound.playsound('assets/sample2.mp3')
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
    help         = 'Set the referesh interval (seconds)'
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
@click.option(
    '--interval', 
    type         = click.IntRange(0, 2),
    default      = 0,
    show_default = True,
    help         = 'Set 1 for Dose-I or 2 for Dose-II. Default is both'
)
@click.option("--district", is_flag=False,  flag_value=True, default=True, help='To find district code keep the argument empty')
@click.option('--alert',    is_flag=True,   help='Sound alert if new slot is found')
def run(**kwargs):
    kwargs.update({'district': update_district(kwargs.get('district'))})
    ping(kwargs) 
    # print(kwargs)


if __name__ == '__main__':
    run()

