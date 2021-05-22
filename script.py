import time
import datetime 
import requests
import json
import random
import click
import sys
import inquirer

DATE_FORMAT = '%d-%m-%Y'

def update_district(district):
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
@click.option("--district", is_flag=False,  flag_value=True, default=True, help='To find district code keep the argument empty')
@click.option('--alert',    is_flag=True,   help='Sound alert if new slot is found')
def run(**kwargs):
    kwargs.update({'district': update_district(kwargs.get('district'))})
    print(kwargs)


if __name__ == '__main__':
    run()

