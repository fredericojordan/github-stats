import os

from flask import Flask, make_response, render_template
from stats import scrape


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "secret_l801#+#a&^1mz)_p&qyq51j51@20_74c-xi%&i)b*u_dt^2=2key"
)


@app.route("/")
def serve_template():
    json_data = scrape()

    template_context = {
        "results": json_data["results"],
        "len": len(json_data["results"]),
    }

    template = render_template("rank.html", **template_context)
    return make_response(template)


@app.route("/json")
def serve_json():
    return make_response(scrape())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
