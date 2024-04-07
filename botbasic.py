import plex_scripts  # imports my python file
import discord       # discord library
import configparser  # for taking in .ini files

plex_scripts.create_config() # Decrypts encryptedconfig.ini
config = configparser.ConfigParser()
config.read('config.ini')
token = config['DISCORD']['token'] # PUT YOUR TOKEN HERE
client = discord.Client()
plex_scripts.wipe_config() # Clears config.ini
token = "*" * 5 # converts token to *****

command_list = [{'Name': '`!help`', 'Def': 'Shows all commands'},
                {'Name': '`!Search =`', 'Def':
                    ' Searches up any content (TV or Movies) with the query. | Example: `!search = The Monkey King`'},
                {'Name': '`!suggest =`', 'Def': ' Adds a suggestion (TV or Movie) to the list to be put on Plex. | '
                                                'Example (Year): `!suggest = The Monkey King (2014)` '
                                                'or `!suggest = The Monkey King (N/A)` if year is unknown'},
                {'Name': '`!GetSuggestionCSV`', 'Def': 'Returns a .csv of all current suggestions '
                                                       '**RUN THIS BEFORE !suggest** | Example: `!GetSuggestionCSV`'},
                {'Name': '`!MoviesCSV =`', 'Def': 'Returns a .csv of all the movies on the Plex | Example: `!MoviesCSV`'}]

@client.event
async def on_ready():
    print('Bot is online! {0.user}'.format(client))
    await client.change_presence(activity=discord.Game(name="!help for commands"))

@client.event
async def on_message(message):
    """
    Takes in a user message and decides what command to execute based on command
    :param message: user message from "plex" dicord channel
    :return: return statement is based on if statements return is seen below.

    !search (working): will return all the items it finds in the plex server
    !search (fail): if search fails it returns that nothing is in the plex
    !MoviesCSV: returns a csv file of all the movies
    !help: returns the help dictionary in a neat format with the name then what it does
    !GetSuggestionCSV: returns the suggestion csv file
    !suggest: returns the suggestion csv file after use adds suggestion
    ! (error): tells the user to enter !help to figure out commands
    """
    username = str(message.author).strip('#')
    user_message = str(message.content).split(" = ")
    channel = str(message.channel.name)
    print(f'{username}: {user_message} ({channel})')

    # Check if message if from the bot
    if message.author == client.user:
        return
    if message.channel.name == 'plex' or message.channel.name == 'bot-cmd': # makes it so bot works with channel named
                                                                            # plex or bot-cmd
        # searches through the plex and returns all the content that contains the search
        if user_message[0].lower() == "!search":
            await message.channel.send("Please hold on for a few minutes :)")
            list_of_search = plex_scripts.search_plex(user_message[1])
            if list_of_search != "Nothing In Plex":
                index = 1
                # print(list_of_search)
                for item in list_of_search:
                    if list_of_search.index(item)+1 == len(list_of_search):
                        await message.channel.send(f'`{index}`: {item}')
                        await message.channel.send("That is all I can find.")
                    else:
                        await message.channel.send(f'`{index}:` {item}')
                    index+=1
                return
            else:
                await message.channel.send("Nothing In Plex: Please change search query")
                return

        # returns a csv of all the movies
        elif user_message[0] == '!MoviesCSV':
            await message.channel.send(file=discord.File("Movies_list.csv"))

        # displays all the commands and examples for them
        elif user_message[0].lower() == '!help':
            for help_command in command_list:
                await message.channel.send(f"{help_command['Name']} | {help_command['Def']}")
            return

        # get the list of suggestions
        elif user_message[0] == "!GetSuggestionCSV":
            await message.channel.send(file=discord.File("suggestions.csv"))

        # allows people to suggest a piece of content they would like to see
        elif user_message[0].lower() == '!suggest':
            await message.channel.send(plex_scripts.suggestion(user_message[1]))
            await message.channel.send("Below is the current list of suggestions")
            await message.channel.send(file=discord.File("suggestions.csv"))

        # invalid command fall back
        elif user_message[0].lower()[:1] == '!':
            await message.channel.send("Invalid Command: Type `!help` if you need help figuring out commands.")

client.run(token)