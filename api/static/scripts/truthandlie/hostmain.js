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
async function getid() {
    const response = await fetch('/twotruthsandalie/host', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'type':'newid'})
    })
    const data = await response.json();
    yourid = data.yourid
    gameid = data.id;
    document.getElementById('gameid').innerHTML = gameid;
}
getid();
async function reload(){
    const response = await fetch('/twotruthsandalie/host', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'type':'refresh','playerid':yourid,'gameid':gameid})
    })
    const data = await response.json();
    console.log(data.players);
    var blank = "<tr><th>Username</th><th>Submitted?</th><th>Score</th></tr>"
    for(var i = 0; i < data.players.length; ++i){
        blank += "<tr><th>" + data.players[i][0] + "</th><th>" + data.players[i][1] + "</th><th>" + data.players[i][2] + "</th></tr>";
    }
    document.getElementById("players").innerHTML = blank;
}
setInterval(reload, 1000);
async function finish(){
    document.getElementById("phase").innerHTML = "Curent Phase: Checking"
    await fetch('/twotruthsandalie/host', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'type':'finish', 'playerid':yourid,'gameid':gameid})
    })
}
async function end(){
    document.getElementById("phase").innerHTML = "Curent Phase: Done"
    await fetch('/twotruthsandalie/host', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'type':'end', 'playerid':yourid,'gameid':gameid})
    })
}