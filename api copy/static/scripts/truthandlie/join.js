// Include the socket.io client library in your HTML file
<script src="/socket.io/socket.io.js"></script>

var socket = io();

var username = "[null]";
var gameID = "[null]";
var userid = "[null]";

function makeid(length) {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;
    let counter = 0;
    while (counter < length) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
        counter += 1;
    }
    return result;
}

function join() {
    gameID = document.getElementById('gameid').value;
    username = document.getElementById('username').value;
    socket.emit('join', { 'gameid': gameID, 'username': username });
}

socket.on('joined', function(data) {
    document.getElementById('join').setAttribute('hidden', '');
    document.getElementById('enter').removeAttribute('hidden');
    userid = data.userid;
    setInterval(reload, 2000);
});

socket.on('error', function(data) {
    alert(data.error);
    console.log("Error:  " + data.error);
});

function go() {
    var l1 = document.getElementById('l1').value;
    var t1 = document.getElementById('t1').value;
    var t2 = document.getElementById('t2').value;
    socket.emit('play', { 'id': userid, 'gameid': gameID, 'username': username, 't1': t1, 't2': t2, 'l1': l1 });
}

socket.on('played', function(data) {
    document.getElementById("submitted").removeAttribute("hidden");
    document.getElementById("submitbutton").setAttribute("hidden", "");
});

function getCurrent() {
    socket.emit('get', { 'id': userid, 'gameid': gameID });
}

var currPhase = "submitting";
function reload() {
    socket.emit('refresh', { 'gameid': gameID, 'id': userid });
}

socket.on('phase', function(data) {
    if (currPhase != data.phase && data.phase.includes("guessing")) {
        currPhase = data.phase;
        document.getElementById("enter").setAttribute("hidden", "");
        document.getElementById("guess").removeAttribute("hidden");

        socket.emit('get', { 'gameid': gameID, 'id': userid });
    }
});

socket.on('data', function(data) {
    g0 = data.g0;
    g1 = data.g1;
    g2 = data.g2;
    document.getElementById("label_option1").innerHTML = g0;
    document.getElementById("label_option2").innerHTML = g1;
    document.getElementById("label_option3").innerHTML = g2;
});