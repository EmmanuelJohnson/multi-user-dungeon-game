# -*- coding: utf-8 -*-

#==========I.Basic Configuration Begins==========#

##################################################
##############A.BUILTIN CONFIGS###################
##################################################

# Enable/Disable debug mode in Flask
DEBUG = True
# Enable/Disable testing mode in Flask
TESTING = False
# The secret key for the Flask App
SECRET_KEY = '3912e802-a02c-11e7-abf4-780cb8781d2e'
#Enable/Disable Assets Debugging in Flask
ASSETS_DEBUG = True

##################################################
##############B.CUSTOM CONFIGS####################
##################################################

HOST_BASE_LINK = "http://localhost:5000"

#Length of the user id that is generated
USER_ID_LENGTH = 5

#The available worlds
WORLDS = [
    {
        "name": "Heaven Earth Hell",
        "path": "worlds/real.json",
        "id": "world1"
    },
    {
        "name": "The Burj Khalifa",
        "path": "worlds/burj.json",
        "id": "world2"
    }
]

#Commands in navigation
NAVIGATION = ["north", "south", "east", "west", "up", "down"]

#Commands in communication
COMMUNICATION = ["say", "yell", "tell"]

#Can add additional command categories like
#INTERACTION = ["pick", "drop", "fight"]

#=========I.Database Configuration Begins========#

##################################################
##################A.FIREBASE######################
##################################################

FIRE_CONFIG = {
    'apiKey': 'AIzaSyBn5s86pGyIY3EH5hSqenTL4AH0PhdXlZ8',
    'authDomain': 'multi-user-dungeon.firebaseapp.com',
    'projectId': 'multi-user-dungeon'
}

#==========Database Configuration Ends==========#