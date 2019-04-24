'use strict';

/* Controllers */
function indexController($scope,$http,$window,$timeout,$location,$routeParams,$rootScope) {
	$scope.worlds = worlds;
}

function mudController($scope,$http,$window,$timeout,$location,$routeParams,$rootScope) {
	
	$scope.worldId = $routeParams.cat1;
	$scope.resp = [];
	$scope.cmd = '';

	//Load the worl information
	$scope.getWorldInfo = function(worldId){
		$http.post("/load-world",{
			worldId: worldId
		}).
		success(function(resp)
		{
			console.log(resp);
			if(resp.status == "success"){
				$scope.resp.push(resp.intro);
			}
			else{
				$(window).unbind('beforeunload');
				window.location = "/";
			}
			$scope.scrollDown();
		})
		.error(function(response){
			console.warn(response);
		});
	}

	$scope.sendCommand = function(value){
		if(value.trim() == "")
			return;
		$scope.cmd = '';
		if(value == "start"){//Start the game
			$scope.startGame();
		}
		else if(value == "finish"){//End the game
			$scope.endGame();
		}
		else{
			$scope.executeCommand(value);//Call the execute command api endpoint
		}
	}

	//Begin the game
	$scope.startGame = function(){
		$http.post("/start-game").
		success(function(resp)
		{
			console.log(resp);
			if(resp.status == "success"){
				$scope.resp.push("You have began your journey...");
				$scope.resp.push("You have been given the name <b>"+getCookie('user_id')+"</b>");
				$scope.resp.push(resp["roomInfo"]["text"]);
				if("usersInRoom" in resp && resp["usersInRoom"].length > 0){
					$scope.resp.push("You see some fellow travellers,");
					$scope.resp.push("<b class='user-list'>"+resp["usersInRoom"].join("     ")+"</b>");
				}
				$scope.scrollDown();
				$scope.initMsgListener();
			}
		})
		.error(function(response){
			console.warn(response);
		});
	}

	//Function to call the execute command api end point
	$scope.executeCommand = function(cmd){
		$http.post("/execute-command",{
			command: cmd
		}).
		success(function(resp)
		{	
			if(resp.status == "success"){
				$scope.resp.push(resp["roomInfo"]["text"]);
				if("usersInRoom" in resp && resp["usersInRoom"].length > 0){
					$scope.resp.push("You see some fellow travellers,");
					$scope.resp.push("<b class='user-list'>"+resp["usersInRoom"].join("     ")+"</b>");
				}
			}
			else if(resp.status == "Progress Failed"){//The user cant move to the new location with the given comman
				$scope.resp.push(resp["roomInfo"]["text"]);
			}
			else if(resp.status == "Command Not Found"){//The given command is not found
				$scope.resp.push("Hmm...I guess you are speaking another language :O Try another command!");
			}
			else if(resp.status == "Not Started"){//The game is not started but a valid command is entered
				$scope.resp.push("You have to begin your adventure before you can say that command!");
			}
			else if(resp.status == "User Not Visible"){//The user you are trying to message is not in the room
				$scope.resp.push("That user is not in your room! They might have left the room or you're in another room.");
			}
			$scope.scrollDown();
			console.log(resp);
		})
		.error(function(response){
			console.warn(response);
		});
	}

	//This function listens to a node in firebase db
	//Any change in the value will trigger a callback here
	$scope.initMsgListener = function(){
		var user_id = getCookie("user_id");
		if (!firebase.apps.length) {
			firebase.initializeApp({
				apiKey: 'AIzaSyBn5s86pGyIY3EH5hSqenTL4AH0PhdXlZ8',
				authDomain: 'multi-user-dungeon.firebaseapp.com',
				projectId: 'multi-user-dungeon'
			});
		}
		 
		var db = firebase.firestore();

		db.collection("users").doc(user_id)
		.onSnapshot(function(doc) {
			var source = doc.metadata.hasPendingWrites ? "Local" : "Server";
			console.log(source, " data: ", doc.data());
			var messages = doc.data().messages;
			if (messages.length > 0){
				var rm = messages[messages.length-1];
				if(rm['from'] == getCookie('user_id'))
					return;
				$scope.$apply(function(){
					var tmsg = "Traveller <i class='user'>"+rm['from']+"</i> "+rm['type']+"s, <b class='"+rm['type']+"'>'"+rm['msg']+"'</b>"
					$scope.resp.push(tmsg);
					$scope.scrollDown();
				});
			}
		});

	}

	//Function to end the game. Triggered by finish command
	$scope.endGame = function(){
		$http.post("/end-game").
		success(function(resp)
		{
			console.log(resp);
			if(resp == "success"){
				$scope.resp.push("<b class='info'>Thank you for playing dungeon traps :)</b>");
				setTimeout(function(){
					$(window).unbind('beforeunload');
					window.location = "/";
				}, 2000);
			}
			else{
				$scope.resp.push("You have to start a game before you can end it.");
			}
			$scope.scrollDown();
		})
		.error(function(response){
			console.warn(response);
		});
	}

	//Function to get the current location of the user
	$scope.getUserLocation = function(){
		$http.post("/get-user-loc").
		success(function(resp)
		{
			if(resp != "error")
				$scope.user_location = resp;
		})
		.error(function(response){
			console.warn(response);
		});
	}

	//Function to scroll down the view
	$scope.scrollDown = function(){
		setTimeout(function(){
			$('.console').scrollTop($('.console')[0].scrollHeight);
		},500);
		$scope.getUserLocation();
	}

	//Get the information like intro of the world
	$scope.getWorldInfo($scope.worldId);

	//Prevent user from navigating away
	$(window).bind('beforeunload', function(){
		return "Please exit the game with finish command";
	});
}

//Get value of a given cookie key
function getCookie(key) {
	var keyValue = document.cookie.match('(^|;) ?' + key + '=([^;]*)(;|$)');
	return keyValue ? keyValue[2] : null;
};
