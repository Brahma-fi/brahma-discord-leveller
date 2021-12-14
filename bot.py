import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='+', help_command=None)

def filepath(filename):
    return f"./out/{filename}"

@bot.event
async def on_ready():
    activity = discord.Game(name="+help")
    await bot.change_presence(status=discord.Status.idle, activity=activity)
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name="scan-users")
async def scan_users(ctx):
    channel = discord.utils.get(ctx.guild.channels, name="voting")
    messages = await channel.history(limit=5000).flatten()
    print(f"{len(messages)} accounts in voting")
    users = []

    for message in messages:
        users.append({
            "user_name": str(message.author),
            "user_id": message.author.id,
            "address": message.content
        })

    json_users = json.dumps(users, indent=4)

    with open(filepath("users.json"), "w") as outfile:
        outfile.write(json_users)

@bot.command(name="scan-messages")
async def scan_messages(ctx):
    user_list = []
    with open(filepath("users.json"), "r") as readfile:
        users = json.load(readfile)
        user_list = [user["user_id"] for user in users]

    print(user_list)

    user_messages = {}
    channels = {}

    with open("config.json", "r") as readfile:
        channels = json.load(readfile)
    
    for channel_name in list(channels.keys()):
       channel = discord.utils.get(ctx.guild.channels, id=channels[channel_name]["id"])
       messages = await channel.history(limit=5000).flatten()
       print(f"{len(messages)} messages found in {channel.name}") 

       for message in messages:
           if len(message.content) > 10:
               if message.author.id in user_list:
                try:
                    user_messages[str(message.author)][channel_name] += len(message.content)
                except:
                    try:
                        user_messages[str(message.author)][channel_name] = len(message.content)
                    except:
                        user_messages[str(message.author)] = {}
                        user_messages[str(message.author)][channel_name] = len(message.content)
    
    user_messages_json = json.dumps(user_messages, indent=4)

    with open(filepath("user_messages.json"), "w") as outfile:
        outfile.write(user_messages_json)

@bot.command(name="karma")
async def karma(ctx):
    user_messages = {}
    with open(filepath("user_messages.json"), "r") as readfile:
        user_messages = json.load(readfile)

    user_addresses = {}
    with open(filepath("users.json"), "r") as readfile:
        users = json.load(readfile)
        for user in users:
            user_addresses[user["user_name"]] = user["address"]

    channels = {}
    with open("config.json", "r") as readfile:
        channels = json.load(readfile)

    voters, depositors = [[],[]]
    with open("voters.json", "r") as readfile:
        voters = json.load(readfile)
    with open("depositors.json", "r") as readfile:
        depositors = json.load(readfile)

    user_karma = {}
    for user in list(user_messages.keys()):
        karma = 0
        stats = user_messages[user]
        user_multiplier = 1

        if user_addresses[user] in depositors:
            user_multiplier = 1.4
        elif user_addresses[user] in voters:
            user_multiplier = 1.5

        for channel_name in list(stats.keys()):
            karma += (stats[channel_name]*channels[channel_name]["weight"]*user_multiplier)
        
        user_karma[user] = {
            "address": user_addresses[user],
            "karma": karma
        }

    user_karma_json = json.dumps(user_karma, indent=4)

    with open(filepath("user_karma.json"), "w") as outfile:
        outfile.write(user_karma_json)

    print(f"karmas of {len(user_messages.keys())} users calculated")

    
bot.run(token, bot=True, reconnect=True)