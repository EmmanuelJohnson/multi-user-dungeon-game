# multi-user-dungeon-game

<h3>How to deploy</h3>

<p>Install Docker Community Edition</p>
<p>Run the following command,</p>
<ul>
  <li>docker run -d --restart always --name dungeon-trap -p 80:8000  gemmanuel/mud:latest</li>
</ul>
<p>This deploys the application in port 80. Feel free to change it.</p>
<p>Visit http://localhost or http://localhost:&lt;port&gt; to view the application.</p>

<h3>Instructions</h3>

<h4>Starting and Ending the Game</h4>
<p><b>start : </b> Begin the game</p>
<p><b>finish : </b> End the game</p>

<h4>Communication</h4>
<p><b>tell &lt;user name&gt; &lt;message&gt; : </b> Send message to a user</p>
<p><b>say &lt;message&gt; : </b> Send message to all the users in the room</p>
<p><b>yell &lt;message&gt; : </b> Send message to all the users in the world</p>

<h4>Navigation</h4>
<p><b>up : </b> Move upwards (One floor up)</p>
<p><b>down : </b> Move downwards (One floor down)</p>
<p><b>north : </b> Move forward</p>
<p><b>south : </b> Move backward</p>
<p><b>east : </b> Move right</p>
<p><b>west : </b> Move left</p>
