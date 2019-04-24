# -*- coding: utf-8 -*-
# Dungeon Trap
from flask import Flask
from flask import render_template, redirect, session, request, json, make_response
from flask.json import jsonify
from flask_assets import Environment, Bundle
import json, os, string, uuid
from google.cloud import firestore
from google.cloud.firestore_v1 import ArrayRemove, ArrayUnion
import google.cloud.exceptions

app = Flask(__name__)
app.config.from_pyfile('config.py')
angular_assets = Environment(app)

# Initialize Firebase Database Client
db = firestore.Client()

# AngularJS Files Bundle
bundles = {
    'angular_js': Bundle(
        'angular/ang/mainAng.js',
        'angular/ang/controllers.js',
        'angular/ang/services.js',
        'angular/ang/filters.js',
        output='opt/ang.js',filters='jsmin'),

    'angular_css': Bundle(
        'assets/css/custom.css',
        output='opt/ang.css',filters='cssmin')
}
angular_assets.register(bundles)

# AngularJS Routings
@app.route('/')
@app.route('/dungeon/<world>')
def dashboard(**kwargs):
    return render_template('console/console.html', worlds = app.config['WORLDS'])

################################################################################
##############################API END POINTS####################################
################################################################################

@app.route('/load-world', methods=['POST'])
def load_world():
    data = json.loads(request.data.decode('utf-8'))
    worldId = data["worldId"]
    world = loadWorld(worldId)
    if world is None:
        return jsonify(status="error")
    session["world_id"] = worldId
    session['world'] = world
    resp = make_response(jsonify(status="success", intro = world["intro"]))
    resp.set_cookie('user_loc','', expires=0)
    if "user_location" in session:
        session.pop("user_location")
    return resp

@app.route('/start-game', methods=['POST'])
def start_game():
    #Generate an unique user id
    uid = generateGuestUserId()
    #Load world in session
    world = loadWorld(session.get("world_id"))
    startLocation = world["start"]
    #Set session values
    session['start_game'] = True
    session['user_id'] = uid
    session['user_location'] = startLocation
    #Set user info in firebase
    doc_ref = db.collection(u'users').document(uid)
    doc_ref.set({
        "userid": uid.decode('utf-8'),
        "messages": []
    })    
    #Retrieve users in the starting room
    usersInRoom = getUsersInRoom()
    setUserToRoom()
    #Retrieve the room info for the start location
    query = getQueryString(startLocation)
    roomInfo = getRoomInfo(query, world["floors"])
    roomInfo['text'] = generateRoomInfoText(roomInfo)
    #Return the response
    resp = make_response(jsonify(status="success", roomInfo = roomInfo, usersInRoom = usersInRoom))
    resp.set_cookie('user_id', uid)
    resp.set_cookie('user_loc', startLocation)
    return resp

@app.route('/execute-command', methods=['POST'])
def execute_command_received():
    #Check if the game has started
    #If the game is not started we won't receive other commands
    if session.get('start_game') != True:
        return jsonify(status="Not Started") #Return game not started status
    #Read request data
    data = json.loads(request.data.decode('utf-8'))
    command = data["command"]
    cSplit = command.split(" ")
    text = ""
    #Command to be executed
    command = cSplit[0].lower()
    #Check to which type the command belongs to
    if command in app.config['NAVIGATION']:#The command is a navigation command like up, down, north, south
        currentLocation = session.get('user_location')
        query = getQueryString(currentLocation)
        status, roomInfo, usersInRoom = handleNavigationCommand(command, query)
        return jsonify(status=status, roomInfo=roomInfo, usersInRoom=usersInRoom)
    elif command in app.config['COMMUNICATION']:#The command is a user communication commands like yell, say, tell
        status = handleCommunicationCommand(command, cSplit)
        return status
    #Additional commands can be added here like
    #elif command in INTERACTION ('pick', 'drop', 'fight')
    else:#No valid command is found
        return jsonify(status="Command Not Found")

@app.route('/end-game', methods=['POST'])
def end_game():
    #If there is a current user session end the game
    if "user_id" in session:
        currentLocation = session.get("user_location")
        worldRef = db.collection(u'world').document(session.get("world_id"))
        worldRef.update({currentLocation.decode('utf-8'): ArrayRemove([session.get("user_id").decode('utf-8')])})
        session.clear()
        return "success"
    else:#Else return error because there is no game to end
        return "error"

@app.route('/get-user-loc', methods=['POST'])
def get_user_location():
    #If there is a current user session end the game
    if "user_location" in session:
        currentLocation = session.get("user_location")
        return currentLocation
    else:#Else return error because there is no game to end
        return "error"

################################################################################
################################FUNCTIONS#######################################
################################################################################

def generateGuestUserId():
    """Generates a guest user id.

    Keyword arguments: None
    Returns: String - user id of the form guest-xxxxx
    """
    uid = id_generator_lowercase(app.config['USER_ID_LENGTH'])
    return "guest-"+uid

def loadWorld(worldName):
    """Loads the given world.

    Keyword arguments:
    worldName -- The name of the world to load
    Returns: JSON - The entire game world
    """
    try:
        world = json.load(open("worlds/"+worldName+".json","r"))
    except IOError as e:
        world = None
    return world

def getQueryString(location):
    """Form the query string (array) using the given location

    Keyword arguments:
    location -- A String of length 3 (Ex. '010')
    Returns: Array of length 3
    """
    return [int(l) for l in location]

def getRoomInfo(query, floors):
    """Gets all the information about the room.
    Contains the room id, monsters, items,
    room type (transparent or solid)

    Keyword arguments:
    query -- An array of length 3 [floor, i-row, j-column]
    floors -- All the floors of the given world
    Returns: JSON - A json object with information about the room
    """
    return floors[query[0]]["rooms"][query[1]][query[2]]

def getUsersInRoom():
    """Gets all users in the room except the current user

    Keyword arguments:
    Returns: Array - A list of user ids
    """
    usersInRoom = list()
    #Get the user list for a particular location in the world
    worldRef = db.collection(u'world').document(session.get("world_id"))
    usersList = worldRef.get().to_dict()
    userLocation = session.get("user_location")
    uid = session.get("user_id")
    if userLocation in usersList:
        usersInRoom = usersList[userLocation]
    if uid in usersInRoom:#Remove the current user form the users list
        usersInRoom.remove(uid)
    return usersInRoom

def setUserToRoom():
    """Sets the user to the current location in the firebase map
    This helps in determining the list of users in a particular location
    """
    userLocation = session.get("user_location")
    uid = session.get("user_id")
    worldRef = db.collection(u'world').document(session.get("world_id"))
    worldRef.update({userLocation.decode('utf-8'): ArrayUnion([uid.decode('utf-8')])})
    return "done"

def handleNavigationCommand(cmd, query):
    """Handles all user navigation commands

    Keyword arguments:
    cmd -- the command to be executed (up, north etc.)
    query -- The query string
    Returns: the status, room information, users in the room
    """
    #Initialize some temporary variables
    text = ""
    progress = False#Check if the user has actually progressed or not in the end
    negIndex = False
    roomInfo = dict()
    usersInRoom = list()
    status = "success"
    if cmd == "up":#Move one position up
        query[0] += 1
    elif cmd == "down":#Move one position down
        if query[0]-1 >= 0:#Should always be greater than zero (no negative indexes)
            query[0] -= 1
        else:
            negIndex = True
    elif cmd == "north":#Move one position forward
        query[1] += 1
    elif cmd == "south":#Move one position backward
        if query[1]-1 >= 0:#Should always be greater than zero (no negative indexes)
            query[1] -= 1
        else:
            negIndex = True
    elif cmd == "east":#Move one position to right
        query[2] += 1
    elif cmd == "west":#Move one position to left
        if query[2]-1 >= 0:#Should always be greater than zero (no negative indexes)
            query[2] -= 1
        else:
            negIndex = True
    if negIndex == True:
        roomInfo['text'] = "Umm...you cant make that move...try something else."
        return "Progress Failed", roomInfo, usersInRoom
    world = loadWorld(session.get("world_id"))
    old_location = session.get('user_location')
    try:
        #Get the room info of the new room
        roomInfo = getRoomInfo(query, world["floors"])
        if roomInfo["type"] == "solid":#You can't enter a room of type solid
            text = "Oops...this room is locked (solid room) ! try something else."
            status = "Progress Failed"
        else:
            progress = True
            session['user_location'] = roomInfo["id"]
    except Exception as e:
        text = "Umm...you cant make that move...try something else."
        status = "Progress Failed"
    if progress == True:#If the user has progressed
        new_location = session['user_location']
        usersInRoom = getUsersInRoom()
        worldRef = db.collection(u'world').document(session.get("world_id"))
        #Remove user from current map location in db and relocate the user to the new location in db
        worldRef.update({old_location.decode('utf-8'): ArrayRemove([session.get("user_id").decode('utf-8')])})
        worldRef.update({new_location.decode('utf-8'): ArrayUnion([session.get("user_id").decode('utf-8')])})
        roomInfo['text'] = generateRoomInfoText(roomInfo)
    else:
        roomInfo['text'] = text
    return status, roomInfo, usersInRoom
    
def handleCommunicationCommand(cmd, cargs):
    """Handles all user communication commands

    Keyword arguments:
    cmd -- the command to be executed (say, tell, yell)
    cargs -- The arguments for the command
    Returns: JSON - A status after executing the command
    """
    if cmd == "tell":#Send message to a specific user
        if len(cargs) < 3:
            return jsonify(status="Command Not Found")
        user = cargs[1]
        msg = " ".join(cargs[2:])
        usersInRoom = getUsersInRoom()
        if user in usersInRoom:#Check if the target user is in the same room (a user might leave the room at anytime)
            userRef = db.collection(u'users').document(user)
            userRef.update({"messages": ArrayUnion([{'from':session.get('user_id').decode('utf-8'), 'msg': msg, 'type': u'tell'}])})
            return jsonify(status="success", roomInfo={'text': 'message sent'})
        else:
            return jsonify(status="User Not Visible")
    elif cmd == "yell":#Send message to all the users in the world
        if len(cargs) < 2:
            return jsonify(status="Command Not Found")
        msg = " ".join(cargs[1:])
        allUsers = db.collection(u'users').get()
        for user in allUsers:
            user_id = user.id
            userRef = db.collection(u'users').document(user_id)
            userRef.update({"messages": ArrayUnion([{'from':session.get('user_id').decode('utf-8'), 'msg': msg, 'type': u'yell'}])})         
        return jsonify(status="success", roomInfo={'text': 'message sent'})
    elif cmd == "say":#Send message to all the users in the room
        if len(cargs) < 2:
            return jsonify(status="Command Not Found")
        msg = " ".join(cargs[1:])
        usersInRoom = getUsersInRoom()
        for user in usersInRoom:
            userRef = db.collection(u'users').document(user)
            userRef.update({"messages": ArrayUnion([{'from':session.get('user_id').decode('utf-8'), 'msg': msg, 'type': u'say'}])})
        return jsonify(status="success", roomInfo={'text': 'message sent'})


def id_generator_lowercase(size=10, chars=string.ascii_lowercase):
    """Generates a random lowercase string of the given size

    Keyword arguments:
    size -- Length of the random string (default 10)
    chars -- Characters to be considered for forming the string (default lowercase alphabets)
    Returns: String - A random string
    """
    import random
    return ''.join(random.choice(chars) for _ in range(size))

def generateRoomInfoText(room):
    """Generates a room description for the given room

    Keyword arguments:
    room -- The room object for which description should be created
    Returns: String - A text based on the room contents
    """
    text = ""
    if "monsters" in room and len(room["monsters"]) > 0:
        monster = room["monsters"][0]
        text += "Whoa! You see a <b class='user'>level "+str(monster['level'])+" "+monster['type']+"</b> in the room."
    if "items" in room and len(room['items']) > 0:
        items = room["items"][0]
        if items["type"] == "object":
            text += "You see a "+items["name"]+" in the room."
        elif items["type"] == "weapon":
            text += "You see a <b class='weapon'>"+items["name"]+" (level "+str(items["level"])+")</b> in the room."
    if len(room["monsters"]) == 0 and len(room['items']) == 0:
        text += "The room is has no items."
    return text

if __name__ == '__main__':
    app.run(host='0.0.0.0')
