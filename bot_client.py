# botClient.py
import os
import discord

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True
intents.presences = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game(name="with BEES NUTS (type \"BB "
                                                                                          "help\")"))
    print(f'{client.user.name} has connected to Discord! uwu')
    # # run "clash_dates.py"
    # os.system('python clash_dates.py')
    # run "event_dates.py"
    os.system('python event_dates.py')
    # run "bot.py"
    os.system('python bot.py')

# # for DM-ing members on join
# @client.event
# async def on_member_join(member):
#     await member.create_dm()
#     import pdb;pdb.set_trace()
#     await member.dm_channel.send(
#         f'Hai {member.name}, welcome to my uwu server!'
#     )


client.run(TOKEN)
