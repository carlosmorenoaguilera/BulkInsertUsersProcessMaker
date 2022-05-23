#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para crear usuarios en ProcessMaker desde una base de datos consumiendo la API REST nativa y 
modificar todos los usuarios para que cambien la contraseña en el primer login usr_logged_next_time = 1 
"""

__author__ = "carlos moreno aguilera"
__license__ = "GPL"
__version__ = "0.1.2"
__maintainer__ = "carlos moreno aguilera"
__email__ = "carlosmauriciomoreno@outlook.com"



from email import header
from http.client import ResponseNotReady
from urllib import response
from wsgiref import headers
import requests
import json
import sqlite3
from peewee import *



def format_latin_characteres(character):
    dict_characteres = { "á": "a" , "é": "e" , "í": "i" , "ó": "o" , "ú": "u" , "ü": "u" , }
    new_character = ""
    for key in dict_characteres.keys():
        character = character.replace(key, str(dict_characteres[key]))
    
    return character

def connect_database():
    """usuarios.db 
        CREATE TABLE users (
            usr_username TEXT PRIMARY KEY,
            usr_firstname TEXT NOT NULL,
            usr_lastname TEXT NOT NULL,
            usr_email TEXT NOT NULL,
            usr_due_date TEXT NOT NULL DEFAULT '2040-12-31',
            usr_status TEXT NOT NULL,
            usr_role TEXT NOT NULL,
            usr_new_pass TEXT NOT NULL DEFAULT '<password>',
            usr_address TEXT NOT NULL,
            usr_position TEXT NOT NULL
        );
   
    """
    db = SqliteDatabase("usuarios.db")

    class BaseModel(Model):
        class Meta:
            database = db

    class users(BaseModel):
        usr_username = TextField(primary_key=True)
        usr_firstname = TextField()
        usr_lastname = TextField()
        usr_email = TextField()
        usr_due_date = TextField()
        usr_status = TextField()
        usr_role = TextField()
        usr_new_pass = TextField()
        usr_address = TextField()
        usr_position = TextField()
    db.connect()

    return users

def create_processmaker_user(api_token, user):
    """ creacion de usuario con el payload 
        
        payload = {'usr_username'   : "carlos.moreno",
                    'usr_firstname'  : "carlos",
                    'usr_lastname'   : "moreno",
                    'usr_email'      : "carlos.moreno.ceniss@outlook.com",
                    'usr_due_date'   : "2040-12-31",
                    'usr_status'     : "ACTIVE",
                    'usr_role'       : "PROCESSMAKER_OPERATOR",
                    'usr_new_pass'   : "Temporal15",
                    'usr_cnf_pass'   : "Temporal15",
                    'usr_address'    : "740 Turtle Dove lane",
                    'usr_position'   : "Developer",
                    }

    """
    api_server = "http://192.168.15.22"
    api_workflow = "workflow"
    api_rest_endpoint = "/api/1.0/" + api_workflow + "/user"

    headers = {"Content-Type":"application/json", "Authorization" : "Bearer " + api_token }

    payload = {'usr_username'   : format_latin_characteres(user.usr_username),
                'usr_firstname'  : user.usr_firstname,
                'usr_lastname'   : user.usr_lastname,
                'usr_email'      : user.usr_email,
                'usr_due_date'   : user.usr_due_date,
                'usr_status'     : user.usr_status,
                'usr_role'       : user.usr_role,
                'usr_new_pass'   : user.usr_new_pass,
                'usr_cnf_pass'   : user.usr_new_pass,
                'usr_address'    : user.usr_address,
                'usr_position'   : user.usr_position
                }
                
    response =  requests.post(api_server + api_rest_endpoint, data=json.dumps(payload), headers=headers)



def search_users(api_token, username):
    #'usr_logged_next_time' : 1
    api_server = "http://192.168.15.22/api/1.0/workflow/extrarest/user/search?match=" + username
    headers = {"Content-Type":"application/json", "Authorization" : "Bearer " + api_token }
    response =  requests.get(api_server, headers=headers)
    if response.status_code == 200:
        return response.json()[0][0]
    return None 

def update_user(api_token, usr_uid):
    api_server = "http://192.168.15.22/api/1.0/workflow/extrarest/user/update"
    headers = {"Content-Type":"application/json", "Authorization" : "Bearer " + api_token }
    payload =  {"usr_uid": usr_uid, "usr_logged_next_time" : 1  }
    response =  requests.put(api_server, data=json.dumps(payload), headers=headers)
    return response.status_code


if __name__ == "__main__":    
    db = SqliteDatabase("usuarios.db")

    class BaseModel(Model):
        class Meta:
            database = db

    class users(BaseModel):
        usr_username = TextField(primary_key=True)
        usr_firstname = TextField()
        usr_lastname = TextField()
        usr_email = TextField()
        usr_email = TextField()
        usr_due_date = TextField()
        usr_status = TextField()
        usr_role = TextField()
        usr_new_pass = TextField()
        usr_address = TextField()
        usr_position = TextField()
    db.connect()

    query = users.select()
    token = "TOKEN_AUTH_PROCESSMAKER"
    for user in query:
        create_processmaker_user(token, user)
        usr_uid = search_users(token, user.usr_username)
        if usr_uid is not None:
            update_user(token,  usr_uid)        
