from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from slugify import slugify
from config import Config
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

mongo = PyMongo(app)
db = mongo.cx[app.config['DATABASE_NAME']]

# --- MODES (store lowercase, display uppercase) ---
MODES = [
    "question bank",
    "books",
    "notes",
    "all resources"
]

DISPLAY_MODE_NAMES = {
    "question bank": "QUESTION BANK",
    "books": "BOOKS",
    "notes": "NOTES",
    "all resources": "ALL RESOURCES"
}

# --- Subjects for each mode ---
QUESTION_BANK = [
    "59 batch cse, lu",
    "60 batch cse, lu",
    "61 batch cse, lu",
    "62 batch cse, lu",
    "63 batch cse, lu",
    "64 batch cse, lu",
    "65 batch cse, lu",
    "66 batch cse, lu",
]

BOOKS = [
    "c programming",
    "java programming",
    "data structures",
    "algorithms",
    "discrete mathematics",
]

NOTES = [
    "Descrete Mathematics",
    "Calculus",
    "English",
    "Instruction to Computing",
    "Others",
]

ALL_RESOURCES = [
    "C ",
    "C++",
    "Python",
    "Java",
    "Javasrip",
    "Html",
    "CSS",
    "Database"
]

# --- Helpers ---
def normalize(s: str) -> str:
    return s.strip().lower().replace("-", " ")

def valid_mode(mode: str) -> bool:
    return normalize(mode) in MODES

def valid_subject(mode: str, subject: str) -> bool:
    nm = normalize(mode)
    ns = normalize(subject)
    if nm == "question bank":
        return ns in QUESTION_BANK
    elif nm == "books":
        return ns in BOOKS
    elif nm == "notes":
        return ns in NOTES
    elif nm == "all resources":
        return ns in ALL_RESOURCES
    return False

def generate_slug(title: str) -> str:
    return slugify(title)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please login to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.context_processor
def inject_globals():
    return dict(
        QUESTION_BANK=QUESTION_BANK,
        BOOKS=BOOKS,
        NOTES=NOTES,
        ALL_RESOURCES=ALL_RESOURCES,
        MODES=[DISPLAY_MODE_NAMES[m] for m in MODES]
    )

# --- Routes ---
@app.route("/")
def home():
    return render_template("home.html", modes=[DISPLAY_MODE_NAMES[m] for m in MODES])

@app.route("/<mode>")
def mode_page(mode):
    nm = normalize(mode)
    if not valid_mode(nm):
        return render_template("error.html", message="Invalid Mode"), 404

    if nm == "question bank":
        subjects = QUESTION_BANK
    elif nm == "books":
        subjects = BOOKS
    elif nm == "notes":
        subjects = NOTES
    elif nm == "all resources":
        subjects = ALL_RESOURCES
    else:
        subjects = []

    return render_template("mode.html", mode=DISPLAY_MODE_NAMES[nm], subjects=subjects)

@app.route("/<mode>/<subject>")
def subject_page(mode, subject):
    nm = normalize(mode)
    ns = normalize(subject)
    if not valid_mode(nm) or not valid_subject(nm, ns):
        return render_template("error.html", message="Invalid Mode or Subject"), 404

    pdfs = list(db.pdfs.find({"mode": nm, "subject": ns}))
    return render_template("subject.html", mode=DISPLAY_MODE_NAMES[nm], subject=ns, pdfs=pdfs)

@app.route("/pdf/<subject>/<filename>")
def pdf_view(subject, filename):
    ns = normalize(subject)
    pdf = db.pdfs.find_one({"subject": ns, "filename": filename})
    if not pdf:
        return render_template("error.html", message="PDF not found"), 404
    return render_template("pdf_view.html", pdf=pdf)

# --- Admin Auth ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username == app.config["ADMIN_USERNAME"] and password == app.config["ADMIN_PASSWORD"]:
            session["admin_logged_in"] = True
            flash("Logged in successfully.", "success")
            return redirect(url_for("upload"))
        else:
            flash("Invalid credentials.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    flash("Logged out.", "info")
    return redirect(url_for("home"))

# --- Upload ---
@app.route("/upload", methods=["GET", "POST"])
@admin_required
def upload():
    if request.method == "POST":
        mode = normalize(request.form.get("mode", ""))
        subject = normalize(request.form.get("subject", ""))
        title = request.form.get("title", "").strip()
        link = request.form.get("link", "").strip()
        description = request.form.get("description", "").strip()
        photo = request.form.get("photo", "").strip()

        errors = []

        if mode not in MODES:
            errors.append("Invalid mode selected.")
        if not valid_subject(mode, subject):
            errors.append("Invalid subject for selected mode.")
        if not title:
            errors.append("Title is required.")
        if not link:
            errors.append("Link is required.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template(
                "upload.html",
                modes=[DISPLAY_MODE_NAMES[m] for m in MODES],
                question_bank=QUESTION_BANK,
                books=BOOKS,
                notes=NOTES,
                all_resources=ALL_RESOURCES,
                form=request.form
            )

        filename = generate_slug(title)

        exists = db.pdfs.find_one({"filename": filename, "subject": subject, "mode": mode})
        if exists:
            flash("A PDF with this title already exists for this subject and mode.", "danger")
            return render_template(
                "upload.html",
                modes=[DISPLAY_MODE_NAMES[m] for m in MODES],
                question_bank=QUESTION_BANK,
                books=BOOKS,
                notes=NOTES,
                all_resources=ALL_RESOURCES,
                form=request.form
            )

        pdf_data = {
            "mode": mode,
            "subject": subject,
            "title": title,
            "filename": filename,
            "link": link,
            "description": description,
            "photo": photo,
        }
        db.pdfs.insert_one(pdf_data)

        flash("PDF metadata uploaded successfully!", "success")
        return redirect(url_for("subject_page", mode=mode.replace(" ", "-"), subject=subject.replace(" ", "-")))

    return render_template(
        "upload.html",
        modes=[DISPLAY_MODE_NAMES[m] for m in MODES],
        question_bank=QUESTION_BANK,
        books=BOOKS,
        notes=NOTES,
        all_resources=ALL_RESOURCES,
        form=None
    )

# --- Search ---
@app.route("/search")
def search():
    query = request.args.get("query", "").strip()
    if not query:
        return render_template("search_results.html", results=[], query=query)

    search_filter = {
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"subject": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
        ]
    }

    results = list(db.pdfs.find(search_filter))
    return render_template("search_results.html", results=results, query=query)

# --- Error Handlers ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", message="Page not found (404)"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template("error.html", message="Internal server error (500)"), 500

if __name__ == "__main__":
    app.run(debug=True)

