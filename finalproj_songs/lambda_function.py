import json
import os
import datetime
import uuid
import datatier
import api_utils

from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: finalproj_songs**")

    config_file = 'spotifyapp-config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
    
    configur = ConfigParser()
    configur.read(config_file)
    
    rds_endpoint = configur.get('rds', 'endpoint')
    rds_portnum = int(configur.get('rds', 'port_number'))
    rds_username = configur.get('rds', 'user_name')
    rds_pwd = configur.get('rds', 'user_pwd')
    rds_dbname = configur.get('rds', 'db_name')
    
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

    print("**Accessing request body**")
    
    playlist_id = ""

    if "body" not in event:
      return api_utils.error(400, "no body in request")
      
    body = json.loads(event["body"])
    
    if "playlist_id" in body: 
      playlist_id = body["playlist_id"]
    else:
      return api_utils.error(400, "missing credentials in body")

    if playlist_id != "":
      print("Retrieving specific playlist's song")

      sql = "SELECT * FROM songs WHERE playlistid = %s"
      rows = datatier.retrieve_all_rows(dbConn, sql, [playlist_id])

      return api_utils.success(200, rows)
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))

    return api_utils.error(500, str(err))
