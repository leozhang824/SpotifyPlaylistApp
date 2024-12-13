import json
import os
import datetime
import uuid
import datatier
import auth
import api_utils

from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: finalproj_create**")

    #
    # setup AWS based on config file
    #
    config_file = 'spotifyapp-config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
    
    configur = ConfigParser()
    configur.read(config_file)
    
    #
    # configure for RDS access
    #
    rds_endpoint = configur.get('rds', 'endpoint')
    rds_portnum = int(configur.get('rds', 'port_number'))
    rds_username = configur.get('rds', 'user_name')
    rds_pwd = configur.get('rds', 'user_pwd')
    rds_dbname = configur.get('rds', 'db_name')
    
    #
    # open connection to the database
    #
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

    #
    # We are expecting either a token, or username/password:
    #
    print("**Accessing request body**")
    
    username = "" 
    password = ""

    if "body" not in event:
      return api_utils.error(400, "no body in request")
      
    body = json.loads(event["body"])
    
    if "username" in body and "password" in body:
      username = body["username"]
      password = body["password"]
    else:
      return api_utils.error(400, "missing credentials in body")
    
    print("**We were passed username/password**")
    print("username:", username)
    print("password:", password)

    pwdhash = auth.hash_password(password)

    sql = "INSERT INTO users (username, pwdhash) VALUES (%s, %s)"
    
    datatier.perform_action(dbConn, sql, [username, pwdhash])

    sql = "SELECT LAST_INSERT_ID()"
    
    row = datatier.retrieve_one_row(dbConn, sql)

    userid = row[0]

    print("**Username and Password have been inserted**")

    return api_utils.success(200, userid)
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))

    return api_utils.error(500, str(err))
