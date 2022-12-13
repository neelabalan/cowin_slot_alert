import time
import datetime
import requests
import json
import click
import inquirer
import requests
import pandas as pd
import playsound
import platform
import os

ascii_art = """
                  _       
  ___ _____      _(_)_ __  
 / __/ _ \ \ /\ / / | '_ \ 
| (_| (_) \ V  V /| | | | |
 \___\___/ \_/\_/ |_|_| |_|
                           
     _       _             
 ___| | ___ | |_           
/ __| |/ _ \| __|          
\__ \ | (_) | |_           
|___/_|\___/ \__|          
                           
       _           _       
  __ _| | ___ _ __| |_     
 / _` | |/ _ \ '__| __|    
| (_| | |  __/ |  | |_     
 \__,_|_|\___|_|   \__|    
"""

DATE_FORMAT = "%d-%m-%Y"
URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={district_id}&date={date}"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://apisetu.gov.in/public/api/cowin",
    "Origin": "https://apisetu.gov.in",
}


def clear():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def build_query(age, vaccine, date_range, dose):
    age_query = "min_age_limit <= {}".format(age)
    vaccine_qeury = 'vaccine == "{}"'.format(vaccine) if not vaccine == "ALL" else None
    date_query = "date in {}".format(str(get_date_range(date_range)))

    dose_query = ""
    if dose:
        dose_query = "dose_I > 0" if dose == 1 else "dose_II > 0"
    else:
        dose_query = "available_capacity > 0"

    return " and ".join(
        filter(None, [age_query, vaccine_qeury, date_query, dose_query])
    )


def get_date_range(date_range):
    return [
        (datetime.date.today() + datetime.timedelta(i)).strftime(DATE_FORMAT)
        for i in range(date_range + 1)
    ]


def extract_preferences(preference):
    age = preference.get("age")
    vaccine = preference.get("vaccine")
    date_range = preference.get("date_range")
    dose = preference.get("dose")
    return age, vaccine, date_range, dose


def filter_query_response(response):
    if not response.empty:
        drop_list = ["min_age_limit", "session_id", "slots", "available_capacity"]
        if (response["dose_I"] == 0).all():
            drop_list.append("dose_I")
        if (response["dose_II"] == 0).all():
            drop_list.append("dose_II")

        filtered_response = response.drop(drop_list, axis=1)
        return filtered_response
    else:
        # return emtpy data frame
        return pd.DataFrame()


def get_preferred_info(centers, query):
    preferred_info = list()

    for center in centers:
        df = pd.DataFrame(center.get("sessions"))
        df.rename(
            columns={
                "available_capacity_dose1": "dose_I",
                "available_capacity_dose2": "dose_II",
            },
            inplace=True,
        )

        query_response = df.query(query)
        filtered_response = filter_query_response(query_response)
        if not filtered_response.empty:
            preferred_info.append(
                {", ".join([center["name"], center["address"]]): filtered_response}
            )

    return preferred_info


def print_formatted_info(pref_info, silent):
    if pref_info:
        if not silent:
            playsound.playsound("assets/sample2.mp3")
        for info in pref_info:
            for center, slots in info.items():
                click.secho(center)
                click.secho(slots.to_string(index=False), fg="blue")
                print("\n\n")


def ping(preference):
    # try and raise for status
    try:
        age, vaccine, date_range, dose = extract_preferences(preference)
        silent = preference.get("silent")
        query = build_query(age, vaccine, date_range, dose)

        while True:
            resp = requests.get(
                URL.format(
                    district_id=preference["district"],
                    date=datetime.datetime.today().strftime(DATE_FORMAT),
                ),
                headers=headers,
            )
            headers.update({"If-None-Match": resp.headers["ETag"]})

            if resp.status_code == 200:
                pref_info = get_preferred_info(resp.json().get("centers"), query)
                clear()
                click.secho(
                    "Last Updated: {}".format(datetime.datetime.now().strftime("%c")),
                    fg="green",
                )
                print_formatted_info(pref_info, silent)

            time.sleep(preference["interval"])

    except (KeyboardInterrupt, SystemExit):
        print("\nexiting")


def update_district(district):
    """update district if not provided in args"""
    if district in ("True", "False"):
        district_map = json.load(open("assets/district_codes.json"))
        which_state = inquirer.prompt(
            [
                inquirer.List(
                    "state",
                    message="Select State",
                    choices=district_map.keys(),
                )
            ]
        ).get("state")

        which_district = inquirer.prompt(
            [
                inquirer.List(
                    "district",
                    message="Select district",
                    choices=district_map.get(which_state).keys(),
                ),
            ]
        ).get("district")

        district = district_map[which_state][which_district]
        click.secho(
            "Your district code for {}, {} is {}".format(
                which_district, which_state, district
            ),
            fg="green",
        )
    return district


@click.command()
@click.option(
    "--date-range",
    type=click.IntRange(0, 6),
    default=0,
    show_default=True,
    help="By default checks availability for today, set from 1-6 to show availability from today to today+n",
)
@click.option(
    "--interval",
    type=int,
    default=120,
    show_default=True,
    help="Set the referesh interval (seconds)",
)
@click.option(
    "--age",
    type=click.IntRange(18, 150),
    required=True,
    prompt=True,
    help="Set age preference",
)
@click.option(
    "--vaccine",
    type=str,
    default="ALL",
    show_default=True,
    prompt=True,
    help="Choose between COVAXIN/COVISHIELD/SPUTNIK. Default is ALL",
)
@click.option(
    "--dose",
    type=click.IntRange(0, 2),
    default=0,
    show_default=True,
    prompt=True,
    help="Set 1 for Dose-I or 2 for Dose-II. Default is both",
)
@click.option(
    "--district",
    is_flag=False,
    flag_value=True,
    default=True,
    help="To find district code keep the argument empty",
)
@click.option("--silent", is_flag=True, help="No alert")
def run(**kwargs):
    kwargs.update({"district": update_district(kwargs.get("district"))})
    clear()
    print(ascii_art)
    time.sleep(5)
    ping(kwargs)


if __name__ == "__main__":
    run()
