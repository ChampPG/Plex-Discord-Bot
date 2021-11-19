import plex_scripts
import discord
import configparser

#TODO make into bot that takes in suggestions fuction and writes to csv files

plex_scripts.create_config()

config = configparser.ConfigParser()
config.read('config.ini')
token = config['DISCORD']['token'] # PUT YOUR TOKEN HERE

client = discord.Client()

plex_scripts.wipe_config()

command_list = [{'Name': '`!help`', 'Def': 'Shows all commands'},
                {'Name': '`!Search=`', 'Def':
                    ' searches up any content with the query. Ex: `!search=The Monkey King`'}]

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    """
    Takes in a user message and decides what command to execute based on command
    :param message: user message from "plex" dicord channel
    :return search working: will return all the items it finds in the plex server
    :return search fail: if search fails it returns that nothing is in the plex
    :return help: returns the help dictionary in a neat format with the name then what it does
    """
    username = str(message.author).strip('#')[0]
    user_message = str(message.content).split("=")
    channel = str(message.channel.name)
    print(f'{username}: {user_message} ({channel})')

    # Check if message if from the bot
    if message.author == client.user:
        return
    if message.channel.name == 'plex':
        if user_message[0].lower() == "!search":
            await message.channel.send("Please hold on for a few minutes :)")
            list_of_search = plex_scripts.search_plex(user_message[1])
            if list_of_search != "Nothing In Plex":
                index = 1
                print(list_of_search)
                for item in list_of_search:
                    await message.channel.send(f'{index}: {item}')
                    index+=1
                return
            else:
                await message.channel.send("Nothing In Plex: Please change search query")
                return
        if user_message[0].lower() == '!help':
            for help_command in command_list:
                await message.channel.send(f"{help_command['Name']} | {help_command['Def']} ")
            return


client.run(token)