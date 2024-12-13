import requests
import jsons

import uuid
import pathlib
import logging
import sys
import os
import base64
import time
import random
import webbrowser

from configparser import ConfigParser
from getpass import getpass



class User:
  def __init__(self, row):
    self.userid = row[0]
    self.username = row[1]
    self.pwdhash = row[2]


class Playlist:
  def __init__(self, row):
    self.playlistid = row[0]
    self.userid = row[1]
    self.playlist_name = row[2]
    self.num_songs = row[3]

class Song:
  def __init__(self, row):
    self.songid = row[0]
    self.playlistid = row[1]
    self.artist_name = row[2]
    self.song_name = row[3]
    self.spotify_songid = row[4]

class Token:
  def __init__(self, row):
    self.token = row[0]
    self.userid = row[1]
    self.expiration_utc = row[2]

def prompt():
  """
  Prompts the user and returns the command number

  Parameters
  ----------
  None

  Returns
  -------
  Command number entered by user (0, 1, 2, ...)
  """
  try:
      print()
      print(">> Enter a command:")
      print("   0 => end")
      print("   1 => create user")
      print("   2 => login")
      print("   3 => authenticate token")
      print("   4 => top songs")
      print("   5 => check playlists")
      print("   6 => create playlist")
      print("   7 => random playlist genre-nator")
      print("   8 => most popular song in playlist")
      print("   9 => logout")

      cmd = input()

      if cmd == "":
        cmd = -1
      elif not cmd.isnumeric():
        cmd = -1
      else:
        cmd = int(cmd)

      return cmd

  except Exception as e:
      print("**ERROR")
      print("**ERROR: invalid input")
      print("**ERROR")
      return -1


############################################################
#
# login
#
def create_user(baseurl):
  try:
    print("Time to create a new user!")
    username = input("Enter a username: ")
    password = input("Enter a password: ")
    
    #
    # call the web service to upload the PDF:
    #
    api = '/create_user'
    url = baseurl + api

    data = {"username": username, "password": password}    

    res = requests.post(url, json=data)

    #
    # clear password variable:
    #
    password = None

    #
    # let's look at what we got back:
    #
    if res.status_code == 401:
      #
      # authentication failed:
      #
      body = res.json()
      print(body)
      return None

    if res.status_code == 200: #success
      pass
    elif res.status_code in [400, 500]:
      # we'll have an error message
      body = res.json()    
      if "Duplicate" in body:
        print("Uh oh, looks like there's already an existing username. Choose a new username!")
      else:
        print("**Error:", body)
      return
    else:
      # failed:
      print("**ERROR: Failed with status code:", res.status_code)
      print("url: " + url)
      return

    #
    # success, extract token:
    #
    body = res.json()

    userid = body

    print("Created user, your userid is :", userid)
    return token

  except Exception as e:
    logging.error("**ERROR: create_user() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return None


############################################################
#
# login
#
def login(auth_url):
  try:
    username = input("username: ")
    password = getpass()
    duration = input("# of minutes before expiration? [ENTER for default] ")

    #
    # build message:
    #
    if duration == "":  # use default
      data = {"username": username, "password": password}
    else:
      data = {"username": username, "password": password, "duration": duration}

    #
    # call the web service to upload the PDF:
    #
    api = '/auth'
    url = auth_url + api

    res = requests.post(url, json=data)

    #
    # clear password variable:
    #
    password = None

    #
    # let's look at what we got back:
    #
    if res.status_code == 401:
      #
      # authentication failed:
      #
      body = res.json()
      print(body)
      return None

    if res.status_code == 200: #success
      pass
    elif res.status_code in [400, 500]:
      # we'll have an error message
      body = res.json()
      print("**Error:", body)
      return
    else:
      # failed:
      print("**ERROR: Failed with status code:", res.status_code)
      print("url: " + url)
      return

    #
    # success, extract token:
    #
    body = res.json()

    token = body

    print("logged in, token:", token)
    return token

  except Exception as e:
    logging.error("**ERROR: login() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return None


############################################################
#
# authenticate
#
def authenticate(auth_url, token):
  try:
    if token is None:
      print("No current token, please login")
      return

    print("token:", token)

    #
    # build message:
    #
    data = {"token": token}

    #
    # call the web service to upload the PDF:
    #
    api = '/auth'
    url = auth_url + api

    res = requests.post(url, json=data)

    #
    # let's look at what we got back:
    #
    if res.status_code == 401:
      #
      # authentication failed:
      #
      body = res.json()
      print(body)
      return

    if res.status_code == 200: #success
      pass
    elif res.status_code in [400, 500]:
      # we'll have an error message
      body = res.json()
      print("**Error:", body)
      return
    else:
      # failed:
      print("**ERROR: Failed with status code:", res.status_code)
      print("url: " + url)
      return

    #
    # success, token is valid:
    #
    print("token is valid!")
    return

  except Exception as e:
    logging.error("**ERROR: authenticate() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
#
# top_songs
#
def top_songs(baseurl, token):
  try:
    print("Here is the weekly top 100 songs (according to Billboard)!")

    api = "/topsongs"

    url = baseurl + api
    data = {"spotify_token": spotify_token, "token": None, "action": None}    

    res = requests.post(url, json=data)
    
    if res.status_code == 200:
      data = res.json()
      tracks = data['tracks']['items']
      count = 1
      for track in tracks:
        track_name = track['track']['name']
        artist_name = track['track']['artists'][0]['name']
        print(f"{count}. {track_name} by {artist_name}")
        count += 1
    else:
      print("Error: " + str(res.status_code))
      print(res.text)

    return
  except Exception as e:
    logging.error("**ERROR: top_songs() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  

############################################################
#
# playlists
#
def playlists(baseurl, token):
  try:
    if token is None:
      print("No current token, please login")
      return
    
    print("Time to check your playlists!")
    playlist_name = input("Enter the name of the playlist you wish to check! If you want to see all your playlists, press ENTER: ")

    data = {"token": token, "playlist_name": playlist_name, "new?": False}

    api = '/playlist'
    url = baseurl + api

    res = requests.post(url, json=data)

    if res.status_code == 401:
      body = res.json()
      print(body)
      return

    if res.status_code == 200: 
      pass
    elif res.status_code in [400, 500]:
      body = res.json()
      print("**Error:", body)
      return
    else:
      print("**ERROR: Failed with status code:", res.status_code)
      print("url: " + url)
      return

    playlists = res.json()

    if playlists == None:
      print("Requested playlist does not exist. Please try a different playlist name.")
      return

    for playlist in playlists:
      data = {"playlist_id": playlist[0]}

      api = '/songs'
      url = baseurl + api

      res = requests.post(url, json=data)
      if res.status_code == 200: 
        pass
      elif res.status_code in [400, 500]:
        body = res.json()
        print("**Error:", body)
        return
      else:
        print("**ERROR: Failed with status code:", res.status_code)
        print("url: " + url)
        return

      songs = res.json()

      print()
      print("Playlist ID:", playlist[0])
      print("   Name:", playlist[2])
      print("   Number of Songs:", playlist[3])
      print()
      for song in songs:
        print("   Song ID:", song[0])
        print("      ", song[3], "by", song[2])
    return

  except Exception as e:
    logging.error("**ERROR: playlists() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
#
# create_playlist
#
def create_playlist(baseurl, token):
  try:
    if token is None:
      print("No current token, please login")
      return
    
    print("Time to create a playlist!")
    playlist_name = input("Enter a name for your playlist: ")
    if playlist_name == "":
      print("No name was given. Try again!")
      return

    data = {"token": token, "playlist_name": playlist_name, "new?": True}

    api = '/playlist'
    url = baseurl + api

    res = requests.post(url, json=data)

    if res.status_code == 401:
      body = res.json()
      print(body)
      return

    if res.status_code == 200: 
      pass
    elif res.status_code in [400, 500]:
      body = res.json()
      print("**Error:", body)
      return
    else:
      print("**ERROR: Failed with status code:", res.status_code)
      print("url: " + url)
      return

    playlist = res.json()
    print("Playlist", playlist[1], "has been created with ID", playlist[0])
    print("Have fun adding songs!")
    return

  except Exception as e:
    logging.error("**ERROR: create_playlist() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
#
# genre_playlist
#
def genre_playlist(baseurl, token):
  try:
    if token is None:
      print("No current token, please login")
      return
    
    print("Time to add random songs from the Billboard Top 100 based on genre to your playlist!")
    print("Here are the available genres from the Billboard Top 100 this week!")

    data = {"spotify_token": spotify_token, "token": token, "action": "genre"}    

    api = '/topsongs'
    url = baseurl + api

    res = requests.post(url, json=data)

    if res.status_code == 504:
      time.sleep(2)
      res = requests.post(url, json=data)

    if res.status_code == 200:
      genres = res.json()[0]
      genres_to_songs = res.json()[1]
      genres = dict(sorted(genres.items(), key=lambda item: item[1], reverse=True))
      for genre in genres:
        print(f"{genre}: {genres[genre]}")
    else:
      print("Error: " + str(res.status_code))
      print(res.text)
      return

    valid = False
    while not valid:
      print()
      print("Enter three genres to choose from!")
      genre1 = input("Genre 1 (At most 5 songs will be selected): ")
      count1 = 5
      genre2 = input("Genre 2 (At most 3 songs will be selected): ")
      count2 = 3
      genre3 = input("Genre 3 (At most 2 songs will be selected): ")
      count3 = 2

      if genre1 not in genres_to_songs or genre2 not in genres_to_songs or genre3 not in genres_to_songs:
        print("Genre(s) does not exist. Try again.")
      else:
        valid = True
  
    count1 = min(len(genres_to_songs[genre1]), 5)
    count2 = min(len(genres_to_songs[genre2]), 3)
    count3 = min(len(genres_to_songs[genre3]), 2)

    repeat = True
    while repeat:
      playlist_rand = []
      
      available1 = genres_to_songs[genre1].copy()
      available2 = genres_to_songs[genre2].copy()
      available3 = genres_to_songs[genre3].copy()

      for i in range(count1):
        rand = random.choice(available1)
        playlist_rand.append(rand)
        available1.remove(rand)
      for i in range(count2):
        rand = random.choice(available2)
        playlist_rand.append(rand)
        available2.remove(rand)
      for i in range(count3):
        rand = random.choice(available3)
        playlist_rand.append(rand)
        available3.remove(rand)

      playlist_rand = list(set(playlist_rand))
      print()
      print("Here is your randomly generated playlist based off the provided genres")
      for track in playlist_rand:
        print(f"{track}")

      print("Enter Y to generate a new playlist. Enter anything else to offically add songs to your playlist")

      if input() !=  "Y":
        repeat = False
  

    # add songs to playlist
    playlist_id = input("Enter the id of the playlist you want to add songs to: ")

    data = {"spotify_token": spotify_token, "token": token, "playlist_id": playlist_id, "songs": playlist_rand}

    api = '/addsongs'
    url = baseurl + api
    res = requests.post(url, json=data)
    if res.status_code == 200:
      playlist_id = res.json()[0]
      num_songs = res.json()[1]
      print(f"Playlist {playlist_id} is now updated with {num_songs} songs")
    else:
      print("Error: " + str(res.status_code))
      print(res.text)
    return

  except Exception as e:
    logging.error("**ERROR: genre_playlist() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
#
# popular_song
#
def popular_song(baseurl, token):
  try:
    if token is None:
      print("No current token, please login")
      return
     
    print("Time to check the most popular song in one of your playlists")
    playlist_id = input("Enter a playlist id: ")

    data = {"spotify_token": spotify_token, "token": token, "playlist_id": playlist_id}

    api = '/popular'
    url = baseurl + api

    res = requests.post(url, json=data)

    if res.status_code == 401:
      body = res.json()
      print(body)
      return

    if res.status_code == 200: 
      pass
    elif res.status_code in [400, 500]:
      body = res.json()
      print("**Error:", body)
      return
    else:
      print("**ERROR: Failed with status code:", res.status_code)
      print("url: " + url)
      return

    song = res.json()

    if song == "No songs in this playlist":
      print("No songs in this playlist. Try a different playlist")
      return

    song_name = song[0]
    song_artist = song[1]
    song_pop = song[2]
    song_link = song[3]
    playlist_name = song[4]

    print(f"Playlist {playlist_name}'s most popular song is {song_name} by {song_artist} with popularity score {song_pop}.")
    play_song = input("Enter Y if you would like to play this song on Spotify. Enter anything else to continue: ")

    if play_song == 'Y':
      print(song_link)
      webbrowser.open(song_link)

    return

  except Exception as e:
    logging.error("**ERROR: upload() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

############################################################
#
# check_url
#
def check_url(baseurl):
  """
  Performs some checks on the given url, which is read from a config file.
  Returns updated url if it needs to be modified.

  Parameters
  ----------
  baseurl: url for a web service

  Returns
  -------
  same url or an updated version if it contains an error
  """

  #
  # make sure baseurl does not end with /, if so remove:
  #
  if len(baseurl) < 16:
    print("**ERROR: baseurl '", baseurl, "' is not nearly long enough...")
    sys.exit(0)

  if baseurl == "https://YOUR_GATEWAY_API.amazonaws.com":
    print("**ERROR: update config file with your gateway endpoint")
    sys.exit(0)

  if baseurl.startswith("http:"):
    print("**ERROR: your URL starts with 'http', it should start with 'https'")
    sys.exit(0)

  lastchar = baseurl[len(baseurl) - 1]
  if lastchar == "/":
    baseurl = baseurl[:-1]
    
  return baseurl
  

############################################################
# main
#
try:
  print('** Welcome to Spotify Playlist Maker **')
  print()

  sys.tracebacklimit = 0

  spotifyapp_config_file = 'spotifyapp-client-config.ini'
  authsvc_config_file = 'authsvc-client-config.ini'
  spotify_auth_config_file ='spotify-auth-config.ini'

  # spotify_auth config file
  print("First, enter name of Spotify authorization config file to use...")
  print("Press ENTER to use default, or")
  print("enter config file name>")
  s = input()

  if s == "": 
    pass  
  else:
    spotify_auth_config_file = s

  if not pathlib.Path(spotify_auth_config_file).is_file():
    print("**ERROR: spotify_auth config file '", spotify_auth_config_file, "' does not exist, exiting")
    sys.exit(0)

  configur = ConfigParser()
  configur.read(spotify_auth_config_file)
  
  client_id = configur.get('client', 'client_id')
  client_secret = configur.get('client', 'client_secret')
  
  auth_value = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

  auth_options = {
    'url': 'https://accounts.spotify.com/api/token',
    'headers': {
        'Authorization': f'Basic {auth_value}'
    },
    'data': {
        'grant_type': 'client_credentials'
    }
  }

  response = requests.post(auth_options['url'], headers=auth_options['headers'], data=auth_options['data'])
  
  if response.status_code == 200:
    spotify_token = response.json()['access_token']
  else:
    print("Error: " + str(response.status_code))
    print(response.text)
    sys.exit(0)

  # authsvc config file
  print("Second, enter name of Auth Service config file to use...")
  print("Press ENTER to use default, or")
  print("enter config file name>")
  s = input()

  if s == "":
    pass  
  else:
    authsvc_config_file = s

  if not pathlib.Path(authsvc_config_file).is_file():
    print("**ERROR: authsvc config file '", authsvc_config_file, "' does not exist, exiting")
    sys.exit(0)

  configur.read(authsvc_config_file)
  auth_url = configur.get('client', 'webservice')
  
  auth_url = check_url(auth_url)

  # spotifyapp config file
  print("Third, enter name of SpotifyApp config file to use...")
  print("Press ENTER to use default, or")
  print("enter config file name>")
  s = input()

  if s == "":
    pass  
  else:
    spotifyapp_config_file = s

  if not pathlib.Path(spotifyapp_config_file).is_file():
    print("**ERROR: authsvc config file '", spotifyapp_config_file, "' does not exist, exiting")
    sys.exit(0)

  configur.read(spotifyapp_config_file)
  baseurl = configur.get('client', 'webservice')
  
  baseurl = check_url(baseurl)

  #
  # initialize login token:
  #
  token = None

  #
  # main processing loop:
  #
  cmd = prompt()

  while cmd != 0:
    #
    if cmd == 1:
      create_user(baseurl)
    elif cmd == 2:
      token = login(auth_url)
    elif cmd == 3:
      authenticate(auth_url, token)
    elif cmd == 4:
      top_songs(baseurl, spotify_token)
    elif cmd == 5:
      playlists(baseurl, token)
    elif cmd == 6:
      create_playlist(baseurl, token)
    elif cmd == 7:
      genre_playlist(baseurl, token)
    elif cmd == 8:
      popular_song(baseurl, token)
    elif cmd == 9:
      #
      # logout
      #
      token = None
    else:
      print("** Unknown command, try again...")
    #
    cmd = prompt()

  #
  # done
  #
  print()
  print('** done **')
  sys.exit(0)

except Exception as e:
  logging.error("**ERROR: main() failed:")
  logging.error(e)
  sys.exit(0)
