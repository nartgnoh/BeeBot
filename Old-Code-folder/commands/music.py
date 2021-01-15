# music.py
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
print('music.py is running!')


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
            add_yt_links_file = open("resource_files/music_bot_files/yt_links.txt", "a")
            add_yt_links_file.write('\n' + yt_search_or_link)
            add_yt_links_file.close()
            open_yt_links_file = open("resource_files/music_bot_files/yt_links.txt")

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
                    # already seen in "download_song()" function
                    # voice.play(discord.FFmpegPCMAudio("resource_files/music_bot_files/song.mp3"),
                    # after=lambda e: download_song(ctx))
                    # voice.is_playing()
                else:
                    # if music is audio is playing already, add audio to queue
                    await ctx.send(':musical_note: Your audio has been added to the queue! :smile:')
    except:
        print("Ignoring errors.")


# bot command to go to next audio in queue by reaction vote
@bot.command(name='next', aliases=['skip'], help='♫ Play the next audio! (Role specific) ♫')
# only specific roles can use this command
@commands.has_role(role_specific_command_name)
async def next(ctx):
    try:
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        # check if the queue is empty
        fl_check = Path(r'{}\resource_files\music_bot_files\yt_links.txt'.format(parent_dir))
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
            await ctx.send(
                "There is not more audio in the queue! :flushed: Try the \"play\" command to add a song! :smile:")
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
        new_yt_links_file = open("resource_files/music_bot_files/yt_links.txt", "w")
        yt_current_file = open("resource_files/music_bot_files/yt_current.txt", "w")
        await ctx.send("Ok I'll leave. :cry:")
        voice.stop()
        voice.disconnect()
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
        yt_current_file = open("resource_files/music_bot_files/yt_current.txt")
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
    new_yt_links_file = open("resource_files/music_bot_files/yt_links.txt")
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
            fl_check = Path(r'{}\resource_files\music_bot_files\yt_links.txt'.format(parent_dir))
            if not fl_check.stat().st_size == 0:
                # pop initial "\n"
                fl_check = open('resource_files/music_bot_files/yt_links.txt').readlines()
                if fl_check[0] == '\n' or fl_check[0] == '':
                    queue_array.pop(0)
            # add current song
            if voice.is_playing:
                yt_current_file = open("resource_files/music_bot_files/yt_current.txt")
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
        next_yt_links_file = open("resource_files/music_bot_files/yt_links.txt")
        # read first line
        first_line = open('resource_files/music_bot_files/yt_links.txt').readlines()
        # delete if it is a "\n"
        if first_line[key] == '\n':
            lines = open('resource_files/music_bot_files/yt_links.txt').readlines()
            with open('resource_files/music_bot_files/yt_links.txt', 'w') as f:
                f.writelines(lines[1:])
        next_yt_links_file.flush()
        first_line = open('resource_files/music_bot_files/yt_links.txt').readlines()
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
        yt_current_file = open("resource_files/music_bot_files/yt_current.txt", "w")
        yt_current_file.write(url)

        try:
            # delete first elements from "yt_links" file
            delete_yt_links_file = open("resource_files/music_bot_files/yt_links.txt")
            first_line = open('resource_files/music_bot_files/yt_links.txt').readlines()
            # also delete the '\n' if present
            if first_line[0] == '\n':
                lines = open('resource_files/music_bot_files/yt_links.txt').readlines()
                with open('resource_files/music_bot_files/yt_links.txt', 'w') as f:
                    f.writelines(lines[1:])
                # refresh file
                delete_yt_links_file.flush()
            lines = open('resource_files/music_bot_files/yt_links.txt').readlines()
            with open('resource_files/music_bot_files/yt_links.txt', 'w') as f:
                f.writelines(lines[1:])
            # refresh file
            delete_yt_links_file.flush()
        except:
            print('nothing left in yt_links.txt file')

        # create song file
        song_there = os.path.isfile("resource_files/music_bot_files/song.mp3")
        try:
            # remove "song.mp3" file
            if song_there:
                os.remove("resource_files/music_bot_files/song.mp3")
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
                os.rename(file, "resource_files/music_bot_files/song.mp3")

        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        # calling this "download_song" function again to play next song
        voice.play(discord.FFmpegPCMAudio("resource_files/music_bot_files/song.mp3"),
                   after=lambda e: download_song(ctx))
        voice.is_playing()

        voice.source.volume = 100
        voice.source = discord.PCMVolumeTransformer(voice.source, volume=1.0)
    except:
        print('No more audio in queue.')


# function to download NEXT audio -> goes back to "download_song" loop after
def download_next_song(ctx):
    try:
        url = get_url()
        yt_current_file = open("resource_files/music_bot_files/yt_current.txt", "w")
        yt_current_file.write(url)

        # create song file
        song_there = os.path.isfile("resource_files/music_bot_files/next_song.mp3")
        try:
            # remove "song.mp3" file
            if song_there:
                os.remove("resource_files/music_bot_files/next_song.mp3")
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
                os.rename(file, "resource_files/music_bot_files/next_song.mp3")

        # calling this "download_song" function again to play next song
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        voice.play(discord.FFmpegPCMAudio("resource_files/music_bot_files/next_song.mp3"),
                   after=lambda e: download_song(ctx))
        voice.is_playing()

    except:
        print('\"download_next_song\" function has errors')


# function to get_url from "yt_links.txt" file
def get_url():
    delete_yt_links_file = open("resource_files/music_bot_files/yt_links.txt")
    first_line = open('resource_files/music_bot_files/yt_links.txt').readlines()
    # also delete the '\n' if present
    if first_line[0] == '\n':
        lines = open('resource_files/music_bot_files/yt_links.txt').readlines()
        with open('resource_files/music_bot_files/yt_links.txt', 'w') as f:
            f.writelines(lines[1:])
        # refresh file
        delete_yt_links_file.flush()

    # read first line in "yt_links.txt" file
    fl_yt_links_file = open("resource_files/music_bot_files/yt_links.txt")
    # reload txt file
    fl_yt_links_file.flush()
    new_url = fl_yt_links_file.readline()
    # # ignore first line because it is a "\n" character
    # if new_url == '\n':
    #     new_url = fl_yt_links_file.readline()
    url = new_url
    return url