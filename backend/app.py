from flask import Flask, render_template, session, redirect
from modules.auth import signup, login
from db_config import get_db_connection
from modules.pets import add_pet, view_pets, delete_pet


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
@app.route("/login", methods=["GET","POST"])
def login_route():
    return login()


# =========================
# DASHBOARD (MY ACCOUNT)
# =========================
@app.route("/myaccount")
def myaccount():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "my_account.html",
        user_name=session["user_name"]
    )


# GROOMING PAGE

@app.route("/grooming")
def grooming():

    pets = []

    if "user_id" in session:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM pets WHERE user_id=%s"
        cursor.execute(query,(session["user_id"],))
        pets = cursor.fetchall()

        cursor.close()
        conn.close()

    return render_template(
        "grooming.html",
        user_name=session.get("user_name"),
        pets=pets
    )


@app.route("/vaccination")
def vaccination():
    return render_template("vaccination.html")

@app.route("/care")
def care():
    return render_template("care.html")

@app.route("/about_us")
def about_us():
    return render_template("about_us.html")



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

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM pets"
    cursor.execute(query)

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


if __name__ == "__main__":
    app.run(debug=True)




