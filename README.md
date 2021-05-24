# COWIN slot alert 💉 🔔

## Command line vaccine tracker 
> get alerted with `Napalm Death` or `Suspense` sound when slot is available for your preference

```python

playsound.playsound('assets/sample2.mp3') 
# to 

playsound.playsound('assets/sample1.mp3') 
# in script.py for Napalm Death alert 🎸
```

> Note: report issues [here](https://github.com/neelabalan/cowin_slot_alert/issues) if you find any. 

```
Usage: script.py [OPTIONS]

Options:
  --date-range INTEGER RANGE  By default checks availability for today, set
                              from 1-6 to show availability from today to
                              today+n  [default: 0;0<=x<=6]
  --interval INTEGER          Set the referesh interval (seconds)  [default:
                              120]
  --age INTEGER RANGE         Set age preference  [18<=x<=150;required]
  --vaccine TEXT              Choose between COVAXIN/COVISHIELD/SPUTNIK.
                              Default is ALL  [default: ALL]
  --dose INTEGER RANGE        Set 1 for Dose-I or 2 for Dose-II. Default is
                              both  [default: 0;0<=x<=2]
  --district TEXT             To find district code keep the argument empty
  --silent                    No alert
  --help                      Show this message and exit.

```

### How it looks like
```
$ python3 script.py --date-range 3
Age: 55
Vaccine [ALL]: COVISHIELD
Dose [0]: 2
[?] Select State: Tamil Nadu
   Mizoram
   Nagaland
   Odisha
   Puducherry
   Punjab
   Rajasthan
   Sikkim
 > Tamil Nadu
   Telangana
   Tripura
   Uttar Pradesh
   Uttarakhand
   West Bengal

[?] Select district: Chennai
   Aranthangi
   Ariyalur
   Attur
   Chengalpet
 > Chennai
   Cheyyar
   Coimbatore
   Cuddalore
   Dharmapuri
   Dindigul
   Erode
   Kallakurichi
   Kanchipuram


Apollo Childrens Hospital, NO. 15 SHAFEE MOHAMMED ROAD THOUSAND LIGHTS CHENNAI
      date    vaccine  dose_II
22-05-2021 COVISHIELD       25



Vivekanandha Nagar UPHC, 39 Appa St. Vivekananda Nagar
      date    vaccine  dose_I  dose_II
22-05-2021 COVISHIELD       6       10



Madhavaram UCHC, Madhavaram
      date    vaccine  dose_I  dose_II
22-05-2021 COVISHIELD      10       10
25-05-2021 COVISHIELD      14       22



Madhavaram GH, GH Milk ColonyMadhavaramChennai
      date    vaccine  dose_I  dose_II
22-05-2021 COVISHIELD       2       10
23-05-2021 COVISHIELD       3       10
24-05-2021 COVISHIELD       5       10
.
.
.
.


```
