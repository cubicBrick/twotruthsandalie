from flask import Flask, render_template, request, redirect, jsonify, json, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy import *
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_login import LoginManager, UserMixin, login_user, logout_user

HTTP_BAD_REQUEST = 400
HTTP_UNOUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_NOT_ACCEPTABLE = 406
HTTP_SERVER_ERROR = 500
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_SERVER_OVERLOADED = 503

APPROVE_THINGS_NOT_TO_DO_SUGGUEST = 0b0000000000000001
ADMINISTRATOR = 0b1111111111111111

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookies over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies

IDLELIMIT = timedelta(seconds=60)
DEFAULTCHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
LOG_FILE = "./.log"
USER_FILE = "./data/userinfo.txt"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
random.seed(os.urandom(32))

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True,
                         nullable=False)
    passwordHash = db.Column(db.String(250),
                         nullable=False)
    permissions = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            user = Users(username=request.form.get("username"),
                        passwordHash=generate_password_hash(request.form.get("password")),
                        permissions=0)
            db.session.add(user)
            db.session.commit()
        except Exception:
            return jsonify({"error" : "User already registered"}), HTTP_FORBIDDEN
        return redirect(url_for("login"))
    return render_template("auth/register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(
            username=request.form.get("username")).first()
        if check_password_hash(request.form.get("password"), user.passwordHash):
            login_user(user)
            return redirect(url_for("home"))
        
    return render_template("auth/login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

def randString(length: int, charset=DEFAULTCHARSET):
    res = ""
    for i in range(length):
        res += charset[random.randint(0, len(charset) - 1)]
    return res

def log(s : str):
    pass

def is_logged_in():
    try:
        current_user = get_jwt_identity()
        return True
    except Exception:
        return False

@app.route("/", methods=["GET", "POST"])
def pageHome():
    if request.method == "GET":
        return render_template("home.html")
    else:
        if is_logged_in():
            return jsonify({"result" : "1"}), 200
        else:
            return jsonify({"result": "0"}), 200
        

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
            return jsonify({"good": "Game found", "userid": playerid}), HTTP_CREATED
        elif data.get("type") == "play":
            t1 = data.get("t1")
            t2 = data.get("t2")
            l1 = data.get("l1")
            playerid = data.get("id")
            gameid = data.get("gameid")
            if gameid not in twotruthsandaliegames.keys():
                return jsonify({"error": "Game not found"}), HTTP_NOT_FOUND
            if playerid not in twotruthsandaliegames[gameid].players.keys():
                return jsonify({"error": "Player not found"}), HTTP_NOT_FOUND
            if twotruthsandaliegames[gameid].played[playerid]:
                return jsonify({"error": "Already played"}), HTTP_FORBIDDEN
            if not twotruthsandaliegames[gameid].submitting:
                return jsonify({'error': 'Submitting phase closed'}), HTTP_FORBIDDEN
            twotruthsandaliegames[gameid].played[playerid] = True
            twotruthsandaliegames[gameid].newPlayer(t1, t2, l1, playerid)
            return jsonify({"good": "Added truth and lies"}), HTTP_OK

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
        if data.get("type") == "newid":
            id = randString(10)
            yourid = randString(16)
            log(f"New game started with id: [{id}] from player id [{yourid}]")
            twotruthsandaliegames[id] = truthAndLie()
            twotruthsandaliegames[id].host = yourid
            return jsonify({"id": id, "yourid": yourid}), HTTP_CREATED
        elif data.get("type") == "refresh":
            gameid = data.get("gameid")
            if gameid not in twotruthsandaliegames.keys():
                return jsonify({"error": "Game not found"}), HTTP_NOT_FOUND
            playerid = data.get("playerid")
            if not playerid == twotruthsandaliegames[gameid].host:
                return jsonify({"error": "Player is not host"}), HTTP_FORBIDDEN
            res:"list[list[str, bool]]" = []
            for i in twotruthsandaliegames[gameid].players.keys():
                res.append([twotruthsandaliegames[gameid].players[i],
                            twotruthsandaliegames[gameid].played[i]])
            return jsonify({'players': res}), HTTP_OK
        elif(data.get("type") == "finish"):
            gameid = data.get("gameid")
            if gameid not in twotruthsandaliegames.keys():
                return jsonify({"error": "Game not found"}), HTTP_NOT_FOUND
            playerid = data.get("playerid")
            if not playerid == twotruthsandaliegames[gameid].host:
                return jsonify({"error": "Player is not host"}), HTTP_FORBIDDEN
            twotruthsandaliegames[gameid].submitting = False
            return jsonify({"good" : "Finished submitting"}), HTTP_OK
            

@app.route("/thingsnottodo", methods=["GET", "POST"])
def pageThingsNotToDo():
    if request.method == "GET":
        return render_template("/thingsnottodo/main.html")
    elif request.method == "POST":
        thingfile = open("data/thingsnottodo/things.txt", "r")
        stuff = thingfile.read().split("|||")
        stuff.reverse()
        res = []
        for i in stuff:
            res.append(
                [
                    i.split("---")[0].replace("\n", ""),
                    i.split("---")[1].replace("\n", ""),
                ]
            )
        return jsonify({"things": res}), 200


class thingsNotToDoSugguestion:
    status: "str"
    thing: "str"
    id: "str"

    def __init__(self, thing: str, id: str):
        self.status = "WAITING FOR APPROVAL"
        self.thing = thing


thingsNotToDoSugguestions: "dict[str, thingsNotToDoSugguestion]" = {}


@app.route("/thingsnottodo/suggest", methods=["GET", "POST"])
def pageThingsNotToDoSuggest():
    if request.method == "GET":
        return render_template("/thingsnottodo/suggest.html")
    elif request.method == "POST":
        data = request.json
        thing = data.get("sugguestion")
        if len(thingsNotToDoSugguestions.keys()) > 500:
            return jsonify({"error": "Too many requests"}), HTTP_SERVER_OVERLOADED
        id = randString(16)
        thingsNotToDoSugguestions[id] = thingsNotToDoSugguestion(thing, id)
        return jsonify({"good": "Sugguestion added", "id": id}), HTTP_CREATED


@app.route("/thingsnottodo/check", methods=["GET", "POST"])
def pageThingsNotToDoCheck():
    if request.method == "GET":
        return render_template("/thingsnottodo/check.html")
    elif request.method == "POST":
        data = request.json
        id = data.get("id")
        if id not in thingsNotToDoSugguestions.keys():
            return jsonify({"error": "ID not found"}), HTTP_NOT_FOUND
        return (
            jsonify(
                {"status": thingsNotToDoSugguestions[id].status, "good": "ID found"}
            ),
            HTTP_OK,
        )

@app.route("/Rkpdjp")
def page_Rkpdjp():
    return render_template("/games/chromedino/index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
