# command_clash.py
import os
import random
import urllib.request
import aiohttp
import pandas as pd
import discord
import youtube_dl
import json
import urllib
import asyncio
import requests
import pdb
import openpyxl as op
import numpy as np
import re
import urllib.request
import giphy_client

from discord.ext.commands import Bot
from giphy_client.rest import ApiException
from datetime import datetime
from pathlib import Path
from openpyxl import load_workbook
from time import sleep
from numpy import source
from youtube_search import YoutubeSearch
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
from typing import Optional

load_dotenv()
loop = asyncio.get_event_loop()

# get from .env file
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
TENOR_KEY = os.getenv('TENOR_KEY')
role_specific_command_name = 'Bot Commander'

# connecting with discord with "discord intents"
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

# parent directory
parent_dir = r'C:\Users\Hong Tran\Python\BeeBot'
# create new "yt_links.txt" file on run
yt_links_file = open("resource_files/music_bot_files/yt_links.txt", "w")
# set the current present time
present = datetime.now()

api_instance = giphy_client.DefaultApi()

# bot prefix
bot = commands.Bot(command_prefix='BB ', case_insensitive=True)
print('command_clash.py is running!')


# bot command to add author from availability list
@bot.command(name='clashadd', aliases=['addclash', 'aclash', 'clasha', 'clashavailable'],
             help='Add your clash availability!')
# only specific roles can use this command
@commands.has_role(role_specific_command_name)
async def clash_add(ctx, *, date: Optional[str]):
    try:
        # available member for clash
        available_member = ctx.message.author
        if date == None:
            await ctx.send('Please specify either \'Sat\' or \'Sun\' after command! :smile:')
        else:
            # check if member is already in the "clash_available.txt" file
            check = False
            # help case sensitivity
            date = date.lower()
            # if not sun or sat (the usual clash days)
            if not date == 'sat' and not date == 'sun':
                await ctx.send('Invalid input! :flushed: Please specify either \'Sat\' or \'Sun\' '
                               'after command! :smile:')
            else:
                # read the "clash_dates.txt" file and check if the given date >= present
                clash_dates_file = open("resource_files/clash_files/clash_dates.txt")
                clash_dates_file.flush()
                new_clash_date = clash_dates_file.readline()
                clash_date_convert = datetime.strptime(new_clash_date, '%d-%m-%Y %H:%M')
                if clash_date_convert >= present:
                    # capitalize "Sun" and "Sat"
                    date = date.capitalize()
                    text_input = str(available_member.id) + date + ' : ' + str(available_member.display_name) + '\n'
                    check_input = str(available_member.id) + date
                    clash_available_file = open("resource_files/clash_files/clash_available.txt")
                    check_txt = clash_available_file.readlines()
                    # check if member is already in the "clash_available.txt" file
                    for lines in check_txt:
                        # look at only the id and date from "lines"
                        only_id = re.sub("\D", "", lines)
                        after_id = lines[len(only_id):]
                        only_date = after_id[:3]
                        # new line
                        new_line = only_id + only_date
                        if check_input == new_line:
                            check = True
                    # if member is already in the "clash_available.txt" file
                    if check == True:
                        await ctx.send('Your name was already added to the list for this day! :open_mouth:')
                    # if member is NOT in the document, add them to the "clash_available.txt" file
                    else:
                        clash_available_file_a = open("resource_files/clash_files/clash_available.txt", "a")
                        clash_available_file_a.write(text_input)
                        clash_available_file_a.close()
                        await ctx.send('Your availability has been added to the list! :white_check_mark:')
    except:
        await ctx.send('There\'s currently no clash scheduled! :open_mouth: Try again next clash!')


# bot command to remove author from availability list
@bot.command(name='clashremove', aliases=['removeclash', 'rclash', 'clashr'],
             help='Remove your clash availability!')
# only specific roles can use this command
@commands.has_role(role_specific_command_name)
async def clash_remove(ctx, *, date: Optional[str]):
    try:
        # available member for clash
        available_member = ctx.message.author
        if date == None:
            await ctx.send('Please specify either \'Sat\' or \'Sun\' after command! :smile:')
        else:
            # check if member is in the "clash_available.txt" file
            check = False
            # help case sensitivity
            date = date.lower()
            # if not sun or sat (the usual clash days)
            if not date == 'sat' and not date == 'sun':
                await ctx.send('Invalid input! :flushed: Please specify either \'Sat\' or \'Sun\' '
                               'after command! :smile:')
            else:
                # read the "clash_dates.txt" file and check if the given date >= present
                clash_dates_file = open("resource_files/clash_files/clash_dates.txt")
                clash_dates_file.flush()
                new_clash_date = clash_dates_file.readline()
                clash_date_convert = datetime.strptime(new_clash_date, '%d-%m-%Y %H:%M')
                if clash_date_convert >= present:
                    # capitalize "Sun" and "Sat"
                    date = date.capitalize()
                    text_input = str(available_member.id) + date + ' : ' + str(available_member.display_name) + '\n'
                    check_input = str(available_member.id) + date
                    clash_available_file = open("resource_files/clash_files/clash_available.txt")
                    check_txt = clash_available_file.readlines()
                    # check if member is in the "clash_available.txt" file
                    for lines in check_txt:
                        # look at only the id and date from "lines"
                        only_id = re.sub("\D", "", lines)
                        after_id = lines[len(only_id):]
                        only_date = after_id[:3]
                        # new line
                        new_line = only_id + only_date
                        if check_input == new_line:
                            check = True
                    # if member is in the "clash_available.txt" file
                    if check == True:
                        # new array to store file
                        new_array_with_remove = []
                        # find the member and delete them
                        for lines in check_txt:
                            if text_input == lines:
                                lines = lines.replace(lines, "")
                            # add the other names from the text file into "new_array_with_remove"
                            new_array_with_remove.append(lines)
                        # close file
                        clash_available_file.close()
                        # create new text file with the same name
                        new_clash_available_file = open('resource_files/clash_files/clash_available.txt', 'w')
                        # write array into new file
                        for lines in new_array_with_remove:
                            new_clash_available_file.write(lines)
                        new_clash_available_file.close()
                        await ctx.send('Your name was removed from the availability list. :slight_smile:')
                    else:
                        await ctx.send('Your name wasn\'t on the availability list. :thinking: '
                                       'Add it with the "addclash" command! :smile:')
    except:
        await ctx.send('There\'s currently no clash scheduled! :open_mouth: Try again next clash!')


# bot command to view clash availability list
@bot.command(name='clashview', aliases=['viewclash', 'clashv', 'vclash'],
             help='View list of people available for clash.')
# only specific roles can use this command
@commands.has_role(role_specific_command_name)
async def clash_view(ctx):
    try:
        clash_array = []
        clash_message = ''
        clash_available_file = open("resource_files/clash_files/clash_available.txt")
        clash_available_file.flush()
        clash_dates_file = open("resource_files/clash_files/clash_dates.txt")
        clash_dates_file.flush()

        # check if "clash_dates.txt" has a valid date
        new_clash_date = clash_dates_file.readline()
        clash_date_convert = datetime.strptime(new_clash_date, '%d-%m-%Y %H:%M')
        if clash_date_convert >= present:
            # check that "clash_availability.txt" file is not empty
            ca_check = Path(r'{}\resource_files\clash_files\clash_available.txt'.format(parent_dir))
            if not ca_check.stat().st_size == 0:
                # add lines in "clash_availability.txt" to a "clash_array"
                for lines in clash_available_file:
                    lines = lines.rstrip().lstrip('0123456789')
                    clash_array.append(lines)
                # alphabetize "clash_array"
                clash_array = sorted(clash_array, key=str.lower)
                print(clash_array)
                # add "clash_array" to "clash_message"
                for key in clash_array:
                    clash_message = clash_message + '\n- ' + key

                    # trying to add a "\n" to split "Sat" and "Sun
                    # for key2 in clash_array:
                    #     key2 = key2[:3]
                    #     if key2 == "Sun":
                    #         clash_message = clash_message + '\n'
                    #         break

                await ctx.send('The people available for clash are:{}'.format(clash_message))
            else:
                await ctx.send('No one has added their availability yet! :cry: '
                               'Add yours with the \"addclash\" command! :smile:')
    except:
        await ctx.send('There\'s currently no clash scheduled! :open_mouth: Try again next clash!')


# bot command to set clash date
@bot.command(name='clashset', aliases=['setclash', 'sclash', 'clashs'],
             help='Set next clash. (Server Owner role specific) (DD-MM-YY HH:MM)')
# only VERY specific roles can use this command
@commands.has_role('Server Owner')
async def clash_set(ctx, *, clash_date: Optional[str]):
    try:
        clash_date_convert = datetime.strptime(clash_date, '%d-%m-%Y %H:%M')
        if clash_date_convert >= present:
            # create new "clash_available.txt" and new "clash_date.txt" files
            new_clash_available_text = open("resource_files/clash_files/clash_available.txt", "w")
            new_clash_dates_text = open("resource_files/clash_files/clash_dates.txt", "w")
            # add the "clash_date" to "clash_date.txt" file
            clash_dates_file_a = open("resource_files/clash_files/clash_dates.txt", "a")
            clash_dates_file_a.write(clash_date)
            clash_dates_file_a.close()
            await ctx.send('You set up a new clash! :smile:')
        else:
            await ctx.send('Invalid input! :flushed:')
    except:
        await ctx.send('Invalid input! :flushed:')
