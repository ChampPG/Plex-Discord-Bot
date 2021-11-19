#!/usr/bin/env python3

#TODO add argparse

import os                                 # needed to scan through directories
from shutil import copyfile               # used to copy files
import csv                                # for csv files
from moviepy.editor import VideoFileClip  # get information on video files
from alive_progress import alive_bar      # progress bar
import time                               # dependency for alive_progress
from plexapi.myplex import MyPlexAccount  # PleX api
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

def wipe_config():
    """
    wipes config.ini file
    :return: wiped config.ini file
    """
    wipe_file = open('config.ini', 'w')
    wipe_file.close()

selection = input("Please enter 'rename', 'csv', 'bot_mode', or 'plex': ")

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
        current_path = r'C:\Users\paul.gleason\Documents\Test_Current'
    new_path = input("Please enter where you want them to go: ")

    for files in os.listdir(current_path):
        if not os.path.isdir(new_path + '/' + files[:-3]):
            os.mkdir(new_path + '/' + files[:-3])
            copyfile(current_path + '/' + files, new_path + '/' + files[:-3] + '/' + files)
            print(files[:-3], 'has been made and', files, 'has been moved')
        else:
            print(files[:-3], 'Dir is already made')


def get_files():
    """
    Gets all the files in a certain directory
        Files must be a file type in the extension_list

    :return compile_csv: If csv was selected at the start this will take all the files in the directory and put
    them into a csv file (list),(str)
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
    if selection == 'csv':
        return compile_csv(file_list, path_to_files)
    if selection == 'plex':
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

    movies_to_check.sort()

    path_to_csv = '/mnt/sda2/plex_scripts/Movies_Check_List.csv'
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
    path_to_csv = '/mnt/sda2/Movies_list.csv'
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


#TODO make suggestion function that writes inputs to a csv
def suggestion(suggest):
    """
    Takes in a user suggesiton and writers it to a csv file
    :param suggest: user suggestion (str)
    :return: list of what is in the suggestion queue (list)
    """
    path_to_csv = '/mnt/sda2/Movies_list.csv'
    list_of_media = []

    # read what is already in the list
    with open(path_to_csv, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        # read file row by row
        for row in reader:
            list_of_media.append(row)

    # add suggestion to list
    list_of_media.append(suggest)

    # writer
    with open('persons.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile)
        # write file row by row
        for item in list_of_media:
            writer.writerow(item)

    return list_of_media


#TODO make a search function that will search for files in plex
def search_plex(search):
    """
    Takes in the name from the discord user in the plex chat.
    Then looks for all files that contain the "search" in it's name
    :param search: Name of search (str)
    :return: list of files that contain name
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

    media_list = []
    for video in plex.search(search):
        if video.TYPE == 'movie':
            media_list.append('%s (%s)' % (video.title, video.TYPE))
        if video.TYPE == 'episode':
            shows_list = plex.library.section('TV Shows')
            for show in shows_list.all():
                for episode in plex.library.section('TV Shows').get(show.title).episodes():
                    if video.title == episode.title:
                        media_list.append('%s %s %s (%s)' %(show.title, "|", video.title, video.TYPE))

    if len(media_list) > 0:
        return media_list
    else:
        return "Nothing In Plex"

# Selects which path to take from user input
if selection == 'csv':
    get_files()
    wipe_config()
    input("Done! press any key to terminate program.")
if selection == 'rename':
    rename()
    wipe_config()
    input("Done! press any key to terminate program.")
if selection == 'plex':
    wipe_config()
    get_files()
