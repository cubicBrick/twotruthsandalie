from flask import Flask, render_template
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = (
    os.environ['SECRET_KEY']
)

@app.route('/')
def home():
    return render_template('./home.html')

if __name__ == '__main__':
    app.run(debug=True)