# games.py
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
print('games.py is running!')


# bot command to pick a game from an excel sheet of games with number of player specification
@bot.command(name='pickgame', help='Picks a game to play. (Auto #: People in voice call)')
async def pick_game(ctx, number_of_players: Optional[int]):
    try:
        if number_of_players == None:
            # if "number_of_players" is none, then count the "number_of_players" in the voice channel of the author
            channel = ctx.message.author.voice.channel
            number_of_players = 0
            # add 1 to "number_of_players" depending on how many members in channel.members
            for member in channel.members:
                number_of_players += 1

        # fix for the full "GameName" not showing up
        pd.set_option('display.max_colwidth', -1)
        # accessing GamesList_copy.xlsx
        games_file = pd.read_excel(r'{}\resource_files\excel_files\game_list_copy.xlsx'.format(parent_dir))
        games_file_df = pd.DataFrame(games_file, columns=['GameName', 'PlayerNumMIN', 'PlayerNumMAX'])

        # calculating "player_range"
        player_range = games_file_df['PlayerNumMAX'] - games_file_df['PlayerNumMIN']
        games_file_df['PlayerRange'] = player_range

        # checking games within the specified range and creating a new dataframe for it
        player_range_check_df = games_file_df.loc[
            (games_file_df['PlayerNumMIN'] <= number_of_players) & (games_file_df['PlayerNumMAX'] >= number_of_players)]

        # wip
        ####################################################
        # for column in player_range_check_df:
        # print(player_range_check_df)
        #####################################################

        # picking a random "GameName"
        game_names = pd.DataFrame(player_range_check_df, columns=['GameName'])
        random_game = game_names.sample().to_string(index=False, header=False)
        # print(random_game)

        pg_quotes = [
            ('Have you tried***{}*** ? :smile:'.format(random_game)),
            ('Why not try***{}*** ? :open_mouth:'.format(random_game)),
            ('I recommend***{}*** ! :liar:'.format(random_game)),
            ('I might not have friends, but your friends can play\n***{}*** ! :smiling_face_with_tear:'.format(
                random_game))
        ]
        pg_message = random.choice(pg_quotes)
        await ctx.send(pg_message)
    # if number_of_players was 0
    except:
        await ctx.send('An error occurred! :thinking:\nTry adding a number after "pickgame" '
                       'or joining a voice channel! :slight_smile:')


# bot command to add a game with specific info to the "GameList.xlsx"
@bot.command(name='addgame', help='Add a game to \"pickgame\" command. (Max: 100) (Role specific)')
# only specific roles can use this command
@commands.has_role(role_specific_command_name)
async def add_game(ctx, game_name: Optional[str], min_players: Optional[int], max_players: Optional[int]):
    try:
        if game_name == None or min_players == None or max_players == None:
            await ctx.send('Please provide a "game name" and both a \"min\" and \"max\" number of players! '
                           ':slight_smile:')
        else:
            if min_players <= max_players and min_players >= 1 and max_players >= 1 and max_players <= 100:
                new_data = pd.DataFrame({'GameName': [game_name],
                                         'PlayerNumMIN': [min_players],
                                         'PlayerNumMAX': [max_players]})

                # adding game info to "GameList_copy.xlsx" file
                gl_writer = pd.ExcelWriter('game_list_copy.xlsx', engine='openpyxl')
                # try to open an existing workbook
                gl_writer.book = load_workbook('resource_files\excel_files\game_list_copy.xlsx')
                # copy existing sheets
                gl_writer.sheets = dict((ws.title, ws) for ws in gl_writer.book.worksheets)
                # read existing file
                gl_reader = pd.read_excel(r'resource_files\excel_files\game_list_copy.xlsx')
                # write out the new sheet
                new_data.to_excel(gl_writer, index=False, header=False, startrow=len(gl_reader) + 1)
                gl_writer.close()

                await ctx.send(':space_invader: Your game has been added to the list! :space_invader:')
            else:
                await ctx.send('Your inputs seem to be incorrect! :flushed: Please try again. :relieved:')
    except:
        await ctx.send('An error occurred! :thinking: Try adding a number after "pickgame"! :slight_smile:')


# bot command to split teams
@bot.command(name='splitteam', aliases=['teamsplit', 'maketeams', 'maketeam', 'pickteams', 'pickteam', 'teams', 'team'],
             help='Splits members in voice channel into teams.')
async def split_team(ctx, number_of_teams: Optional[int]):
    max_teams = 101
    team_number = 0
    count_members = 0
    players_array = []
    teams_array = []
    final_message = ''
    try:
        # set "number_of_teams" to 1 if none
        if number_of_teams == None:
            number_of_teams = 2
        if number_of_teams <= max_teams:
            # create a "players_array" for members in the voice channel
            channel = ctx.message.author.voice.channel
            for member in channel.members:
                count_members += 1
                user = member.display_name
                players_array.append(user)
            # randomize the elements of the array 1 to "count_members" times
            for i in range(random.randint(1, count_members)):
                random.shuffle(players_array)

            # split the teams into the number of teams
            team_splitting = np.array_split(players_array, number_of_teams)

            # create a "team_array" for the split teams
            for i in range(len(team_splitting)):
                # checking empty
                # if team_splitting[i]:
                quote_players = ''
                for j in range(len(team_splitting[i])):
                    if team_splitting[i][j]:
                        quote_players = quote_players + '{}, '.format(team_splitting[i][j])
                teams_array.append(quote_players)

            # create a "final_message" with all the teams
            for teams in range(len(teams_array)):
                team_number += 1
                # check if element is not empty
                if teams_array[teams]:
                    final_message = final_message + 'Team {} :  {}\n'.format(team_number, teams_array[teams][:-2])

            await ctx.send('The teams are : \n{}'.format(final_message))
        else:
            await ctx.send('Too many teams! :confounded: Please try again!')
    except:
        await ctx.send('An error has occurred! :confounded: Please try again!')

