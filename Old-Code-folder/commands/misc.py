# misc.py
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
parent_dir = r'C:\Users\Hong Tran\Python\BeeBot\commands'
# create new "yt_links.txt" file on run
yt_links_file = open("resource_files/music_bot_files/yt_links.txt", "w")
# set the current present time
present = datetime.now()

api_instance = giphy_client.DefaultApi()

# bot prefix
bot = commands.Bot(command_prefix='BB ', case_insensitive=True)
print('misc.py is running!')


# bot command to add suggestions for BeeBot
@bot.command(name='suggest', aliases=['suggestion'], help='Make a suggestion for a BeeBot feature! (Role specific)')
# only specific roles can use this command
@commands.has_role(role_specific_command_name)
async def suggest(ctx, *, suggestion: Optional[str]):
    if suggestion == None:
        await ctx.send('Please include a suggestion! :smile:')
    else:
        suggest_file = open("resource_files/text_files/suggestions_for_bot.txt", "a")
        suggest_file.write('- ' + suggestion + '\n')
        suggest_file.close()
        await ctx.send('Your suggestion has been added to the list! :face_with_monocle:')


# bot command to flip coin
@bot.command(name='coinflip', aliases=['coin', 'coins', 'flip', 'flips'], help='Simulates coin flip.')
async def coin_flip(ctx, number_of_coins: Optional[int]):
    try:
        # empty message
        cf_message = ''
        # default 1 coin
        if number_of_coins == None:
            number_of_coins = 1
        if number_of_coins > 300 or number_of_coins < 1:
            await ctx.send('Sorry! The coin is broken. :cry: Try again! ')
        else:
            coin_flip_ht = [
                'Heads, ',
                'Tails, '
            ]
            cf_quotes = [
                'You coin flip(s) were:\n',
                'Clink, spin, spin, clink:\n',
                'Heads or Tails? :open_mouth:\n',
                'I wish you good RNG :relieved:\n',
                ':coin:\n'
            ]
            # add coin flips to string
            for i in range(number_of_coins):
                cf_message = cf_message + random.choice(coin_flip_ht)
            await ctx.send('{}{}'.format(random.choice(cf_quotes), cf_message[:-2]))
    except:
        # if out of bounds of bot's capability
        await ctx.send('Sorry! The coin is broken. :cry: Try again! ')


# bot command to roll dice (no specification is an auto 1D6)
@bot.command(name='rolldice', aliases=['diceroll', 'roll', 'dice'],
             help='Simulates rolling dice. (Auto: 1D6)')
async def roll(ctx, number_of_dice: Optional[int], number_of_sides: Optional[int]):
    try:
        # default 1D6 dice
        if number_of_dice == None:
            number_of_dice = 1
        if number_of_sides == None:
            number_of_sides = 6
        if number_of_dice > 500 or number_of_dice < 1 or number_of_sides < 1:
            await ctx.send('Sorry! The dice is broken. :cry: Try again! ')
        else:
            dice = [
                str(random.choice(range(1, number_of_sides + 1)))
                for _ in range(number_of_dice)
            ]
            rd_quotes = [
                'Your dice roll(s) were:\n',
                'Clack, rattle, clatter:\n',
                'Highroller?!? :open_mouth:\n',
                'I wish you good RNG :relieved:\n',
                ':game_die:\n',
                ':skull: + :ice_cube:\n'
            ]
            rd_message = random.choice(rd_quotes)
            await ctx.send('{}'.format(rd_message) + ', '.join(dice))
    except:
        # if out of bounds of bot's capability
        await ctx.send('Sorry! The dice is broken. :cry: Try again! ')

