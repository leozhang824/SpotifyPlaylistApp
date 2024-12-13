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

    config_file = 'authsvc-client-config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
  
    configur.read(config_file)

    client_webservice = configur.get('client', 'webservice')
    
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

    print("**Accessing request body**")
    
    token = "" 
    playlist_name = ""

    if "body" not in event:
      return api_utils.error(400, "no body in request")
      
    body = json.loads(event["body"])
    
    if "token" in body and "playlist_name" in body and "new?" in body: 
      token = body["token"]
      playlist_name = body["playlist_name"]
      new = body["new?"]
    else:
      return api_utils.error(400, "missing credentials in body")
    
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
    
    # check all playlists
    if playlist_name == "":
      print("Retrieving all playlists")

      sql = "SELECT * FROM playlists WHERE userid = %s"
      rows = datatier.retrieve_all_rows(dbConn, sql, [userid])

      print("**Retrieving all playlists for given user**")

      return api_utils.success(200, rows)
    
    # check specific playlist
    else:
      print("Retrieving specific playlists")

      sql = "SELECT * FROM playlists WHERE userid = %s AND playlist_name = %s"
      rows = datatier.retrieve_all_rows(dbConn, sql, [userid, playlist_name])

      # does not exist, create playlist
      if rows == () or rows is None:
        if new:
          print("Creating playlist")

          sql = "INSERT INTO playlists(userid, playlist_name) VALUES(%s, %s)"
          datatier.perform_action(dbConn, sql, [userid, playlist_name])

          sql = "SELECT LAST_INSERT_ID()"
      
          row = datatier.retrieve_one_row(dbConn, sql)

          playlistid = row[0]

          print("**New Playlist has been created**")

          return api_utils.success(200, [playlistid, playlist_name])
        
        else:
          print("**Requested playlist does not exist**")
          return api_utils.success(200, None)

      else:
        print("**Retrieving all playlists under this name for given user**")
        return api_utils.success(200, rows)
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))

    return api_utils.error(500, str(err))
