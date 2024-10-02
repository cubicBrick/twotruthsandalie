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

HTTP_BAD_REQUEST = 400
HTTP_UNOUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_NOT_ACCEPTABLE = 406
HTTP_SERVER_ERROR = 500
HTTP_OK = 200
HTTP_CREATED = 201

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
                return jsonify({"error": "Game not found"}), HTTP_NOT_FOUND
            playerid = randString(32)
            twotruthsandaliegames[gameid].players[playerid] = username
            twotruthsandaliegames[gameid].played[playerid] = False
            return jsonify({"good": "Game found", "userid":playerid}), HTTP_CREATED
        elif data.get("type") == "play":
            t1 = data.get('t1')
            t2 = data.get('t2')
            l1 = data.get('l1')
            playerid = data.get('id')
            gameid = data.get('gameid')
            if gameid not in twotruthsandaliegames.keys():
                return jsonify({"error": "Game not found"}), HTTP_NOT_FOUND
            if playerid not in twotruthsandaliegames[gameid].players.keys():
                return jsonify({'error': 'Player not found'}), HTTP_NOT_FOUND
            if twotruthsandaliegames[gameid].played[playerid]:
                return jsonify({'error': "Already played"}), HTTP_FORBIDDEN
            if not twotruthsandaliegames[gameid].submitting:
                return jsonify({'error', 'Submitting phase closed'}), HTTP_FORBIDDEN
            twotruthsandaliegames[gameid].played[playerid] = True
            twotruthsandaliegames[gameid].newPlayer(t1, t2, l1, playerid)
            return jsonify({'good' : "Added truth and lies"}), HTTP_OK
        
    return render_template("/truthandlie/join.html")


class truthAndLie:
    players: "dict[str, str]" = {}
    played: "dict[str, bool]" = {}
    tandl: "dict[str, tuple[str, str, str]]" = {}
    host: "str" = ""
    submitting = True
    currtime = datetime.now()

    def newPlayer(self, t1: str, t2: str, l1: str, id: str):
        self.tandl[id] = (t1, t2, l1)


@app.route("/twotruthsandalie/host", methods=["GET", "POST"])
def pageHostTruthLies():
    if request.method == "GET":
        return render_template("/truthandlie/host.html")
    elif request.method == "POST":
        data = request.json
        if(data.get("type") == "newid"):
            id = randString(10)
            yourid = randString(16)
            log(f"New game started with id: [{id}] from player id [{yourid}]")
            twotruthsandaliegames[id] = truthAndLie()
            twotruthsandaliegames[id].host = yourid
            return jsonify({'id' : id, 'yourid': yourid}), HTTP_CREATED
        elif(data.get("type") == "refresh"):
            gameid = data.get("gameid")
            if gameid not in twotruthsandaliegames.keys():
                return jsonify({"error": "Game not found"}), HTTP_NOT_FOUND
            playerid = data.get("playerid")
            if not playerid == twotruthsandaliegames[gameid].host:
                return jsonify({"error": "player is not host"}), HTTP_FORBIDDEN
            res:"list[list[str, bool]]" = []
            for i in twotruthsandaliegames[gameid].players.keys():
                res.append([twotruthsandaliegames[gameid].players[i],
                            twotruthsandaliegames[gameid].played[i]])
            return jsonify({'players': res}), HTTP_OK
            


if __name__ == "__main__":
    app.run(debug=True)
