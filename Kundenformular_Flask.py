from flask import Flask, render_template, request, redirect, url_for, flash
from config import HEADER
from google_sheets import ensure_header, append_customer
from dotenv import load_dotenv  # .env laden
import os

load_dotenv()  # .env Variablen (SECRET_KEY, SPREADSHEET_ID, GOOGLE_SERVICE_ACCOUNT_JSON)
print("ENV check:",
      "FILE =", os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_FILE"),
      "| RAW set =", os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON") is not None)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")


def validate(data: dict):
    errors = []
    if not data.get("Name"):
        errors.append("Name fehlt.")
    email = data.get("Email", "")
    if "@" not in email or "." not in email:
        errors.append("Bitte eine gültige E-Mail eingeben.")
    return errors


@app.route("/", methods=["GET", "POST"])
def kundenformular():
    if request.method == "POST":
        # 1) Daten aus dem Formular einsammeln
        data = {}
        for col in HEADER:
            if col == "Trainingsschwerpunkt":
                # Mehrfachauswahl
                data[col] = request.form.getlist(col)
            else:
                # Alle anderen Felder als String
                data[col] = (request.form.get(col, "") or "").strip()

        # 2) Validierung
        errors = validate(data)
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("form.html")  # bei Bedarf: Werte vorbefüllen

        # 3) Schreiben ins Google Sheet
        try:
            ensure_header()
            append_customer(data)
            flash("Kunde wurde in Google Sheets eingetragen!", "success")
        except Exception as e:
            flash(f"Fehler beim Speichern in Google Sheets: {e}", "error")
            return render_template("form.html")

        # 4) Redirect zur Zusammenfassung – Listen hübsch zu String
        data_qs = {k: (", ".join(v) if isinstance(v, list) else v) for k, v in data.items()}
        return redirect(url_for("summery", **data_qs))

    # GET: Formular anzeigen
    return render_template("form.html")


@app.route("/summery")
def summery():
    data = dict(request.args)
    return render_template("summery.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)