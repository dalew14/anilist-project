
from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = "anime-project-secret-key"

API_URL = "http://127.0.0.1:8000/anime/"


def get_optional_int(value):
    return int(value) if value.strip() else None


def get_optional_float(value):
    return float(value) if value.strip() else None


def build_anime_data(include_anilist_id=True):
    data = {
        "title": request.form["title"].strip(),
        "average_score": get_optional_float(request.form["average_score"]),
        "popularity": get_optional_int(request.form["popularity"]),
        "episodes": get_optional_int(request.form["episodes"]),
        "release_year": get_optional_int(request.form["release_year"]),
        "season": request.form["season"] or None,
        "anime_format": request.form["anime_format"] or None,
        "genres": [
            genre.strip()
            for genre in request.form["genres"].split(",")
            if genre.strip()
        ],
        "description": request.form["description"] or None,
        "anilist_url": request.form["anilist_url"] or None
    }

    if include_anilist_id:
        data["anilist_id"] = int(request.form["anilist_id"])

    return data



@app.route("/")
def home():
    search = request.args.get("search", "").strip().lower()
    selected_genre = request.args.get("genre", "")
    selected_format = request.args.get("format", "")

    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        anime_list = response.json()

        genres = sorted({
            genre
            for anime in anime_list
            for genre in (anime.get("genres") or [])
        })

        formats = sorted({
            anime.get("anime_format")
            for anime in anime_list
            if anime.get("anime_format")
        })

        if search:
            anime_list = [
                anime for anime in anime_list
                if search in anime["title"].lower()
            ]

        if selected_genre:
            anime_list = [
                anime for anime in anime_list
                if selected_genre in (anime.get("genres") or [])
            ]

        if selected_format:
            anime_list = [
                anime for anime in anime_list
                if anime.get("anime_format") == selected_format
            ]

        return render_template(
            "index.html",
            anime_list=anime_list,
            genres=genres,
            formats=formats,
            search=search,
            selected_genre=selected_genre,
            selected_format=selected_format
        )

    except requests.RequestException:
        flash("Could not connect to the anime API.")
        return render_template(
            "index.html",
            anime_list=[],
            genres=[],
            formats=[],
            search=search,
            selected_genre=selected_genre,
            selected_format=selected_format
        )



@app.route("/anime/<int:anime_id>")
def anime_details(anime_id):
    try:
        response = requests.get(f"{API_URL}{anime_id}")
        response.raise_for_status()
        anime = response.json()
        return render_template("details.html", anime=anime)
    except requests.RequestException:
        flash("Could not find that anime.")
        return redirect(url_for("home"))


@app.route("/anime/create", methods=["GET", "POST"])
def create_anime():
    if request.method == "POST":
        try:
            data = build_anime_data()
            response = requests.post(API_URL, json=data)

            if response.status_code == 201:
                flash("Anime created successfully!")
                return redirect(
                    url_for("anime_details", anime_id=response.json()["id"])
                )

            flash(f"Could not create anime: {response.text}")

        except (requests.RequestException, ValueError) as error:
            flash(f"Error creating anime: {error}")

    return render_template("create.html")


@app.route("/anime/<int:anime_id>/edit", methods=["GET", "POST"])
def edit_anime(anime_id):
    if request.method == "POST":
        try:
            data = build_anime_data(include_anilist_id=False)
            response = requests.put(f"{API_URL}{anime_id}", json=data)

            if response.status_code == 200:
                flash("Anime updated successfully!")
                return redirect(url_for("anime_details", anime_id=anime_id))

            flash(f"Could not update anime: {response.text}")

        except (requests.RequestException, ValueError) as error:
            flash(f"Error updating anime: {error}")

    try:
        response = requests.get(f"{API_URL}{anime_id}")
        response.raise_for_status()
        anime = response.json()
        return render_template("edit.html", anime=anime)
    except requests.RequestException:
        flash("Could not find that anime.")
        return redirect(url_for("home"))


@app.route("/anime/<int:anime_id>/delete", methods=["POST"])
def delete_anime(anime_id):
    try:
        response = requests.delete(f"{API_URL}{anime_id}")

        if response.status_code == 200:
            flash("Anime deleted successfully!")
        else:
            flash(f"Could not delete anime: {response.text}")

    except requests.RequestException as error:
        flash(f"Error deleting anime: {error}")

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
