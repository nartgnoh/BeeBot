# event_dates.py
# Every time BeeBot runs, check the "present" date and the dates in "event_dictionary.txt" to make
# value null if event passed

import os
import json
import ast
import easygui
from datetime import datetime

present = datetime.now()
# open dictionary file
with open('resource_files/text_files/event_dictionary.txt') as f:
    data = f.read()
date_dict = ast.literal_eval(data)


# reset clash date
def clash_date():
    # delete "clash_available.txt" file if clash_date < present
    if os.path.isfile("resource_files/clash_files/clash_available.txt"):
        os.remove("resource_files/clash_files/clash_available.txt")


# birthday pop-up reminders
def birthday_date():
    name = x[9:]
    easygui.msgbox("It's {}'s Birthday today!".format(name), title="Birthday Reminder")


for x in date_dict:
    # null date
    if date_dict[x] == "00-00-0000-00:00":
        continue
    date_convert = datetime.strptime(date_dict[x], '%d-%m-%Y-%H:%M')
    if date_convert < present:
        date_dict[x] = "00-00-0000-00:00"
        if x == 'clash':
            clash_date()
        elif 'birthday_' in x:
            # add a year to birthday reminder
            birthday_date()
            new_date_add_year = date_convert.replace(year=date_convert.year + 1)
            new_date_string = new_date_add_year.strftime('%d-%m-%Y-%H:%M')
            date_dict[x] = new_date_string

# create new "event_dictionary.txt" files
new_event_dates_text = open("resource_files/text_files/event_dictionary.txt", "w")
# add the "date_dict" to "event_dictionary.txt" file
dates_file_a = open("resource_files/text_files/event_dictionary.txt", "a")
# convert date_dict to string
date_dict_to_str = json.dumps(date_dict)
# add the "date_dict" to "event_dictionary.txt" file
dates_file_a.write(date_dict_to_str)
dates_file_a.close()

print('event_dates.py is finished!')
