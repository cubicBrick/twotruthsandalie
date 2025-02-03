var username = "[null]"
var gameID = "[null]"
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
var userid = "[null]";
async function join() {
    gameID = document.getElementById('gameid').value;
    username = document.getElementById('username').value;
    const response = await fetch('/twotruthsandalie/join', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'type': 'join', "gameid": gameID, "username": username })
    });
    const data = await response.json();
    if (data.good) {
        document.getElementById('join').setAttribute('hidden', '');
        document.getElementById('enter').removeAttribute('hidden');
        userid = data.userid;
        setInterval(reload, 2000)
    }
    else {
        alert(data.error)
        console.log("Error:  " + data.error);
    }
}

async function go() {
    var l1 = document.getElementById('l1').value;
    var t1 = document.getElementById('t1').value;
    var t2 = document.getElementById('t2').value;
    const response = await fetch('/twotruthsandalie/join', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'type': 'play', "id": userid, "gameid": gameID, "username": username, "t1": t1, "t2": t2, "l1": l1 })
    });
    const data = await response.json();
    if (!data.good) {
        alert("ERROR! Could not submit: " + data.error);
        return;
    }
    document.getElementById("submitted").removeAttribute("hidden");
    document.getElementById("submitbutton").setAttribute("hidden", "");
}
async function getCurrent() {
    const response = await fetch('/twotruthsandalie/join', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'type': 'get', "id": userid, "gameid": gameID })
    });
}
var currPhase = "submitting"
async function reload() {
    const response = await fetch('/twotruthsandalie/join', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'type': 'refresh', 'gameid': gameID, 'id': userid })
    })
    const data = await response.json();
    if (!data.good) {
        alert("ERROR! Could not fetch data from the server: " + data.error);
        return;
    }
    if (currPhase != data.phase && data.phase.includes("guessing")) {
        currPhase = data.phase
        document.getElementById("enter").setAttribute("hidden", "");
        document.getElementById("guess").removeAttribute("hidden");

        const response = await fetch('/twotruthsandalie/join', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 'type': 'get', 'gameid': gameID, 'id': userid })
        })
        if (!data.good) {
            alert("ERROR! Could not fetch data from the server: " + data.error);
            return;
        }
        g0 = data.g0
        g1 = data.g1
        g2 = data.g2
        document.getElementById("label_option1").innerHTML = g0;
        document.getElementById("label_option2").innerHTML = g1;
        document.getElementById("label_option3").innerHTML = g2;
    }
    else if (data.phase == "") {

    }
}