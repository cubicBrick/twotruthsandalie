from flask import Flask, render_template, request, redirect, jsonify, json
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

IDLELIMIT = timedelta(seconds=60)
DEFAULTCHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
LOG_FILE = "./.log"
random.seed(os.urandom(32))


# Logs the data with a timestamp
def log(data: str, *, file=LOG_FILE) -> None:
    logs = open(file, "a")
    logs.write(f"[{datetime.now().ctime()}]: {data}\n")
    logs.close()


def randString(length: int, charset=DEFAULTCHARSET):
    res = ""
    for i in range(length):
        res += charset[random.randint(0, len(charset) - 1)]
    return res


@app.route("/")
def pageHome():
    return render_template("./home.html")


@app.route("/twotruthsandalie/home")
def pageTruthsLiesHome():
    return render_template("./truthandlie/main.html")


twotruthsandaliegames: "dict[str, truthAndLie]" = {}


@app.route("/twotruthsandalie/join", methods=["GET", "POST"])
def pageTruthsLiesJoin():
    if request.method == "POST":
        data = request.json
        if data.get("type") == "join":
            gameid = data.get("gameid")
            username = data.get("username")
            log(f"Attempted to join game with id [{gameid}], username [{username}].")
            if gameid not in twotruthsandaliegames.keys():
                return jsonify({"error": "Game not found"}), 404
            playerid = randString(32)
            twotruthsandaliegames[gameid].players[playerid] = username
            return jsonify({"good": "Game found", "userid":playerid}), 200
        elif data.get("type") == "play":
            t1 = data.get('t1')
            t2 = data.get('t2')
            l1 = data.get('l1')
            playerid = data.get('id')
            gameid = data.get('gameid')
            if gameid not in twotruthsandaliegames.keys():
                return jsonify({"error": "Game not found"}), 404
            if playerid not in twotruthsandaliegames[gameid].players.keys():
                return jsonify({'error': 'Player not found'}), 404
            if playerid in twotruthsandaliegames[gameid].tandl.keys():
                return jsonify({'error': "Already played"}), 403
            twotruthsandaliegames[gameid].newPlayer(t1, t2, l1, playerid)
            return jsonify({'good' : "Added truth and lies"}), 200
            


    return render_template("/truthandlie/join.html")


class truthAndLie:
    players: "dict[str, str]" = {}
    played: "dict[str, bool]" = {}
    tandl: "dict[str, tuple[str, str, str]]" = {}
    currtime = datetime.now()

    def newPlayer(self, t1: str, t2: str, l1: str, id: str):
        self.tandl[id] = (t1, t2, l1)


@app.route("/twotruthsandalie/host", methods=["GET", "POST"])
def pageHostTruthLies():
    if request.method == "GET":
        return render_template("/truthandlie/host.html")
    else:
        data = request.json
        id = data.get("id")
        log(f"New game started with id: [{id}]")
        twotruthsandaliegames[id] = truthAndLie()
        return jsonify({})

@app.route("/thingsnottodo", methods=["GET", "POST"])
def pageThingsNotToDo():
    if request.method == "GET":
        return render_template("/thingsnottodo/main.html")
    elif request.method == "POST":
        thingfile = open("data/thingsnottodo/things.txt", "r")
        stuff = thingfile.read().split('|||')
        stuff.reverse()
        res = []
        for i in stuff:
            res.append([i.split('---')[0].replace('\n', ''), i.split('---')[1].replace('\n', '')])
        return jsonify({"things" : res}), 200

@app.route("/thingsnottodo/suggest", methods=["GET", "POST"])
def pageThingsNotToDoSuggest():
    if request.method == "GET":
        return render_template("/thingsnottodo/suggest.html")

if __name__ == "__main__":
    app.run(debug=True)
