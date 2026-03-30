from flask import Flask, render_template, session, redirect, request, jsonify
from modules.auth import signup, login
from db_config import get_db_connection
from modules.pets import add_pet, delete_pet
from modules.reminders import get_reminders_for_user, auto_reminder_job   # ← fixed import
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from modules.grooming import add_grooming, view_grooming, delete_grooming


app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend",
    static_url_path=""
)

app.secret_key = "petcare_secret_key"


# =========================
# HOME PAGE
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# SIGNUP
# =========================
@app.route("/signup", methods=["GET", "POST"])
def signup_route():
    return signup()


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login_route():
    return login()


# =========================
# DASHBOARD (MY ACCOUNT)
# =========================
@app.route("/myaccount")
def myaccount():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("my_account.html", user_name=session["user_name"])


# =========================
# GROOMING PAGE
# =========================
@app.route("/grooming", methods=["GET", "POST"])
def grooming():
    if request.method == "POST":
        return add_grooming()
    return view_grooming()

@app.route("/delete_grooming/<int:grooming_id>")
def delete_grooming_route(grooming_id):
    return delete_grooming(grooming_id)

# =========================
# BOOKING PAGE  (GET = show form)
# =========================
@app.route("/booking")
def booking():
    pets = []
    if "user_id" in session:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pets WHERE user_id=%s", (session["user_id"],))
        pets = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template("booking.html", pets=pets)


# =========================
# SUBMIT BOOKING  (POST)
# =========================
@app.route("/submit_booking", methods=["POST"])
def submit_booking():
    if "user_id" not in session:
        return redirect("/login")

    user_id      = session["user_id"]
    pet_id       = request.form.get("pet_id")
    owner_name   = request.form.get("owner_name")
    phone        = request.form.get("phone")
    pet_size     = request.form.get("pet_size")
    pet_breed    = request.form.get("pet_breed", "")
    pet_age      = request.form.get("pet_age", "")
    booking_date = request.form.get("booking_date")
    time_slot    = request.form.get("time_slot")
    shop_name    = request.form.get("shop_name", "")
    notes        = request.form.get("notes", "")

    # Multi-value fields
    services     = request.form.getlist("services")   # list of service values
    addons       = request.form.getlist("addons")     # list of addon values

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get service IDs
    cursor.execute("SELECT id, service_name FROM services")
    service_rows = cursor.fetchall()
    service_map  = {row['service_name'].strip().lower(): row['id'] for row in service_rows}

    # Map grooming sub-types to the 'grooming' service id
    grooming_id = service_map.get('grooming')

    # Insert one booking row per service selected
    for svc_value in services:
        # Use the grooming service_id for all grooming sub-services
        svc_id = service_map.get(svc_value.replace('_', ' '), grooming_id)
        if not svc_id:
            svc_id = grooming_id   # fallback

        cursor.execute(
            """INSERT INTO bookings
               (user_id, pet_id, service_id, shop_name, booking_date,
                time_slot, pet_size, pet_breed, pet_age, owner_phone,
                addons, notes, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
            (
                user_id, pet_id, svc_id, shop_name, booking_date,
                time_slot, pet_size, pet_breed, pet_age, phone,
                ",".join(addons), notes
            )
        )

    conn.commit()
    cursor.close()
    conn.close()

    # Redirect back to dashboard with success flag
    return redirect("/myaccount?booking=success")


# =========================
# VACCINATION
# =========================
@app.route("/vaccination")
def vaccination():
    return render_template("vaccination.html")


# =========================
# CARE / ABOUT / FOOD
# =========================
@app.route("/care")
def care():
    return render_template("care.html")

@app.route("/about_us")
def about_us():
    return render_template("about_us.html")

@app.route("/pet-food")
def pet_food():
    return render_template("pet_food.html")

@app.route("/needs")
def needs():
    return render_template("needs.html")


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =========================
# ADD PET
# =========================
@app.route("/add_pet", methods=["GET", "POST"])
def add_pet_route():
    return add_pet()


# =========================
# VIEW PETS
# =========================
@app.route("/pets")
def view_pets_route():
    if "user_id" not in session:
        return redirect("/login")
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pets WHERE user_id=%s", (session["user_id"],))
    pets = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("pets.html", pets=pets)


# =========================
# DELETE PET
# =========================
@app.route("/delete_pet/<int:pet_id>")
def delete_pet_route(pet_id):
    return delete_pet(pet_id)


# =========================
# REMINDERS PAGE  ← FIXED
# =========================
@app.route("/reminders")
def reminders():
    if "user_id" not in session:
        return redirect("/login")

    reminder_list = get_reminders_for_user(session["user_id"])   # ← use module function

    return render_template("reminders.html", reminders=reminder_list)


# =========================
# BOOK PET (demo route)
# =========================
@app.route("/book/<path:pet_name>")
def book_pet(pet_name):
    return f"Booking page for {pet_name}"


# =========================
# SCHEDULER  ← FIXED
# =========================
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=auto_reminder_job,          # ← correct function from reminders module
    trigger="interval",
    hours=1                          # run every hour, not every minute
)
scheduler.start()



import json
import os

@app.route("/product.json")
def product_json():
    file_path = os.path.join(app.root_path, "../frontend/templates/product.json")
    
    with open(file_path) as f:
        data = json.load(f)
    
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)