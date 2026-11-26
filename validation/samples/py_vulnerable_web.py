import hashlib
import os
import pickle
import random
import sqlite3
import subprocess
import tempfile

import requests
import yaml
from flask import Flask, request, render_template_string

app = Flask(__name__)
app.config["WTF_CSRF_ENABLED"] = False        # EXPECT: CSRF Protection Disabled
DB_PASSWORD = "Sup3rS3cret!"                  # EXPECT: Hardcoded Secret
AWS_ACCESS = "AKIAIOSFODNN7EXAMPLE"           # EXPECT: Exposed Cloud Key / Private Key


@app.route("/user")
def get_user():
    name = request.args.get("name")
    cur = sqlite3.connect("app.db").cursor()
    cur.execute("SELECT * FROM users WHERE name = '" + name + "'")   # EXPECT: SQL Injection
    return str(cur.fetchall())


@app.route("/search")
def search():
    term = request.args.get("q")
    query = f"SELECT * FROM items WHERE title LIKE '%{term}%'"   # EXPECT: SQL Injection
    return str(sqlite3.connect("app.db").execute(query).fetchall())


@app.route("/report")
def report():
    uid = request.args.get("uid")
    sql = ("SELECT * FROM reports "              # EXPECT: SQL Injection
           "WHERE owner = " + uid)
    return str(sqlite3.connect("app.db").execute(sql).fetchall())


@app.route("/ping")
def ping():
    host = request.args.get("host")
    os.system("ping -c 1 " + host)                # EXPECT: OS Command Injection
    subprocess.call("nslookup " + host, shell=True)   # EXPECT: OS Command Injection
    return "done"


@app.route("/calc")
def calc():
    return str(eval(request.args.get("expr")))    # EXPECT: Dangerous eval/exec


@app.route("/hello")
def hello():
    name = request.args.get("name")
    return render_template_string("<h1>Hi " + name + "</h1>")   # EXPECT: Cross-Site Scripting (XSS)


@app.route("/load", methods=["POST"])
def load():
    obj = pickle.loads(request.data)              # EXPECT: Insecure Deserialization
    cfg = yaml.load(request.data)                 # EXPECT: Insecure Deserialization
    return str(obj) + str(cfg)


@app.route("/proxy")
def proxy():
    return requests.get(request.args.get("url")).text   # EXPECT: Server-Side Request Forgery


@app.route("/file")
def read_file():
    return open(request.args.get("path")).read()  # EXPECT: Path Traversal


@app.route("/admin/<int:user_id>")                # EXPECT: Possible Missing Authorization (IDOR)
def admin_view(user_id):
    is_admin = request.args.get("admin")          # EXPECT: Trusting Client-Supplied Role
    return str(user_id) if is_admin else "denied"


def hash_value(text):
    return hashlib.md5(text.encode()).hexdigest()     # EXPECT: Weak Hash Algorithm


def fetch(address):
    return requests.get(address, verify=False).text   # EXPECT: TLS Verification Disabled


def check_login(user_password):
    if user_password == "letmein":                # EXPECT: Insecure Authentication
        return True
    return False


def make_code():
    session_token = str(random.randint(100000, 999999))   # EXPECT: Insecure Randomness
    return session_token


def temp_name():
    return tempfile.mktemp()                      # EXPECT: Insecure Temp File


def log_login(password):
    print("login attempt", password)              # EXPECT: Sensitive Data in Logs


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)           # EXPECT: Debug Mode Enabled | Binds to All Interfaces
