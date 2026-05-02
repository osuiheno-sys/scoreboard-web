from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_logo(team_name):
    try:
        url = f"https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={team_name}"
        res = requests.get(url).json()
        if res["teams"]:
            logo_url = res["teams"][0]["strTeamBadge"]
            img = requests.get(logo_url)
            return Image.open(BytesIO(img.content)).convert("RGBA")
    except:
        return None
    return None

def create_scoreboard(team1, team2, score1, score2, scorers1, scorers2, bg_path=None):
    WIDTH, HEIGHT = 1200, 700

    if bg_path:
        bg = Image.open(bg_path).resize((WIDTH, HEIGHT))
    else:
        bg = Image.new("RGB", (WIDTH, HEIGHT), (5, 25, 20))

    draw = ImageDraw.Draw(bg)

    font_big = ImageFont.truetype("fonts/Orbitron-Bold.ttf", 120)
    font_mid = ImageFont.truetype("fonts/Orbitron-Bold.ttf", 50)
    font_small = ImageFont.truetype("fonts/Orbitron-Bold.ttf", 28)

    draw.rounded_rectangle((400,180,800,360), radius=40, fill=(0,0,0))

    draw.text((460,200), f"{score1}-{score2}", font=font_big, fill=(0,255,150))
    draw.text((150,500), team1, font=font_mid, fill="white")
    draw.text((850,500), team2, font=font_mid, fill="white")

    draw.text((150,560), scorers1, font=font_small, fill=(0,255,150))
    draw.text((850,560), scorers2, font=font_small, fill=(255,200,0))

    def paste_logo(logo, pos):
        if logo:
            logo = logo.resize((140,140))
            mask = Image.new("L", (140,140), 0)
            ImageDraw.Draw(mask).ellipse((0,0,140,140), fill=255)
            bg.paste(logo, pos, mask)

    paste_logo(get_logo(team1), (120,220))
    paste_logo(get_logo(team2), (940,220))

    path = "output.png"
    bg.save(path)
    return path

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    team1 = request.form["team1"]
    team2 = request.form["team2"]
    score1 = request.form["score1"]
    score2 = request.form["score2"]
    scorers1 = request.form["scorers1"]
    scorers2 = request.form["scorers2"]

    file = request.files.get("background")
    bg_path = None

    if file and file.filename:
        bg_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(bg_path)

    img_path = create_scoreboard(team1, team2, score1, score2, scorers1, scorers2, bg_path)

    return send_file(img_path, mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
