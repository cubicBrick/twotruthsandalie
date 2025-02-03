from imports import *

LOGIN_EXPIRE = timedelta(hours=12)

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

DEFAULT_PERMS = 0b0000000000000000
APPROVE_THINGS_NOT_TO_DO_SUGGUEST = 0b0000000000000001
EDIT_THINGS_NOT_TO_DO_QUEUE = 0b0000000000000010
ADMINISTRATOR = 0b1111111111111111
THINGS_NOT_TO_DO_ADMINISTRATOR = (
    EDIT_THINGS_NOT_TO_DO_QUEUE | APPROVE_THINGS_NOT_TO_DO_SUGGUEST | 0b0000000000000100
)
TRUTH_AND_LIE_ADMINISTRATOR = 0b0000000000001000

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
app.config["SESSION_COOKIE_SECURE"] = True  # Only send cookies over HTTPS
app.config["SESSION_COOKIE_HTTPONLY"] = True  # Prevent JavaScript access to cookies
socketio = SocketIO(app)
IDLELIMIT = timedelta(seconds=60)
DEFAULTCHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
LOG_FILE = "./.log"
USER_FILE = "./data/userinfo.txt"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
random.seed(os.urandom(32))

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    passwordHash = db.Column(db.String(505), nullable=False)
    permissions = db.Column(db.Integer, nullable=False)


with app.app_context():
    db.create_all()


@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)


IS_REGSITERING = False


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not IS_REGSITERING:
            return jsonify({"error": "Registering is turned off"}), HTTP_FORBIDDEN
        try:
            user = Users(
                username=request.form.get("username")[:15],
                passwordHash=generate_password_hash(request.form.get("password"))[:500],
                permissions=DEFAULT_PERMS,
            )
            db.session.add(user)
            db.session.commit()
        except Exception:
            return (
                jsonify({"error": "User already registered! Choose another username"}),
                HTTP_FORBIDDEN,
            )
        return redirect("/login")
    if is_logged_in():
        return redirect("/login")
    return render_template("auth/register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form.get("username")).first()
        if not user:
            return redirect("/authFailed")
        if check_password_hash(user.passwordHash, request.form.get("password")):
            if not login_user(user, remember=True, force=True, duration=LOGIN_EXPIRE):
                return redirect("/static/authFailed.html")
            return redirect("/")
        return redirect("/static/authFailed.html")
    return render_template("auth/login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


def is_logged_in():
    return current_user.is_authenticated


def randString(length: int, charset=DEFAULTCHARSET):
    res = ""
    for i in range(length):
        res += charset[random.randint(0, len(charset) - 1)]
    return res


def log(s: str):
    pass


@app.route("/", methods=["GET", "POST"])
def pageHome():
    if request.method == "GET":
        return render_template("home.html")
    else:
        if is_logged_in():
            return jsonify({"result": "1"}), HTTP_OK
        else:
            return jsonify({"result": "0"}), HTTP_OK


######################################
#       ^^^ Authentication ^^^       #
#    vvv Two Truths and a Lie vvv    #
######################################


@app.route("/twotruthsandalie/home")
def pageTruthsLiesHome():
    return render_template("./truthandlie/main.html")

twotruthsandaliegames: "dict[str, truthAndLie]" = {}

class truthAndLie:
    def __init__(self):
        self.players = {}
        self.played = {}
        self.tandl = {}
        self.score = {}
        self.order = []
        self.rorder = [0, 1, 2]
        self.liepos = 0
        self.host = ""
        self.submitting = True
        self.done = False
        self.currtime = datetime.now()

    def add_player(self, playerid, username):
        self.players[playerid] = username
        self.played[playerid] = False
        self.score[playerid] = 0

    def player_exists(self, playerid):
        return playerid in self.players

    def player_has_played(self, playerid):
        return self.played.get(playerid, False)

    def is_submitting_phase(self):
        return self.submitting

    def add_truths_and_lie(self, playerid, t1, t2, l1):
        self.played[playerid] = True
        self.tandl[playerid] = (t1, t2, l1)

    def get_phase(self):
        if self.submitting:
            return "submitting"
        elif self.done:
            return "done"
        else:
            return "guessing" + str(len(self.order))

    def can_fetch_data(self):
        return not (self.submitting or self.done)

    def get_player_data(self):
        order = self.order[0]
        g0 = self.tandl[order][self.rorder[0]]
        g1 = self.tandl[order][self.rorder[1]]
        g2 = self.tandl[order][self.rorder[2]]
        return g0, g1, g2

    def finish_submit(self):
        self.submitting = False
        self.order = list(self.players.keys())
        random.shuffle(self.order)

    def next(self):
        if len(self.order) <= 1:
            return False
        self.order.pop(0)
        random.shuffle(self.order)
        self.liepos = self.rorder.index(0)
        return True

@socketio.on('join')
def handle_join(data):
    gameid = data.get('gameid')
    username = data.get('username')
    game = twotruthsandaliegames.get(gameid)

    if not game:
        emit('error', {'error': 'Game not found'})
        return

    playerid = randString(32)
    game.add_player(playerid, username)
    emit('joined', {'userid': playerid})

@socketio.on('play')
def handle_play(data):
    gameid = data.get('gameid')
    playerid = data.get('id')
    game = twotruthsandaliegames.get(gameid)

    if not game or not game.player_exists(playerid):
        emit('error', {'error': 'Game or player not found'})
        return

    if game.player_has_played(playerid):
        emit('error', {'error': 'Already played'})
        return

    if not game.is_submitting_phase():
        emit('error', {'error': 'Submitting phase closed'})
        return

    t1, t2, l1 = data.get('t1'), data.get('t2'), data.get('l1')
    game.add_truths_and_lie(playerid, t1, t2, l1)
    emit('played', {'message': 'Added truth and lies'})

@socketio.on('refresh')
def handle_refresh(data):
    gameid = data.get('gameid')
    playerid = data.get('id')
    game = twotruthsandaliegames.get(gameid)

    if not game or not game.player_exists(playerid):
        emit('error', {'error': 'Game or player not found'})
        return

    phase = game.get_phase()
    emit('phase', {'phase': phase})

@socketio.on('get')
def handle_get(data):
    gameid = data.get('gameid')
    playerid = data.get('id')
    game = twotruthsandaliegames.get(gameid)

    if not game or not game.player_exists(playerid):
        emit('error', {'error': 'Game or player not found'})
        return

    if not game.can_fetch_data():
        emit('error', {'error': 'Not in correct phase'})
        return

    g0, g1, g2 = game.get_player_data()
    emit('data', {'g0': g0, 'g1': g1, 'g2': g2})

@socketio.on('newid')
def handle_newid():
    id = randString(10)
    yourid = randString(16)
    log(f"New game started with id: [{id}] from player id [{yourid}]")
    twotruthsandaliegames[id] = truthAndLie()
    twotruthsandaliegames[id].host = yourid
    emit('newid', {'id': id, 'yourid': yourid})

@socketio.on('finish')
def handle_finish(data):
    gameid = data.get('gameid')
    playerid = data.get('playerid')
    game = twotruthsandaliegames.get(gameid)

    if not game or not playerid == game.host:
        emit('error', {'error': 'Game not found or player is not host'})
        return

    game.finish_submit()
    emit('finished', {'message': 'Finished submitting'})

@socketio.on('next')
def handle_next(data):
    gameid = data.get('gameid')
    playerid = data.get('playerid')
    game = twotruthsandaliegames.get(gameid)

    if not game or not playerid == game.host:
        emit('error', {'error': 'Game not found or player is not host'})
        return

    if game.next():
        emit('next', {'message': 'Moved to next random player'})
    else:
        emit('end', {'message': 'No more players'})

######################################
#    ^^^ Two truths and a lie ^^^    #
#      vvv Things not to do vvv      #
######################################


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
        return jsonify({"things": res}), HTTP_OK


class thingsNotToDoSugguestion:
    status: "str"
    thing: "str"
    id: "str"
    ac: "int"

    def __init__(self, thing: str, id: str):
        self.status = "WAITING FOR APPROVAL"
        self.thing = thing
        self.id = id
        self.ac = 0


thingsNotToDoSugguestions: "dict[str, thingsNotToDoSugguestion]" = {}


@app.route("/thingsnottodo/suggest", methods=["GET", "POST"])
def pageThingsNotToDoSuggest():
    if request.method == "GET":
        return render_template("/thingsnottodo/suggest.html")
    elif request.method == "POST":
        data = request.json
        thing: "str" = data.get("sugguestion")[:60]
        thing.replace("|||", "***")
        thing.replace("---", "***")
        thing.replace("\n", "*")
        thing.replace("\r", "*")
        if len(thingsNotToDoSugguestions.keys()) > 500:
            return jsonify({"error": "Too many requests"}), HTTP_SERVER_OVERLOADED
        if len(thing) == 0:
            return jsonify({"error": "No submission"}), HTTP_BAD_REQUEST
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


@app.route("/thingsnottodo/verify", methods=["GET", "POST"])
@login_required
def pageThingsNotToDoVerify():
    global thingsNotToDoSugguestions
    if request.method == "GET":
        if not (current_user.permissions & APPROVE_THINGS_NOT_TO_DO_SUGGUEST):
            return redirect("/login")
        return render_template("/thingsnottodo/verify.html")
    elif request.method == "POST":
        data = request.json
        if not (current_user.permissions & APPROVE_THINGS_NOT_TO_DO_SUGGUEST):
            return jsonify({"error": "Forbidden"}), HTTP_FORBIDDEN
        if data.get("type") == "get":
            if len(thingsNotToDoSugguestions.keys()) == 0:
                return jsonify({"error": "No sugguestions"}), HTTP_NOT_FOUND
            keyListD = thingsNotToDoSugguestions.keys()
            keyList = []
            for i in keyListD:
                keyList.append(i)
            sid = keyList[random.randint(0, len(keyList) - 1)]
            return jsonify(
                {
                    "status": thingsNotToDoSugguestions[sid].status,
                    "id": thingsNotToDoSugguestions[sid].id,
                    "content": thingsNotToDoSugguestions[sid].thing,
                }
            )
        elif data.get("type") == "accept":
            subid = data.get("id")
            if subid not in thingsNotToDoSugguestions.keys():
                return jsonify({"error": "ID not found"}), HTTP_NOT_FOUND
            thingsNotToDoSugguestions[subid].status = "ACCEPTED"
            thingsNotToDoSugguestions[subid].ac = 1
            return jsonify({"good": "Queued to update"}), HTTP_CREATED
        elif data.get("type") == "deny":
            subid = data.get("id")
            if subid not in thingsNotToDoSugguestions.keys():
                return jsonify({"error": "ID not found"}), HTTP_NOT_FOUND
            thingsNotToDoSugguestions[subid].status = "DENIED"
            thingsNotToDoSugguestions[subid].ac = -1
            return jsonify({"good": "Denied request"}), HTTP_OK
        elif data.get("type") == "fullclear":
            if not (current_user.permissions & THINGS_NOT_TO_DO_ADMINISTRATOR):
                return (
                    jsonify(
                        {"error": "You do not have permissions to do this action!"}
                    ),
                    HTTP_FORBIDDEN,
                )
            thingsNotToDoSugguestions.clear()
            return jsonify({"good": "teapot"}), 418
        elif data.get("type") == "softclear":
            if not (current_user.permissions & EDIT_THINGS_NOT_TO_DO_QUEUE):
                return (
                    jsonify(
                        {"error": "You do not have permissions to do this action!"}
                    ),
                    HTTP_FORBIDDEN,
                )
            newt: "dict[str, thingsNotToDoSugguestion]" = {}
            things = open("./data/thingsnottodo/things.txt", "a")
            tfLen = 0
            with open("./data/thingsnottodo/things.txt", "r") as f:
                tfLen = len(f.read().split("|||")) + 1
            for i in thingsNotToDoSugguestions.keys():
                if thingsNotToDoSugguestions[i].ac == 1:
                    things.write(
                        "|||\n"
                        + str(tfLen)
                        + "---"
                        + thingsNotToDoSugguestions[i].thing
                    )
                    tfLen += 1
                elif thingsNotToDoSugguestions[i].ac == 0:
                    newt[i] = thingsNotToDoSugguestions[i]
            thingsNotToDoSugguestions = newt
            return jsonify({"good": "added all checked sugguestions"}), HTTP_CREATED
        return jsonify({"error": "bad request"}), HTTP_BAD_REQUEST


######################################
#      ^^^ Things not to do ^^^      #
#               vvvvvv               #
######################################

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
