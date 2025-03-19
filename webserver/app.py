from flask import Flask

# instance of flask application
app = Flask(__name__)

# home route that returns below text when root url is accessed
@app.route("/")
def hello_world():
    return "<p>Fuck off max</p>"

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')