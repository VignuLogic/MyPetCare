from flask import request, render_template, redirect, session
from db_config import get_db_connection


# =========================
# GROOMING TIPS BY PET TYPE
# =========================
GROOMING_TIPS = {
    "dog": [
        "Brush your dog's coat at least 2-3 times a week to avoid tangles.",
        "Trim nails every 3-4 weeks — long nails can cause pain while walking.",
        "Clean ears weekly to prevent infections.",
        "Bathe your dog once every 4-6 weeks with a pet-safe shampoo.",
        "Brush teeth 2-3 times a week to prevent dental disease."
    ],
    "cat": [
        "Brush short-haired cats once a week, long-haired cats daily.",
        "Never bathe a cat unless necessary — they self-clean.",
        "Trim nails every 2-3 weeks to avoid scratching.",
        "Check ears weekly for wax buildup or redness.",
        "Dental chews or brushing helps prevent gum disease."
    ],
    "rabbit": [
        "Brush rabbits gently 2-3 times a week, daily during shedding season.",
        "Never bathe a rabbit — it causes extreme stress.",
        "Trim nails every 4-6 weeks.",
        "Check teeth regularly — overgrown teeth are common in rabbits.",
        "Clean the area around the tail weekly."
    ],
    "bird": [
        "Allow birds to bathe themselves in a shallow dish of water.",
        "Trim wing feathers every 6-8 weeks if needed.",
        "Check beak and nails monthly — trim if overgrown.",
        "Keep the cage clean to avoid feather and skin issues."
    ],
    "fish": [
        "Clean the tank every 1-2 weeks — partial water change of 25%.",
        "Check water pH, ammonia, and nitrate levels weekly.",
        "Remove uneaten food daily to keep water clean.",
        "Clean the filter monthly without replacing all media at once."
    ]
}

def get_tips_for_pet(pet_type):
    """Return tips based on pet type. Defaults to dog tips if type not found."""
    key = pet_type.strip().lower()
    return GROOMING_TIPS.get(key, GROOMING_TIPS["dog"])


# =========================
# SCHEDULE GROOMING
# =========================
def add_grooming():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pets WHERE user_id = %s", (user_id,))
    pets = cursor.fetchall()
    cursor.close()
    conn.close()

    if request.method == "POST":

        pet_id        = request.form.get("pet_id")
        grooming_date = request.form.get("grooming_date")
        grooming_type = request.form.get("grooming_type", "")
        notes         = request.form.get("notes", "")

        conn   = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO grooming (pet_id, user_id, grooming_date, grooming_type, notes)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(query, (pet_id, user_id, grooming_date, grooming_type, notes))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/grooming")

    return render_template("grooming.html", pets=pets)


# =========================
# VIEW GROOMING HISTORY + TIPS
# =========================
def view_grooming():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get grooming history with pet name
    query = """
    SELECT g.*, p.pet_name, p.pet_type
    FROM grooming g
    JOIN pets p ON g.pet_id = p.id
    WHERE g.user_id = %s
    ORDER BY g.grooming_date DESC
    """
    cursor.execute(query, (user_id,))
    history = cursor.fetchall()

    # Get user's pets for the form dropdown
    cursor.execute("SELECT * FROM pets WHERE user_id = %s", (user_id,))
    pets = cursor.fetchall()

    cursor.close()
    conn.close()

    # Build tips for each unique pet type the user has
    tips_by_pet = {}
    for pet in pets:
        pet_type = pet["pet_type"].strip().lower()
        if pet_type not in tips_by_pet:
            tips_by_pet[pet_type] = get_tips_for_pet(pet_type)

    return render_template(
        "grooming.html",
        history=history,
        pets=pets,
        tips_by_pet=tips_by_pet,
        user_name=session.get("user_name")
    )


# =========================
# DELETE GROOMING RECORD
# =========================
def delete_grooming(grooming_id):

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn   = get_db_connection()
    cursor = conn.cursor()

    query = "DELETE FROM grooming WHERE id = %s AND user_id = %s"
    cursor.execute(query, (grooming_id, user_id))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/grooming")