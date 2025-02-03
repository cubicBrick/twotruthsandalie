// Include the socket.io client library in your HTML file
<script src="/socket.io/socket.io.js"></script>

var socket = io();

function makeid(length) {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()-=_+';
    const charactersLength = characters.length;
    let counter = 0;
    while (counter < length) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
      counter += 1;
    }
    return result;
}

var yourid = "";
var gameid = "";

function getid() {
    socket.emit('newid');
}

socket.on('newid', function(data) {
    yourid = data.yourid;
    gameid = data.id;
    document.getElementById('gameid').innerHTML = gameid;
});

function reload() {
    socket.emit('refresh', { 'playerid': yourid, 'gameid': gameid });
}

socket.on('players', function(data) {
    console.log(data.players);
    var blank = "<tr><th>Username</th><th>Submitted?</th><th>Score</th></tr>";
    for (var i = 0; i < data.players.length; ++i) {
        blank += "<tr><th>" + data.players[i][0] + "</th><th>" + data.players[i][1] + "</th><th>" + data.players[i][2] + "</th></tr>";
    }
    document.getElementById("players").innerHTML = blank;
});

setInterval(reload, 1000);

function finish() {
    document.getElementById("phase").innerHTML = "Curent Phase: Checking";
    socket.emit('finish', { 'playerid': yourid, 'gameid': gameid });
}

function end() {
    document.getElementById("phase").innerHTML = "Curent Phase: Done";
    socket.emit('end', { 'playerid': yourid, 'gameid': gameid });
}