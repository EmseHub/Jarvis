from flask import Flask, render_template, request, jsonify, json


from chatbot.chatbot import get_response


app = Flask(
    __name__,
    template_folder="webfrontend",
    static_folder="webfrontend"
)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/data")
def data():
    reply = {}
    return jsonify(reply)


@app.post("/response")
def response():
    data = json.loads(request.data)
    message = data["message"]

    if (not message.strip()):
        return None

    response, diagnostic = get_response(message)

    reply = {
        "request": message,
        "response": response,
        "diagnostic": diagnostic
    }

    return jsonify(reply)
    # Website und Objekt zurückgeben:
    # return render_template("index.html", reply=jsonify(reply))


if (__name__) == "__main__":
    app.run(debug=True)
