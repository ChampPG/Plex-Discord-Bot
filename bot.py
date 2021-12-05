import plex_scripts               # imports my python file
from discord.ext import commands  # discord.ext commands library
import discord                    # discord library
import configparser               # for taking in .ini files


plex_scripts.create_config() # Decrypts encryptedconfig.ini
config = configparser.ConfigParser()
config.read('config.ini')
token = config['DISCORD']['token'] # PUT YOUR TOKEN HERE
client = commands.Bot(command_prefix='!', help_command=None)
plex_scripts.wipe_config() # Clears config.ini


@client.event
async def on_ready():
    print('Bot is online! {0.user}'.format(client))
    # await client.change_presence(activity=discord.Game(name="!help for commands"))


@client.command()
async def help(ctx):
    """
    If user types !help gives user a list of commands. This uses a list of dicts for the commands
    :return: The command list
    """
    command_list = [{'Name': '`!help`', 'Def': 'Shows all commands'},
                    {'Name': '`!Search =`', 'Def':
                        ' Searches up any content (TV or Movies) with the query. | Example: `!search = The Monkey King`'},
                    {'Name': '`!suggest =`', 'Def': ' Adds a suggestion (TV or Movie) to the list to be put on Plex. | '
                                                    'Example (Year): `!suggest = The Monkey King (2014)` '
                                                    'or `!suggest = The Monkey King (N/A)` if year is unknown'},
                    {'Name': '`!GetSuggestionCSV`', 'Def': 'Returns a .csv of all current suggestions '
                                                           '**RUN THIS BEFORE !suggest** | Example: `!GetSuggestionCSV`'},
                    {'Name': '`!MoviesCSV =`',
                     'Def': 'Returns a .csv of all the movies on the Plex | Example: `!MoviesCSV`'}]
    if ctx.channel.name == 'plex':
        for help_command in command_list:
            await ctx.send(f"{help_command['Name']} | {help_command['Def']}")


@client.command()
async def search(ctx):
    """
    Allows user to search through movies with a key word user puts in.
    :return: Movies & tv episodes that fall under the key work. If movie returns trailer
    """
    await ctx.send("Please hold on for a few minutes :)")
    user_message = str(ctx.message.content).split(" = ")
    list_of_search = plex_scripts.search_plex(user_message[1])
    if list_of_search != "Nothing In Plex":
        index = 1
        # print(list_of_search)
        for item in list_of_search:
            if list_of_search.index(item) + 1 == len(list_of_search):
                await ctx.send(f'`{index}`: {item}')
                await ctx.send("That is all I can find.")
            else:
                await ctx.send(f'`{index}:` {item}')
            index += 1
        return
    else:
        await ctx.send("Nothing In Plex: Please change search query")
        return


@client.command()
async def MoviesCSV(ctx):
    """
    Sends Movies_list.csv file to user
    :return: Movies_list.csv file
    """
    await ctx.send(file=discord.File("Movies_list.csv"))

@client.command()
async def suggest(ctx):
    """
    Allows users to suggest movies and put that into the suggestions.csv file
    :return: the suggestions.csv file to show that it has been added
    """
    user_message = str(ctx.message.content).split(" = ")
    await ctx.send(plex_scripts.suggestion(user_message[1]))
    await ctx.send("Below is the current list of suggestions")
    await ctx.send(file=discord.File("suggestions.csv"))


@client.command()
async def GetSuggestionCSV(ctx):
    """
    Gives user the suggestions.csv file
    :return: suggestion.csv file is given to user
    """
    await ctx.send(file=discord.File("suggestions.csv"))


@client.event
async def on_command_error(ctx, error):
    """
    If user types invalid command gives user a message saying they need to type !help
    :param error: error message
    :return: Invalid Command: Type `!help` if you need help figuring out commands.
    """
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid Command: Type `!help` if you need help figuring out commands.")

client.run(token)