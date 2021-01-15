# clash_dates.py
# Every time BeeBot runs, check the "present" date and the "clash_dates.txt" file to see if clash is soon

import os
from datetime import datetime

present = datetime.now()


def get_clash_date():
    # check if "clash_dates.txt" exists
    if os.path.isfile("resource_files/clash_files/clash_dates.txt"):
        clash_dates_file = open("resource_files/clash_files/clash_dates.txt")
        clash_dates_file.flush()
        # convert the date in file from string to datetime variable
        new_clash_date = clash_dates_file.readline()
        clash_date_convert = datetime.strptime(new_clash_date, '%d-%m-%Y %H:%M')
        return clash_date_convert
    else:
        return present


# call "get_clash_date" function
clash_date = get_clash_date()
# delete "clash_dates.txt" file if clash_date < present
if os.path.isfile("resource_files/clash_files/clash_dates.txt"):
    if clash_date < present:
        os.remove("resource_files/clash_files/clash_dates.txt")

# delete "clash_available.txt" file if clash_date < present
if os.path.isfile("resource_files/clash_files/clash_available.txt"):
    if clash_date < present:
        os.remove("resource_files/clash_files/clash_available.txt")

print('clash_dates.py is finished!')
