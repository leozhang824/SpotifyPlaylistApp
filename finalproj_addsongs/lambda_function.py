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
    print("**lambda: finalproj_playlist**")

    config_file = 'spotifyapp-config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
   
    configur = ConfigParser()
    configur.read(config_file)
    
    rds_endpoint = configur.get('rds', 'endpoint')
    rds_portnum = int(configur.get('rds', 'port_number'))
    rds_username = configur.get('rds', 'user_name')
    rds_pwd = configur.get('rds', 'user_pwd')
    rds_dbname = configur.get('rds', 'db_name')

    api_config = 'spotifyapi-config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = api_config
    configur.read(api_config)
    
    baseurl = configur.get('api', 'webservice')

    config_file = 'authsvc-client-config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
  
    configur.read(config_file)

    client_webservice = configur.get('client', 'webservice')
    
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

    print("**Accessing request body**")
    
    token = ""
    playlist_id = "" 
    songs = ""

    if "body" not in event:
      return api_utils.error(400, "no body in request") 
    body = json.loads(event["body"])
    
    if "token" in body and "playlist_id" in body and "songs" in body and "spotify_token" in body: 
      token = body["token"]
      playlist_id = body["playlist_id"]
      songs = body["songs"]
      spotify_token = body["spotify_token"]
    else:
      return api_utils.error(400, "missing credentials in body")
    
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
    
    # check if playlist exists:
    print("Retrieving specific playlists")

    sql = "SELECT * FROM playlists WHERE userid = %s AND playlistid = %s"
    row = datatier.retrieve_one_row(dbConn, sql, [userid, playlist_id])

    if row == () or row is None:
      print("**Requested playlist does not exist**")
      return {'statusCode': 500, 'body': json.dumps("Playlist does not exist")} 
    
    api = "/search?q="

    for song in songs:
      song = song.replace(" ", "") 
      url = baseurl + api + song + "&type=track"

      headers = {"Authorization": f"Bearer {spotify_token}"}
      res = requests.get(url, headers=headers)

      if res.status_code == 200:
        data = res.json()
        track = data['tracks']['items'][0]
        spotify_songid = track['id']
        song_name = track['name']
        artist_name = track['artists'][0]['name']

        sql = "INSERT INTO songs (playlistid, artist_name, song_name, spotify_songid) VALUES (%s, %s, %s, %s)"
        datatier.perform_action(dbConn, sql, [playlist_id, artist_name, song_name, spotify_songid])
      else:
        print("Error: " + str(res.status_code))
        return api_utils.error(401, res.text)
      
    sql = "SELECT COUNT(*) FROM songs WHERE playlistid = %s"
    row = datatier.retrieve_one_row(dbConn, sql, [playlist_id])

    num_songs = row[0]

    sql = "UPDATE playlists SET num_songs = %s WHERE playlistid = %s"
    datatier.perform_action(dbConn, sql, [num_songs, playlist_id])

    return api_utils.success(200, [playlist_id, num_songs])
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))

    return api_utils.error(500, str(err))
