from flask import Flask, render_template,session, redirect
from modules.auth import signup, login
from db_config import get_db_connection

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend",
    static_url_path=""
)

@app.route("/")
def home():
    return render_template("PetCare.html")

# Signup route
@app.route("/signup", methods=["GET", "POST"])
def signup_route():
    return signup()


#login route
@app.route("/login", methods=["GET","POST"])
def login_route():
    return login()

# Dashboard page after login
@app.route("/myaccount")
def myaccount():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "MyAcc.html",
        user_name=session["user_name"]
    )

# Logout route
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)