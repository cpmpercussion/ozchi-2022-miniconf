# pylint: disable=global-statement,redefined-outer-name
import argparse
import csv
import glob
import json
import os
import random

import yaml
from flask import Flask, jsonify, redirect, render_template, send_from_directory
from flask_frozen import Freezer
from flaskext.markdown import Markdown
from flask_flatpages import FlatPages


site_data = {}
by_uid = {}


def main(site_data_path):
    global site_data, extra_files
    extra_files = ["README.md"]
    # Load all for your sitedata one time.
    for f in glob.glob(site_data_path + "/*"):
        extra_files.append(f)
        name, typ = f.split("/")[-1].split(".")
        if typ == "json":
            site_data[name] = json.load(open(f))
        elif typ in {"csv", "tsv"}:
            site_data[name] = list(csv.DictReader(open(f)))
        elif typ == "yml":
            site_data[name] = yaml.load(open(f).read(), Loader=yaml.SafeLoader)

    for typ in ["papers", "speakers", "workshops", "creativity", "sessions"]:
        by_uid[typ] = {}
        for p in site_data[typ]:
            by_uid[typ][p["UID"]] = p

    # print(site_data["papers"])
    print("Data Successfully Loaded")
    return extra_files


# ------------- SERVER CODE -------------------->

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'
FLATPAGES_ROOT = 'pages'

app = Flask(__name__)
app.config.from_object(__name__)
freezer = Freezer(app)
markdown = Markdown(app)
pages = FlatPages(app)


# MAIN PAGES


def _data():
    data = {}
    data["config"] = site_data["config"]
    return data


@app.route("/")
def index():
    return redirect("/index.html")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(site_data_path, "favicon.ico")


# TOP LEVEL PAGES

@app.route("/index.html")
def home():
    data = _data()
    data["readme"] = open("README.md").read()
    data["committee"] = site_data["committee"]["committee"]
    data["speakers"] = site_data["speakers"]
    # data["pages"] = [p for p in pages]
    return render_template("index.html", **data)

@app.route("/volunteers.html")
def volunteers():
    data = _data()
    data["volunteers"] = open("./pages/volunteers.md").read()
    return render_template("volunteers.html", **data)

@app.route("/organisers.html")
def organisers():
    data = _data()
    data["committee"] = site_data["committee"]["committee"]
    return render_template("organisers.html", **data)

@app.route("/help.html")
def about():
    data = _data()
    data["FAQ"] = open("help.md").read()
    return render_template("help.html", **data)

@app.route('/<name>.html')
def post(name):
    data = _data()
    page = pages.get_or_404(name)
    return render_template("flatpage.html", page=page, **data)

@app.route("/papers.html")
def papers():
    data = _data()
    data["papers"] = site_data["papers"]
    return render_template("papers.html", **data)

@app.route("/papers2.html")
def papers2():
    data = _data()
    data["papers"] = site_data["papers"] # fix this
    random.shuffle(data["papers"])
    return render_template("papers2.html", **data)

@app.route("/creativity.html")
def creativity():
    data = _data()
    data["creativity"] = site_data["creativity"]
    data["creativity_gig"] = open("pages/creativity_gig.md").read()
    data["creativity_room"] = open("pages/creativity_room.md").read()
    return render_template("creative.html", **data)


@app.route("/paper_vis.html")
def paper_vis():
    data = _data()
    return render_template("papers_vis.html", **data)


@app.route("/calendar.html")
def schedule():
    data = _data()
    data["day"] = {
        "speakers": site_data["speakers"],
        "highlighted": [
            format_paper(by_uid["papers"][h["UID"]]) for h in site_data["highlighted"]
        ],
    }
    data["sessions"] = site_data["sessions"]
    data["speakers"] = site_data["speakers"]
    return render_template("schedule.html", **data)

@app.route("/schedule_list.html")
def schedule_list():
    data = _data()
    data["day"] = {
        "speakers": site_data["speakers"],
        "highlighted": [
            format_paper(by_uid["papers"][h["UID"]]) for h in site_data["highlighted"]
        ],
    }
    data["sessions"] = site_data["sessions"]
    data["speakers"] = site_data["speakers"]
    data["papers"] = site_data["papers"]
    data["calendar"] = site_data["main_calendar"]
    return render_template("schedule_list.html", **data)



@app.route("/workshops.html")
def workshops():
    data = _data()
    data["workshops"] = [
        format_workshop(workshop) for workshop in site_data["workshops"]
    ]
    return render_template("workshops.html", **data)


def extract_list_field(v, key):
    value = v.get(key, "")
    if isinstance(value, list):
        return value
    else:
        return value.split("|")


def format_paper(v):
    list_keys = ["authors", "keywords", "sessions"]
    list_fields = {}
    for key in list_keys:
        list_fields[key] = extract_list_field(v, key)

    return {
        "UID": v["UID"],
        "title": v["title"],
        "forum": v["UID"],
        "authors": list_fields["authors"],
        "keywords": list_fields["keywords"],
        "type": v.get("type", ""),
        "abstract": v["abstract"],
        "TLDR": v["abstract"],
        "bio": v.get("bio",""),
        "id": v.get("UID",""),
        "image": v.get("image",""),
        "recs": [],
        "sessions": list_fields["sessions"],
        # links to external content per poster
        "pdf_url": v.get("pdf_url", ""),  # render poster from this PDF
        "code_link": v.get("code", ""),  # link to code
        "link": v.get("link",""),  # link to paper
    }


def format_workshop(v):
    list_keys = ["authors"]
    list_fields = {}
    for key in list_keys:
        list_fields[key] = extract_list_field(v, key)

    return {
        "id": v["UID"],
        "title": v["title"],
        "organizers": list_fields["authors"],
        "abstract": v["abstract"],
        "timedate": v.get("timedate",""),
        "url": v.get("url",""),
    }


# ITEM PAGES

@app.route("/creative_<creative>.html")
def creative(creative):
    uid = creative
    v = by_uid["creativity"][uid]
    data = _data()
    data["paper"] = format_paper(v)
    return render_template("creative_submission.html", **data)

@app.route("/poster_<poster>.html")
def poster(poster):
    uid = poster
    v = by_uid["papers"][uid]
    data = _data()
    data["paper"] = format_paper(v)
    data["paper_content"] = v
    data["session"] = by_uid["sessions"][v.get("session_code", "")]
    return render_template("poster.html", **data)


@app.route("/speaker_<speaker>.html")
def speaker(speaker):
    uid = speaker
    v = by_uid["speakers"][uid]
    data = _data()
    data["speaker"] = v
    return render_template("speaker.html", **data)


@app.route("/workshop_<workshop>.html")
def workshop(workshop):
    uid = workshop
    v = by_uid["workshops"][uid]
    data = _data()
    data["workshop"] = format_workshop(v)
    return render_template("workshop.html", **data)

@app.route("/session_<session>.html")
def session(session):
    uid = session
    v = by_uid["sessions"][uid]
    data = _data()
    data["session"] = v
    data["papers"] = site_data["papers"]
    return render_template("session.html", **data)


@app.route("/chat.html")
def chat():
    data = _data()
    return render_template("chat.html", **data)


# FRONT END SERVING


@app.route("/papers.json")
def paper_json():
    json = []
    for v in site_data["papers"]:
        json.append(format_paper(v))
    return jsonify(json)


@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory("static", path)


@app.route("/serve_<path>.json")
def serve(path):
    return jsonify(site_data[path])


# --------------- DRIVER CODE -------------------------->
# Code to turn it all static


@freezer.register_generator
def generator():
    for paper in site_data["papers"]:
        yield "poster", {"poster": str(paper["UID"])}
    for speaker in site_data["speakers"]:
        yield "speaker", {"speaker": str(speaker["UID"])}
    for workshop in site_data["workshops"]:
        yield "workshop", {"workshop": str(workshop["UID"])}
    for session in site_data["sessions"]:
        yield "session", {"session": str(session["UID"])}
    for creative in site_data["creativity"]:
        yield "creative", {"creative": str(creative["UID"])}
    for page in pages:
        yield "post", {"name": page.path}
    for key in site_data:
        yield "serve", {"path": key}


def parse_arguments():
    parser = argparse.ArgumentParser(description="MiniConf Portal Command Line")

    parser.add_argument(
        "--build",
        action="store_true",
        default=False,
        help="Convert the site to static assets",
    )

    parser.add_argument(
        "-b",
        action="store_true",
        default=False,
        dest="build",
        help="Convert the site to static assets",
    )

    parser.add_argument("path", help="Pass the JSON data path and run the server")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_arguments()

    site_data_path = args.path
    extra_files = main(site_data_path)

    if args.build:
        freezer.freeze()
    else:
        debug_val = False
        if os.getenv("FLASK_DEBUG") == "True":
            debug_val = True

        app.run(port=5000, debug=debug_val, extra_files=extra_files)
