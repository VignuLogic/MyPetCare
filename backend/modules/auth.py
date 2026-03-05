from flask import request, render_template, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from db_config import get_db_connection


def signup():

    if request.method == "POST":

        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        mobile = request.form.get("mobile")
        email = request.form.get("email")
        password = request.form.get("password")

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO users (first_name, last_name, mobile, email, password)
        VALUES (%s,%s,%s,%s,%s)
        """

        cursor.execute(query,(first_name,last_name,mobile,email,hashed_password))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/login")

    return render_template("Signup.html")


def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"],password):
            session["user_id"] = user["id"]
            session["user_name"] = user["first_name"]
            return redirect("/myaccount")

        else:
            return "Invalid Email or Password"

    return render_template("Login.html")