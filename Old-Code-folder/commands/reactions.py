# reactions.py
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
print('reactions.py is running!')


# bot command to show bee facts
@bot.command(name='facts', aliases=['fact'], help='Bee facts!')
async def facts(ctx):
    img_path = parent_dir + r'\resource_files\image_files\bee_facts_images'
    fact_images = random.choice([
        x for x in os.listdir(img_path)
        if os.path.isfile(os.path.join(img_path, x))
    ])
    # credits:
    # idea from https://github.com/SamKeathley/BeeBot
    # additional facts from https://www.sciencelearn.org.nz/resources/2002-bees-fun-facts
    fact_quotes = [
        ':bee: Bees have 5 eyes. :eyes:',
        ':bee: Bees are insects, so they have 6 legs. (That\'s a lot of boots :boot:)',
        ':bee: Male bees in the hive are called drones. :male_sign:',
        ':bee: Bees fly about 20 mph! :runner:',
        ':bee: Female bees in the hive (except for her Royal Majesty) are called worker bees! '
        ':woman_construction_worker:',
        ':bee: Losing its stinger will cause a bee to die! :skull:',
        ':bee: Bees carry pollen on their hind legs in a pollen basket or corbicula! :basket:',
        ':bee: An average beehive can hold around 50,000 bees! :house_with_garden:',
        ':bee: Foragers must collect nectar from about 2 million flowers to make 1 pound of honey! :sunflower:',
        ':bee: The average forager makes about 1/12 th of a teaspoon of honey in her lifetime! :honey_pot:',
        ':bee: The principal form of communication among honey bees is through chemicals called pheromones! :scientist:',
        ':bee: Honey has been shown to have many health benefits both when eaten and when applied to the skin.'
        'The darker the honey the better! :honey_pot:',
        ':bee: There are over 20, 000 different species of bee, found on every continent except Antarctica! '
        ':earth_americas:',
        ':bee: Bees love blue and love cluster plants like lavender and rosemary! :blue_heart:',
        ':bee: A Queen Bee can produce 2,000 eggs a day. Fertilised eggs become females and unfertilised eggs '
        'become males, with the help of pheromones! :egg:',
        ':bee: Bees mate high in the sky. Afterwards the male bee loses his reproductive organs and dies! :skull:'
    ]
    fact_message = random.choice(fact_quotes)

    await ctx.send('{}'.format(fact_message),
                   file=discord.File('resource_files/image_files/bee_facts_images/{}'.format(fact_images)))


# bot command to show cute angry pictures
@bot.command(name='happy', aliases=['c:'], help='BeeBot happy! c:')
async def happy(ctx):
    img_path = parent_dir + r'\resource_files\image_files\happy_images'
    happy_images = random.choice([
        x for x in os.listdir(img_path)
        if os.path.isfile(os.path.join(img_path, x))
    ])
    happy_quotes = [
        'Smiley! :smile:',
        'I\'m a happy bee! :smile:',
        'Very happy. c:'
    ]
    happy_message = random.choice(happy_quotes)

    await ctx.send('{}'.format(happy_message),
                   file=discord.File('resource_files/image_files/happy_images/{}'.format(happy_images)))


# bot command to show cute sad pictures
@bot.command(name='sad', aliases=['sadge', ':c'], help='BeeBot sad! :c')
async def sad(ctx):
    img_path = parent_dir + r'\resource_files\image_files\sad_images'
    sad_images = random.choice([
        x for x in os.listdir(img_path)
        if os.path.isfile(os.path.join(img_path, x))
    ])
    sad_quotes = [
        'Big sad.',
        'Big sadge.',
        'Do not talk me. Am sad.',
        'No talk me. Im sad.',
        'How could you?',
    ]
    sad_message = random.choice(sad_quotes)

    await ctx.send('{}'.format(sad_message),
                   file=discord.File('resource_files/image_files/sad_images/{}'.format(sad_images)))


# bot command to show cute angry pictures
@bot.command(name='angry', aliases=['angy', 'mad', 'hmph', '>:c', 'madge'], help='BeeBot angry! >:c')
async def angry(ctx):
    img_path = parent_dir + r'\resource_files\image_files\angry_images'
    angry_images = random.choice([
        x for x in os.listdir(img_path)
        if os.path.isfile(os.path.join(img_path, x))
    ])
    angry_quotes = [
        'Do not talk me. Am anger.',
        'No talk me. Im angy.',
        'Wat you looking at?',
        'How dare you.',
        'Hmph.',
        'I will attack.',
        'I\'m so done.',
        ':angry:'
    ]
    angry_message = random.choice(angry_quotes)

    await ctx.send('{}'.format(angry_message),
                   file=discord.File('resource_files/image_files/angry_images/{}'.format(angry_images)))


# bot command to pick random colour
@bot.command(name='pickcolour', aliases=['pickcolor', 'colour', 'color'],
             help='Picks a colour. (Typically chroma colours)')
async def colour(ctx):
    colours_quotes = [
        'Red',
        'Orange',
        'Yellow',
        'Green',
        'Light Blue',
        'Dark Blue',
        'Purple',
        'White',
        'Black',
        'Pink'
    ]
    colours_message = random.choice(colours_quotes)
    await ctx.send(colours_message)


# bot command to wish someone a Happy Birthday
@bot.command(name='happybirthday', aliases=['hbd', 'birthday'],
             help='Wishes someone a Happy Birthday! (Try a mention!)')
async def hbd(ctx, member_name: Optional[str]):
    if member_name == None:
        member_name = ''
    hbd_quotes = [
        'HAPPY BIRTHDAY {}!!!!!  :partying_face: :birthday: :tada:'.format(member_name),
        'Wishing you a Happy Birthday {}! :relieved: :birthday: :tada:'.format(member_name),
        'May all your birthday wishes come true {} — except for the illegal ones!\n:birthday: :tada: '
        ':neutral_face:'.format(member_name)
    ]
    hbd_message = random.choice(hbd_quotes)
    await ctx.send(hbd_message)


@bot.command(name='gif', aliases=['giphy', 'tenor'], help='Find gif from tenor.')
async def gif(ctx, *, search: Optional[str]):
    # set discord.Embed colour to blue
    embed = discord.Embed(colour=discord.Colour.blue())
    # search 'bees' if no given search
    if search == None:
        search = 'bees'
    # make the search, url friendly by changing all spaces into "+"
    search.replace(' ', '+')
    # api.tenor website for given search
    # settings: ContentFilter = medium (PG)
    url = 'https://api.tenor.com/v1/search?q={}&key={}&ContentFilter=medium'.format(search, TENOR_KEY)
    # get url info
    get_url_info = requests.get(url)
    # 200 status_code means tenor is working
    if get_url_info.status_code == 200:
        # checking for results
        json_search = get_url_info.json()
        json_check = json_search['next']
        if json_check == "0":
            await ctx.send("Sorry! Couldn't find any gifs for {}! :cry:".format(search))
        else:
            # load json to get url data
            data = json.loads(get_url_info.text)
            # random choice
            gif_choice = random.randint(0, 9)
            # get gif result
            result_gif = data['results'][gif_choice]['media'][0]['gif']['url']
            # embed gif and send
            embed.set_image(url=result_gif)
            await ctx.send(embed=embed)
    # 404 status_code means tenor is not working/down
    elif get_url_info.status_code == 404:
        await ctx.send("Sorry! Tenor is not working at the moment! :cry:")
