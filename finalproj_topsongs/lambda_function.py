import json
import os
import datetime
import uuid
import datatier
import api_utils
import requests

from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: finalproj_topsongs**")

    configur = ConfigParser()

    api_config = 'spotifyapi-config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = api_config
    configur.read(api_config)
    
    baseurl = configur.get('api', 'webservice')

    config_file = 'authsvc-client-config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
  
    configur.read(config_file)

    client_webservice = configur.get('client', 'webservice')
 
    print("**Accessing request body**")
    
    spotify_token = ""
    token = "" 
    action = ""
    
    if "body" not in event:
      return api_utils.error(400, "no body in request")

    body = json.loads(event["body"])
    
    if "spotify_token" in body: 
      spotify_token = body["spotify_token"]
    else:
      return api_utils.error(400, "missing spotify token in body")
    
    if "token" in body and "action" in body: 
      token = body["token"]
      action = body["action"]
    else:
      return api_utils.error(400, "missing credentials in body")
    
    # check top songs
    api = "/playlists/6UeSakyzhiEt4NB3UAd6NQ"
    url = baseurl + api
    headers = {"Authorization": f"Bearer {spotify_token}"}
    res = requests.get(url, headers=headers)

    if res.status_code == 200:
      data = res.json()
      top_songs = data
    else:
      print("Error: " + str(res.status_code))
      return api_utils.error(401, res.text)
    
    # acutally do something with top songs
    if token != None:
      print("**We were passed a token**")
      print("**We were passed a token**")
      print("token:", token)
      
      data = {'token': token}
      auth_url = client_webservice + '/auth'
      print(auth_url)
      print(token)
      res = requests.post(auth_url, json=data)
      print(res.status_code)

      if res.status_code == 401: #authentication failure
        return {
        'statusCode': 401,
        'body': json.dumps(res.json())
        }
      elif res.status_code == 500 or res.status_code == 400:
        return {
          'statusCode': 500,
          'body': json.dumps(res.json())
        }
      elif res.status_code > 200:
        return {
            'statusCode': 500,
            'body': json.dumps(res.json())
          }
      else:
        token = res.json()[0]
        userid = res.json()[1]

      # complies genre of songs
      print("Compiling genres")
      if action == "genre":
        genre_dict = {}
        genre_to_song = {}
        tracks = top_songs['tracks']['items']
        for track in tracks:
          artist_name = track['track']['artists'][0]['name']
          artist_name = artist_name.replace(" ", "") 
          
          api = "/search?q="
          url = baseurl + api + artist_name + "&type=artist"
          headers = {"Authorization": f"Bearer {spotify_token}"}
          res = requests.get(url, headers=headers)
          
          if res.status_code == 200:
            data = res.json()
            genres = data['artists']['items'][0]['genres']
            for genre in genres:
              if genre in genre_dict:
                genre_dict[genre] += 1
              else: 
                genre_dict[genre] = 1

              if genre in genre_to_song:
                genre_to_song[genre].append(track['track']['name'])
              else: 
                genre_to_song[genre] = [track['track']['name']]
          else:
            print("Error: " + str(res.status_code))
            print(res.text)
        data = [genre_dict, genre_to_song]
        
    return api_utils.success(200, data)
  
  except Exception as err:
    print("**ERROR**")
    print(str(err))

    return api_utils.error(500, str(err))
