import json
from flask import Flask, request, jsonify
from mangakakalot import Mangakakalot
from manganato import MangaNato

app = Flask(__name__)
manganato = MangaNato()
mangakakalot = Mangakakalot()


@app.route("/")
def home():
    return ""


@app.route("/recent", methods=['GET'])
def recent_update():
    pg_limit = int(request.args.get("limit"))
    site = request.args.get("site")
    if site == "manganato":
        data = manganato.get_recent_updates(pg_limit)
    elif site == "mangakakalot":
        data = mangakakalot.get_recent_updates(pg_limit)
    return jsonify(data)
        

@app.route("/genre-link", methods=['POST'])
def genre():
    data = request.get_json() if request.json() != None else json.loads(request.get_data().decode('utf-8'))
    site = data.get("site")
    genre = data.get("genre")
    state = data.get("state")
    type = data.get("type")
    if site == "manganato":
        try:
            link = manganato.get_genre_link(genre, state, type)
        except ValueError:
            link = "Error!"
    if site == "mangakakalot":
        try:
            link = mangakakalot.get_genre_link(genre)
        except ValueError:
            link = "Error!"
    return {
        "Link": link
    }


@app.route("/genre-list", methods=['GET', 'POST'])
def genre_list():
    if request.method == "GET":
        pg_limit = int(request.args.get("limit"))
        url = request.args.get("url")
        site = request.args.get("site")
    if request.method == "POST":
        data = request.get_json() if request.json() != None else json.loads(request.get_data().decode('utf-8'))
        pg_limit = int(data.get("limit"))
        url = data.get("url")
        site = data.get("site")
    if site == "manganato":
        respo = manganato.get_genre_list(url, pg_limit)
    elif site == "mangakakalot":
        respo = mangakakalot.get_genre_list(url, pg_limit)
    return respo
    
    
@app.route("/chapter-imgs", methods=['GET', 'POST'])
def chapter_imgs():
    if request.method == "GET":
        url = request.args.get("url")
        site = request.args.get("site")
    if request.method == 'POST':
        data = request.get_json() if request.json() != None else json.loads(request.get_data().decode('utf-8'))
        url = data.get("url")
        site = data.get("site")
    if site == "manganato":
        links = manganato.get_chapter_images(url)
    elif site == "mangakakalot":
        links = mangakakalot.get_chapter_images(url)
    return {
        "Urls": links
    }
    
    
@app.route("/info", methods=['GET', 'POST'])
def info():
    if request.method == 'GET':
        url = request.args.get("url")
        site = request.args.get("site")
    if request.method == "POST":
        data = request.get_json() if request.json() != None else json.loads(request.get_data().decode('utf-8'))
        url = data.get("url")
        site = data.get("site")
    if site == "manganato":
        respo = manganato.get_manga_info(url)
    elif site == "mangakakalot":
        respo = mangakakalot.get_manga_info(url)
    return respo


@app.route("/manga-chapters", methods=['GET', 'POST'])
def manga_chapters():
    if request.method == "GET":
        url = request.args.get("url")
        site = request.args.get("site")
    if request.method == 'POST':
        data = request.get_json() if request.json() != None else json.loads(request.get_data().decode('utf-8'))
        url = data.get("url")
        site = data.get("site")
    if site == "manganato":
        respo = manganato.get_manga_chapters(url)
    elif site == "mangakakalot":
        respo = mangakakalot.get_manga_chapters(url)
    return {
        "Title": respo[1],
        "Chapters": respo[0]
    }


@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        name = request.args.get("name")
        limit = int(request.args.get("limit"))
        site = request.args.get("site")
    if request.method == 'POST':
        data = request.get_json() if request.json() != None else json.loads(request.get_data().decode('utf-8'))
        name = data.get("name")
        limit = int(data.get("limit"))
        site = data.get("site")
    if site == "manganato":
        respo = manganato.search_manga(name, limit)
    elif site == "mangakakalot":
        respo = mangakakalot.search_manga(name, limit)
    return jsonify(respo)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5932, debug=False)