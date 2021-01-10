# bot.py
import os
import random
import urllib.request
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
role_specific_command_name = 'Bot Commander'

# connecting with discord with "discord intents"
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

# parent directory
parent_dir = r'C:\Users\Hong Tran\Python\BeeBot'
# create new "yt_links.txt" file on run
yt_links_file = open("Code_files/music_bot_files/yt_links.txt", "w")

# bot prefix
bot = commands.Bot(command_prefix='BB ')
print('bot.py is running!')
print('updated c:')


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
        games_file = pd.read_excel(r'{}\Code_files\Excel_files\GameList_copy.xlsx'.format(parent_dir))
        games_file_df = pd.DataFrame(games_file, columns=['GameName', 'PlayerNumMIN', 'PlayerNumMAX'])

        # calculating "player_range"
        player_range = games_file_df['PlayerNumMAX'] - games_file_df['PlayerNumMIN']
        games_file_df['PlayerRange'] = player_range

        # checking games within the specified range and creating a new dataframe for it
        player_range_check_df = games_file_df.loc[
            (games_file_df['PlayerNumMIN'] <= number_of_players) & (games_file_df['PlayerNumMAX'] >= number_of_players)]

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
@bot.command(name='addgame', help='Add a game to \"pickgame\" command. (Role specific)')
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
                gl_writer = pd.ExcelWriter('GameList_copy.xlsx', engine='openpyxl')
                # try to open an existing workbook
                gl_writer.book = load_workbook('Code_files\Excel_files\GameList_copy.xlsx')
                # copy existing sheets
                gl_writer.sheets = dict((ws.title, ws) for ws in gl_writer.book.worksheets)
                # read existing file
                gl_reader = pd.read_excel(r'Code_files\Excel_files\GameList_copy.xlsx')
                # write out the new sheet
                new_data.to_excel(gl_writer, index=False, header=False, startrow=len(gl_reader) + 1)
                gl_writer.close()

                await ctx.send(':space_invader: Your game has been added to the list! :space_invader:')
            else:
                await ctx.send('Your inputs seem to be incorrect! :flushed: Please try again. :relieved:')
    except:
        await ctx.send('An error occurred! :thinking: Try adding a number after "pickgame"! :slight_smile:')


# bot command to split teams
@bot.command(name='splitteam', aliases=['teamsplit', 'maketeams', 'maketeam', 'teams', 'team'],
             help='Splits members in voice channel into teams.')
async def split_team(ctx, number_of_teams: Optional[int]):
    max_teams = 101
    team_number = 0
    count_members = 0
    players_array = []
    teams_array = []
    final_message = ''
    # try:
    # set "number_of_teams" to 1 if none
    if number_of_teams == None:
        number_of_teams = 1
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
    # except:
    #     await ctx.send('An error has occurred! :confounded: Please try again!')


# bot command to add suggestions for BeeBot
@bot.command(name='suggest', aliases=['suggestion'], help='Make a suggestion for a BeeBot feature! (Role specific)')
# only specific roles can use this command
@commands.has_role(role_specific_command_name)
async def feature_suggest(ctx, *, suggestion: Optional[str]):
    if suggestion == None:
        await ctx.send('Please include a suggestion! :smile:')
    else:
        suggest_file = open("Code_files/Text_files/suggestions_for_bot.txt", "a")
        suggest_file.write('- ' + suggestion + '\n')
        suggest_file.close()
        await ctx.send('Your suggestion has been added to the list! :face_with_monocle:')


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


# bot command to show cute angry pictures
@bot.command(name='angry', aliases=['angy', 'mad'], help='BeeBot angry! >:c')
async def angry(ctx):
    img_path = parent_dir + r'\Code_files\Image_files\angry_images'
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
        'I will attack.'
    ]
    angry_message = random.choice(angry_quotes)

    await ctx.send('{}'.format(angry_message),
                   file=discord.File('Code_files/Image_files/angry_images/{}'.format(angry_images)))


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
        if number_of_dice > 500:
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


# bot command to play Youtube Audio
@bot.command(name='play', aliases=['playaudio', 'playsong'],
             help='♫ Plays YouTube audio! Provide YouTube search or link! (Role specific) ♫')
# only specific roles can use this command
@commands.has_role(role_specific_command_name)
async def play(ctx, *, yt_search_or_link: Optional[str]):
    try:
        # no "url" provided
        if yt_search_or_link == None:
            await ctx.send('Please provide a YouTube link or YouTube search info! :pleading_face:')
        else:
            # if "url" is not a real url link, then "YoutubeSearch" and create new a YouTube url link
            if 'www.youtube.com' not in yt_search_or_link:
                yt = YoutubeSearch(yt_search_or_link, max_results=1).to_json()
                yt_id = str(json.loads(yt)['videos'][0]['id'])
                yt_search_or_link = 'https://www.youtube.com/watch?v=' + yt_id

            # append "url_link" to "yt_links" file
            add_yt_links_file = open("Code_files/music_bot_files/yt_links.txt", "a")
            add_yt_links_file.write('\n' + yt_search_or_link)
            add_yt_links_file.close()
            open_yt_links_file = open("Code_files/music_bot_files/yt_links.txt")

            # get_url function
            url = get_url()

            # check if bot is in channel and join if is not
            channel = ctx.message.author.voice.channel
            if channel:
                voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
                if voice and voice.is_connected():
                    await voice.move_to(channel)
                else:
                    voice = await channel.connect()

                # audio not playing then play audio
                if not voice.is_playing():
                    await ctx.send(':musical_note: BeeBot will now bee playing ***{}!*** '
                                   ':musical_note:'.format(message_now_playing(url)))
                    # call "download_song" function
                    download_song(ctx)
                    voice.play(discord.FFmpegPCMAudio("Code_files/music_bot_files/song.mp3"),
                               after=lambda e: download_song(ctx))
                    voice.is_playing()
                else:
                    # if music is audio is playing already, add audio to queue
                    await ctx.send(':musical_note: Your audio has been added to the queue! :smile:')
    except:
        print("Ignoring errors c:")


# bot command to go to next audio in queue by reaction vote
@bot.command(name='next', aliases=['skip'], help='♫ Play the next audio! (Role specific) ♫')
# only specific roles can use this command
@commands.has_role(role_specific_command_name)
async def next(ctx):
    try:
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        # check if the queue is empty
        fl_check = Path(r'{}\Code_files\music_bot_files\yt_links.txt'.format(parent_dir))
        if not fl_check.stat().st_size == 0:
            # check if voice is playing
            if not voice.is_playing:
                await ctx.send('Not playing any music right now. :thinking:')
            else:
                # get url for message
                url = get_url()
                await ctx.send(':musical_note: BeeBot will now bee playing ***{}!*** '
                               ':musical_note:'.format(message_now_playing(url)))
                # stop the current song
                voice.stop()
                # download "next_song.mp3" and play that
                download_next_song(ctx)
        else:
            await ctx.send("There is not more audio in the queue! :flushed: Try the \"play\" command to add a song! :smile:")
    except:
        await ctx.send("An error has occurred! :open_mouth: Please try again!")


# bot command to leave voice channel and deletes queue
@bot.command(name='leave', aliases=['stopaudio', 'leavecall', 'deletequeue'],
             help='♫ Leaves voice channel and deletes current queue. (Role specific) ♫')
# only specific roles can use this command
@commands.has_role(role_specific_command_name)
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        new_yt_links_file = open("Code_files/music_bot_files/yt_links.txt", "w")
        yt_current_file = open("Code_files/music_bot_files/yt_current.txt", "w")
        await ctx.send("Ok I'll leave. :cry:")
        voice.stop()
        await voice.disconnect()
    else:
        await ctx.send("BeeBot is not connected to a voice channel. :thinking:")


# bot command to pause audio
@bot.command(name='pause', aliases=['pauseaudio'], help='♫ Pause current audio playing! (Role specific) ♫')
# only specific roles can use this command
@commands.has_role(role_specific_command_name)
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        await ctx.send("Pausing audio! :pause_button:")
        voice.pause()
    else:
        await ctx.send("Currently no audio is playing. :thinking:")


# bot command to resume audio
@bot.command(name='resume', aliases=['resumeaudio'], help='♫ Resume current audio playing! (Role specific) ♫')
# only specific roles can use this command
@commands.has_role(role_specific_command_name)
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        await ctx.send("Resuming audio! :headphones:")
        voice.resume()
    else:
        await ctx.send("The audio is not paused. :thinking:")


# bot command to view current audio
@bot.command(name='viewcurrent', aliases=['currentview', 'currentaudio', 'vcurrent', 'cview', 'current'],
             help='♫ View the current audio! ♫')
async def view_current(ctx):
    try:
        yt_current_file = open("Code_files/music_bot_files/yt_current.txt")
        read_file = yt_current_file.readline()
        message = message_now_playing(read_file)
        await ctx.send(':musical_note:  BeeBot is currently playing ***{}!***  '
                       ':musical_note:'.format(message))
    except:
        await ctx.send("There's no current audio! :open_mouth:")


# bot command to view current queue
@bot.command(name='viewqueue', aliases=['queueview', 'currentqueue', 'viewq', 'qview', 'queue'],
             help='♫ View the current queue! ♫')
async def current_queue(ctx):
    # order of use
    new_yt_links_file = open("Code_files/music_bot_files/yt_links.txt")
    new_yt_links_file.flush()
    count = 0
    title_count = 0
    queue_array = []
    title_array = []
    queue_array_num = []
    final_message = ''
    try:
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if not voice.is_playing:
            await ctx.send('There is not audio in the queue! :flushed: Try the "play" command to add a song! :smile:')
        else:
            # transfer file elements to "queue_array"
            for lines in new_yt_links_file:
                lines = lines.rstrip()
                queue_array.append(lines)
                count += 1

            # check if "yt_links.txt" is empty
            fl_check = Path(r'{}\Code_files\music_bot_files\yt_links.txt'.format(parent_dir))
            if not fl_check.stat().st_size == 0:
                # pop initial "\n"
                fl_check = open('Code_files/music_bot_files/yt_links.txt').readlines()
                if fl_check[0] == '\n' or fl_check[0] == '':
                    queue_array.pop(0)
            # add current song
            if voice.is_playing:
                yt_current_file = open("Code_files/music_bot_files/yt_current.txt")
                yt_current_file.flush()
                current_audio = yt_current_file.readline()
                queue_array.insert(0, current_audio)
            # create an array of "titles"
            for url in queue_array:
                # call the "message_now_playing" function to get YouTube titles
                url_title = message_now_playing(url)

                titles = [url_title]
                title_array.append(titles)
            # create array of formatted elements (Example: "1 : 'current song'")
            for key in title_array:
                title_count += 1
                new_array_line = '{} : {}\n'.format(title_count, str(key)[1:-1])
                queue_array_num.append(new_array_line)
            # create a single final_message string
            for key in queue_array_num:
                final_message += key
            # send queue message
            await ctx.send(':musical_note: :musical_note:  The current queue is: :musical_note: :musical_note:'
                           '\n{}'.format(final_message))
    except:
        # errors
        await ctx.send('There is not audio in the queue! :flushed: Try the \"play\" command to add a song! :smile:')


# bot command to view next audio
@bot.command(name='viewnext', aliases=['nextview', 'nextaudio', 'vnext', 'nview'],
             help='♫ View the next audio! ♫')
async def view_next(ctx):
    try:
        key = 0
        next_yt_links_file = open("Code_files/music_bot_files/yt_links.txt")
        # read first line
        first_line = open('Code_files/music_bot_files/yt_links.txt').readlines()
        # delete if it is a "\n"
        if first_line[key] == '\n':
            lines = open('Code_files/music_bot_files/yt_links.txt').readlines()
            with open('Code_files/music_bot_files/yt_links.txt', 'w') as f:
                f.writelines(lines[1:])
        next_yt_links_file.flush()
        first_line = open('Code_files/music_bot_files/yt_links.txt').readlines()
        # send message
        message = message_now_playing(first_line[key])
        await ctx.send(':musical_note:  BeeBot will be ***{}*** next!'
                       ':musical_note:'.format(message))
    except:
        await ctx.send("There's no next audio! :open_mouth:")


# bot command for tests
@bot.command(name='ztest', help='Testing things! (Please ignore)')
async def ztest(ctx):
    await ctx.send("Ignore me pls c:")


# function to get YouTube titles
def message_now_playing(url):
    # get title name of the YouTube url
    video_id = url.split('=')
    video_id.pop(0)
    params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % '='.join(video_id)}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string
    with urllib.request.urlopen(url) as response:
        response_text = response.read()
        url_title = json.loads(response_text.decode())
    # return YouTube Title as string
    return url_title['title']


# function to download audio and delete link from "yt_links.txt' file
def download_song(ctx):
    try:
        url = get_url()
        yt_current_file = open("Code_files/music_bot_files/yt_current.txt", "w")
        yt_current_file.write(url)

        try:
            # delete first elements from "yt_links" file
            delete_yt_links_file = open("Code_files/music_bot_files/yt_links.txt")
            first_line = open('Code_files/music_bot_files/yt_links.txt').readlines()
            # also delete the '\n' if present
            if first_line[0] == '\n':
                lines = open('Code_files/music_bot_files/yt_links.txt').readlines()
                with open('Code_files/music_bot_files/yt_links.txt', 'w') as f:
                    f.writelines(lines[1:])
                # refresh file
                delete_yt_links_file.flush()
            lines = open('Code_files/music_bot_files/yt_links.txt').readlines()
            with open('Code_files/music_bot_files/yt_links.txt', 'w') as f:
                f.writelines(lines[1:])
            # refresh file
            delete_yt_links_file.flush()
        except:
            print('nothing left in yt_links.txt file')

        # create song file
        song_there = os.path.isfile("Code_files/music_bot_files/song.mp3")
        try:
            # remove "song.mp3" file
            if song_there:
                os.remove("Code_files/music_bot_files/song.mp3")
        except PermissionError:
            print('Error has occurred in \"download_song\" function at song_there!')

        # download audio into "song.mp3"
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                os.rename(file, "Code_files/music_bot_files/song.mp3")

        # calling this "download_song" function again to play next song
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        voice.play(discord.FFmpegPCMAudio("Code_files/music_bot_files/song.mp3"), after=lambda e: download_song(ctx))
        voice.is_playing()

    except:
        print('\"download_song\" function has errors')


# function to download NEXT audio -> goes back to "download_song" loop after
def download_next_song(ctx):
    try:
        url = get_url()
        yt_current_file = open("Code_files/music_bot_files/yt_current.txt", "w")
        yt_current_file.write(url)

        # create song file
        song_there = os.path.isfile("Code_files/music_bot_files/next_song.mp3")
        try:
            # remove "song.mp3" file
            if song_there:
                os.remove("Code_files/music_bot_files/next_song.mp3")
        except PermissionError:
            print('Error has occurred in \"download_next_song\" function at song_there!')

        # download audio into "next_song.mp3"
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                os.rename(file, "Code_files/music_bot_files/next_song.mp3")

        # calling this "download_song" function again to play next song
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        voice.play(discord.FFmpegPCMAudio("Code_files/music_bot_files/next_song.mp3"), after=lambda e: download_song(ctx))
        voice.is_playing()

    except:
        print('\"download_next_song\" function has errors')


# function to get_url from "yt_links.txt" file
def get_url():
    delete_yt_links_file = open("Code_files/music_bot_files/yt_links.txt")
    first_line = open('Code_files/music_bot_files/yt_links.txt').readlines()
    # also delete the '\n' if present
    if first_line[0] == '\n':
        lines = open('Code_files/music_bot_files/yt_links.txt').readlines()
        with open('Code_files/music_bot_files/yt_links.txt', 'w') as f:
            f.writelines(lines[1:])
        # refresh file
        delete_yt_links_file.flush()

    # read first line in "yt_links.txt" file
    fl_yt_links_file = open("Code_files/music_bot_files/yt_links.txt")
    # reload txt file
    fl_yt_links_file.flush()
    new_url = fl_yt_links_file.readline()
    # # ignore first line because it is a "\n" character
    # if new_url == '\n':
    #     new_url = fl_yt_links_file.readline()
    url = new_url
    return url


# does not work c:
async def count_reactions(message):
    channel = message.channel
    choices = {"🇦": "Solos",
               "🇧": "Duos",
               "🇨": "Squads"}

    vote = discord.Embed(title="**[POLL]**", description=" ", color=0x00ff00)
    value = "\n".join("- {} {}".format(*item) for item in choices.items())
    vote.add_field(name="Please vote for the match type:", value=value, inline=True)

    message_1 = await bot.send_message(channel, embed=vote)

    for choice in choices:
        await bot.add_reaction(message_1, choice)

    await asyncio.sleep(60)  # wait for one minute
    message_1 = await bot.get_message(channel, message_1.id)

    counts = {react.emoji: react.count for react in message_1.reactions}

    return


bot.run(TOKEN)
