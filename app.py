import random
import json
import sqlite3
from flask import Flask, render_template, url_for, redirect, request


def load_config() -> dict:
    """Open the config.json file and return the data"""
    f = open('config.json', 'r')
    data = json.load(f)
    return data


app = Flask(__name__)
app.debug = True
app.static_folder = "./static"
db = sqlite3.connect("app.db", check_same_thread=False)
cursor = db.cursor()


# create table - first time use only
# INFO: uncomment this only for the first time use
#cursor.execute("""CREATE TABLE IF NOT EXISTS data(
    #key TEXT,
    #url TEXT,
    #num_visited INTEGER
#)""")
#db.commit()


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/shorturi", methods=["POST"])
def shorturi():
    url = request.form.get('inp_uri')
    random_byte = random.getrandbits(128)
    key = "%03x" % random_byte # thanks to stackoverflow
    cropped_key = key[:5]
    cursor.execute("INSERT INTO data(key, url, num_visited) VALUES(?,?,?)", (cropped_key, url, 0))
    db.commit()
    return render_template('shortner.html', shorted_url=f'http://127.0.0.1:5000/{cropped_key}')


@app.route("/<key>")
def redirect(key):
    fetch = cursor.execute("SELECT * FROM data WHERE key = ?", (key,))
    data = fetch.fetchone()
    if data is None:
        return """
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Key Not Found</title>
                <head>
                <body>
                    <script>
                        alert('Key Not Found, retry!!');
                    </script>
                </body>
            </html>
        """
    else:
        url = data[1]
        num = data[2]
        cursor.execute("UPDATE data SET num_visited = ? WHERE key = ?", (num+1, key))
        db.commit()
        return """
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Redirecting...</title>
                <head>
                <body>
                    <script>
                        window.location.href = "{url}";
                    </script>
                </body>
            </html>
        """.format(url=url)


if __name__ == '__main__':
    try:
        json_data = load_config()
        app.secret_key = json_data["secret_key"]
        app.run(port=json_data["port"], host=json_data["host"])
    except Exception as e:
        print('Error while trying to run the script\nTraceback:\n{}'.format(e))
