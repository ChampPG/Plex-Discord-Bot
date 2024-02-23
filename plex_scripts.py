#!/usr/bin/env python3

#TODO add argparse

import os                                 # needed to scan through directories
from shutil import copyfile               # used to copy files
import csv                                # for csv files
import requests                           # for moviedb api requests
from moviepy.editor import VideoFileClip  # get information on video files
from alive_progress import alive_bar      # progress bar
import time                               # dependency for alive_progress
from plexapi.myplex import MyPlexAccount  # MyPlexAccount api
import configparser                       # Users .ini file for configuration
from cryptography.fernet import Fernet    # Encryption for config.ini and encryptedconfig.ini


def create_config():
    """
    Files the config.ini with the decrypted information from the encryptedconfig.ini
    :return: config.ini with all decrypted information
    """
    with open('keyconfig', 'rb') as filekey:
        key = filekey.read()

    fernet = Fernet(key)

    with open('encryptedconfig.ini', 'rb') as encrypted_file:
        encrypted = encrypted_file.read()

    decrypted = fernet.decrypt(encrypted)

    with open('config.ini', 'wb') as decrypted_file:
        decrypted_file.write(decrypted)


def encrypt_config():
    """
    Allows the ability to add new information to the config.ini before it becomes encrypted.
    :return: encryptedconfig.ini
    """
    with open('keyconfig', 'rb') as filekey:
        key = filekey.read()

    fernet = Fernet(key)

    with open('config.ini', 'rb') as decrypted_file:
        decrypted = decrypted_file.read()

    decrypted = fernet.encrypt(decrypted)

    with open('encryptedconfig.ini', 'wb') as decrypted_file:
        decrypted_file.write(decrypted)


def wipe_config():
    """
    wipes config.ini file
    :return: wiped config.ini file
    """
    wipe_file = open('config.ini', 'w')
    wipe_file.close()


selection = input("Please enter 'rename', 'Make_Movie_csv', 'bot_mode', 'plex_check', or 'precopy': ")
                # selection of what function you want to use
                # bot_mode does nothing expect for let the code run for the bot
                # plex_check creates a csv file of the plex movies that much be checked
                # rename is for renaming movie files
                # Make_Movie_csv makes a csv of all the movies


def precopy_check():
    """
    Checks main drive to see if folder is already there and if so write it down
    :return: a csv with all the names of moves that are copies
    """
    path_type = input("Please enter custom or static: ")
    if path_type == 'custom':
        download_path = input("Please enter current path of files: ")
    elif path_type == 'static':
        download_path = '/home/plexadmin/Downloads/Plex/Movies/'
    # new_path = input("Please enter where you want them to go: ")
    master_path = '/home/plexadmin/Downloads/Plex/Movies/'

    download_path_list = []
    master_path_list = []

    for download_dirs in os.listdir(download_path):
        download_path_list.append(download_dirs)

    for master_dirs in os.listdir(master_path):
        master_path_list.append(master_dirs)

    write_list = []
    for item in download_path_list:
        if item in master_path_list:
            write_list.append({'Name': item})

    headers = ["Name"]

    with open('precopy.csv', 'w', encoding='ISO-8859-1', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(write_list)

    delete = input("Please enter 'd' to delete these files or enter to continue: ")
    if delete == 'd':
        for folder in write_list:
            os.remove(download_path + folder['Name'])


def rename():
    """
    Renames files in a directory
        File Format: NAME (YEAR).extension
        The extension only works if it is 3 chars long

    :return: Takes file renames it and puts it in a folder with the same name as the file (NULL)
    """
    path_type = input("Please enter custom or static: ")
    if path_type == 'custom':
        current_path = input("Please enter current path of files: ")
    elif path_type == 'static':
        current_path = '/home/plexadmin/Downloads/Plex/Epic Films 4/'
    # new_path = input("Please enter where you want them to go: ")
    new_path = '/home/plexadmin/Downloads/Plex/Movies/'

    for files in os.listdir(current_path):
        if not os.path.isdir('/dev/sda2/Movies/' + files[:files.find('(')-1]):
            extention = files[-4:]
            os.mkdir(new_path + '/' + files[:files.find('(')-1])
            copyfile(current_path + '/' + files, new_path + '/' + files[:files.find('(')-1] + '/' +
                     files[:files.find('(')-1] + extention)
            print(files[:files.find('(')-1], 'has been made and', files[:files.find('(')-1] + extention,
                  'has been moved')
        else:
            print(files[:files.find('(')-1], 'Dir is already made')


def get_files():
    """
    Gets all the files in a certain directory
        Files must be a file type in the extension_list

    :return compile_csv: If Make_Movie_csv was selected at the start this will take all the files in the directory and
    put them into a csv file (list),(str)
    :return plexcheck: If plex was selected at the start this will check all the folders in the selected directory and
    check the names to all the files in the selected plex library (list)
    """
    path_type = input("Please enter custom or static: ")
    if path_type == 'custom':
        path_to_files = input("Please enter current path of files: ")
    elif path_type == 'static':
        path_to_files = '/mnt/sda2/Movies'

    extention_list = ['mp4', 'mov', 'mkv',
                      'avi', 'wmv', 'flv',
                      'f4v', 'swf', 'mpg',
                      'mp2', 'mpe']
    file_list = []
    directory_list = []
    for directories in os.listdir(path_to_files):
        # print(directories)
        directory_list.append(directories)
        try:
            for files in os.listdir(path_to_files + '/' + directories):
                if files[-3:] in extention_list:
                    file_list.append(files)
        except NotADirectoryError:
            print('This current directory is invalid.')
            path_to_files = input("Please enter current path of files: ")
            for files in os.listdir(path_to_files + '/' + directories):
                if files[-3:] in extention_list:
                    file_list.append(files)

    file_list.sort()
    if selection == 'Make_Movie_csv':
        return compile_csv(file_list, path_to_files)
    if selection == 'plex_check':
        return plexcheck(directory_list)


def plexcheck(list_of_files):
    """
    Checks all the files from selected plex directory and checks them with the files in selected directory
    to see if they all show up.

    :param list_of_files: Takes in all the files in the selected directory from get_files() (list)
    :return: A CSV that has been premade and puts all the names of the files that don't show up in plex (CSV)
    """
    create_config()
    config = configparser.ConfigParser()
    config.read('config.ini')
    username = config['PLEX']['username']  # username of plex admin from config.ini
    password = config['PLEX']['password']  # password of plex admin from config.ini
    server_name = config['PLEX']['server_name']  # takes in server name from config.ini
    wipe_config()
    # gets plex content
    account = MyPlexAccount(username, password)
    plex = account.resource(server_name).connect()

    movies_list = []
    movies = plex.library.section('Movies')

    movies_to_check = []
    with alive_bar(total=len(list_of_files), bar='blocks') as bar:

        for video in movies.all():
            time.sleep(.005)
            movies_list.append(video.title)
            bar()

        for movie in range(len(movies_list)):
            movies_list[movie] = movies_list[movie].lower()

        for video_check in list_of_files:
            if video_check.lower() not in movies_list and '[' not in video_check:
                movies_to_check.append({'Current Name': video_check})

    movies_to_check = sorted(movies_to_check, key=lambda d: d['Current Name'])

    path_to_csv = 'Movies_Check_List.csv'
    headers = ['Current Name']
    with open(path_to_csv, 'w', encoding='ISO-8859-1', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(movies_to_check)


def compile_csv(list_of_files, directory_path):
    """
    Takes all the files from list_of_files and uses the directory_path to add all the files to a csv file

    :param list_of_files: list of file at path (list)
    :param directory_path: path to the files (str)
    :return: a csv with the headers and puts the name | File Type | Resolution | Length (Minutes) (CSV)
    """
    # path_to_csv = input("Please enter path to CSV file: ")
    path_to_csv = 'Movies_list.csv'
    headers = ['Name', 'File Type', 'Resolution', 'Length (Minutes)']
    split_file_list = []

    with alive_bar(total=len(list_of_files), bar='blocks') as bar:  # Creates the bar
        time.sleep(.005)
        for file in list_of_files:
            time.sleep(.005)
            print(file)
            try:
                clip = VideoFileClip(directory_path + '/' + file[:-4] + '/' + file)
                split_file_list.append({'Name': file.split('.')[0], 'File Type': file[-3:],
                                        'Resolution': str(clip.w) + 'x' + str(clip.h),
                                        'Length (Minutes)': int(clip.duration / 60)})
            except UnicodeDecodeError:
                print('UnicodeDecodeError at:', file)
            bar()  # updates bar every loop

    with open(path_to_csv, 'w', encoding='ISO-8859-1', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(split_file_list)


def suggestion(suggest):
    """
    Takes in a user suggesiton and writers it to a csv file
    :param suggest: user suggestion (str)
    :return: list of what is in the suggestion queue (list)
    """
    path_to_csv = 'suggestions.csv'
    list_of_media = []

    if suggest[-1] != ')':
        return 'Please enter format correctly Ex: `!suggest = The Monkey King (2014)`'

    try:
        name = suggest.split(" (")[0]
        year = suggest.split(" (")[1][0:-1]
    except IndexError:
        return 'Please enter format correctly Ex: `!suggest = The Monkey King (2014)`'

    headers = ['Name', 'Year']
    # read what is already in the list
    with open(path_to_csv, 'r', encoding='ISO-8859-1', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        # read file row by row
        for row in reader:
            list_of_media.append(row)

    # add suggestion to list
    list_of_media.append({'Name': name, 'Year': year})

    # writer
    with open(path_to_csv, 'w', encoding='ISO-8859-1', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(list_of_media)

    return "Thank You for the suggestion"


def search_plex(search):
    """larity of code and layout
    Takes in the name from the discord user in the plex chat.
    Then looks for all files that contain the "search" in it's name
    :param search: Name of search (str)
    :return: list of files that contain name
    """
    # sets config
    create_config()
    config = configparser.ConfigParser()
    config.read('config.ini')
    username = config['PLEX']['username']  # username of plex admin from config.ini
    password = config['PLEX']['password']  # password of plex admin from config.ini
    server_name = config['PLEX']['server_name']  # takes in server name from config.ini
    api_key = config['MOVIEDB']['key']
    wipe_config()
    # gets plex content
    account = MyPlexAccount(username, password)
    username = "*" * 5
    password = "*" * 5

    # connect to server
    # print(f"About to connect to {server_name}")
    print("Connecting......")
    plex = account.resource(server_name).connect()
    # print(f"Connected to '{server_name}'")
    print("Connected")
    print("Searching.......")

    media_list = []
    # movies which have the same name as another movie
    problem_movies = [{'Name': 'The Monkey King', 'id': '119892'}]
    for video_search in plex.search(search):
        if video_search.TYPE == 'movie':
            # get movie id
            param_dict = {'api_key': api_key,
                          'language': 'en-US',
                          'query': video_search.title,
                          'page': 1,
                          'include_adult': 'true'}
            api_url = 'https://api.themoviedb.org/3/search/movie?'
            movie_id_getter = requests.get(api_url, param_dict)
            movie_id = movie_id_getter.json()
            if movie_id['total_results'] == 0:
                # wanted to try to do a different way of formatting
                # adds movie to
                media_list.append('%s (%s) %s' % (video_search.title, video_search.TYPE, "Couldn't find a trailer."))
            else:
                param_dict_movie = {'api_key': api_key,
                                    'language': 'en-US'}
                movie_data = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id['results'][0]['id']}/videos?",
                                        param_dict_movie)
                key = movie_data.json()
                try:
                    # print(key)
                    media_list.append('%s (%s - %s) %s %s' % (video_search.title, video_search.TYPE,
                                                              movie_id['results'][0]['release_date'][:4], '|',
                                                              f"https://www.youtube.com/watch?v={key['results'][0]['key']}"))
                except IndexError:# if movie hasn't been release
                    # look through problem movies
                    hit = []# if movie name is the same as the movie that has been searched
                    for index in range(len(problem_movies)):
                        for Name in problem_movies[index]:
                            if video_search.title == problem_movies[index][Name]:
                                hit.append(index)
                                param_dict_movie = {'api_key': api_key,
                                                    'language': 'en-US',
                                                    'page': 1}
                                movie_data = requests.get(
                                    f"https://api.themoviedb.org/3/movie/{problem_movies[index]['id']}/videos?",
                                    param_dict_movie)
                                key = movie_data.json()
                                media_list.append('%s (%s - %s) %s %s' % (video_search.title, video_search.TYPE,
                                                                          key['results'][0]['published_at'][:4], '|',
                                                                     f"https://www.youtube.com/watch?v={key['results'][0]['key']}"))
                            elif index not in hit:
                                media_list.append('%s (%s - %s) %s' % (video_search.title, video_search.TYPE,
                                                                       movie_id['results'][0]['release_date'][:4],
                                                                       "Couldn't find a trailer."))
        # if video is an episode
        if video_search.TYPE == 'episode':
            shows_list = plex.library.section('TV Shows')
            for show in shows_list.all():
                for episode in plex.library.section('TV Shows').get(show.title).episodes():
                    if video_search.title == episode.title:
                        media_list.append('%s %s %s (%s %s)' % (show.title, "|", video_search.title, "TV",
                                                                video_search.TYPE))

    api_key = "*" * 5
    if len(media_list) > 0:
        return media_list
    else:
        return "Nothing In Plex"


def jacob():
    """

    :return:
    """
    create_config()
    config = configparser.ConfigParser()
    config.read('config.ini')
    username = config['PLEX']['username']  # username of plex admin from config.ini
    password = config['PLEX']['password']  # password of plex admin from config.ini
    my_server = config['PLEX']['server_name']  # takes in server name from config.ini
    jacobs_server = "The Hive"
    wipe_config()

    account = MyPlexAccount(username, password)
    my_plex = account.resource(my_server).connect()
    print('connect to', my_server)
    jacob_plex = account.resource(jacobs_server).connect()
    print('connect to', jacobs_server)

    my_movies = my_plex.library.section('Movies')
    jacob_movies = jacob_plex.library.section('Movies')

    my_movie_list = []
    for my_movie in my_movies.all():
        my_movie_list.append(my_movie.title)

    jacob_movie_list = []
    for jacob_movie in jacob_movies.all():
        jacob_movie_list.append(jacob_movie.title)

    movie_list = []
    with alive_bar(total=len(jacob_movies.all()), bar='blocks') as bar:  # Creates the bar
        time.sleep(.005)
        for movie in my_movie_list:
            if movie not in jacob_movie_list:
                movie_list.append({"Name": movie})
            bar()

    headers = ["Name"]

    with open('jacob.csv', 'w', encoding='ISO-8859-1', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(movie_list)

# Selects which path to take from user input
if selection == 'Make_Movie_csv':
    get_files()
    wipe_config()
elif selection == 'rename':
    rename()
elif selection == 'plex_check':
    wipe_config()
    get_files()
elif selection == 'precopy':
    precopy_check()

# test search
elif selection == 'search':
    print(search_plex('Monkey'))

# for adding information to the config
elif selection == "open":
    create_config()
elif selection == "close":
    encrypt_config()
    wipe_config()
elif selection == "clear":
    wipe_config()

# test with friends server
elif selection == 'jacob':
    jacob()