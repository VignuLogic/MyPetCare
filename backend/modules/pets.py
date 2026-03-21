from flask import request, render_template, redirect, session
from db_config import get_db_connection


# =========================
# ADD PET
# =========================
def add_pet():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        pet_name = request.form["pet_name"]
        pet_type = request.form["pet_type"]
        age = request.form["age"]

        user_id = session["user_id"]

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO pets (user_id, pet_name, pet_type, age)
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(query, (user_id, pet_name, pet_type, age))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/pets")

    return render_template("add_pet.html")


# =========================
# VIEW PETS
# =========================
def view_pets():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM pets WHERE user_id = %s"
    cursor.execute(query, (user_id,))

    pets = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("pets.html", pets=pets)


# =========================
# DELETE PET
# =========================
def delete_pet(pet_id):

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor()

    # ensure user can only delete their own pets
    query = "DELETE FROM pets WHERE id = %s AND user_id = %s"
    cursor.execute(query, (pet_id, user_id))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/pets")