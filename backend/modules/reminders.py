from db_config import get_db_connection
from datetime import datetime, timedelta


# ──────────────────────────────────────────────
#  SERVICE NAME → ID  (safe lookup, no KeyError)
# ──────────────────────────────────────────────
def _get_service_map(cursor):
    """Return {lowercase_name: id} for every row in services table."""
    cursor.execute("SELECT id, service_name FROM services")
    return {row['service_name'].strip().lower(): row['id']
            for row in cursor.fetchall()}


# ──────────────────────────────────────────────
#  BUILD REMINDER LIST  (called by /reminders route)
# ──────────────────────────────────────────────
def get_reminders_for_user(user_id):
    """
    Returns a list of reminder dicts:
      {
        pet_name : str,
        message  : str,
        type     : 'overdue' | 'upcoming' | 'info',
        date     : date | None
      }
    """
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    reminders   = []
    today       = datetime.today().date()
    service_map = _get_service_map(cursor)

    # ── Fetch all pets for this user ──
    cursor.execute("SELECT * FROM pets WHERE user_id = %s", (user_id,))
    pets = cursor.fetchall()

    if not pets:
        cursor.close()
        conn.close()
        return []

    for pet in pets:
        pet_id   = pet['id']
        pet_name = pet['pet_name']

        # ─────────────────────────────
        #  VACCINATION reminders
        # ─────────────────────────────
        vac_id = service_map.get('vaccination')
        if vac_id:
            cursor.execute(
                """SELECT booking_date FROM bookings
                   WHERE pet_id = %s AND service_id = %s
                   ORDER BY booking_date DESC""",
                (pet_id, vac_id)
            )
            vac_rows = cursor.fetchall()

            if not vac_rows:
                reminders.append({
                    "pet_name": pet_name,
                    "message": "💉 No vaccination scheduled yet",
                    "type": "info",
                    "date": None
                })
            else:
                for row in vac_rows:
                    d = row['booking_date']
                    # booking_date might be a date or datetime object
                    if isinstance(d, datetime):
                        d = d.date()

                    if d < today:
                        reminders.append({
                            "pet_name": pet_name,
                            "message": f"❗ Vaccination was missed on {d.strftime('%d %b %Y')}",
                            "type": "overdue",
                            "date": d
                        })
                    elif d <= today + timedelta(days=3):
                        reminders.append({
                            "pet_name": pet_name,
                            "message": f"💉 Vaccination due on {d.strftime('%d %b %Y')} — coming soon!",
                            "type": "upcoming",
                            "date": d
                        })
                    elif d <= today + timedelta(days=7):
                        reminders.append({
                            "pet_name": pet_name,
                            "message": f"💉 Vaccination scheduled for {d.strftime('%d %b %Y')}",
                            "type": "info",
                            "date": d
                        })

        # ─────────────────────────────
        #  GROOMING reminders
        # ─────────────────────────────
        grm_id = service_map.get('grooming')
        if grm_id:
            cursor.execute(
                """SELECT booking_date FROM bookings
                   WHERE pet_id = %s AND service_id = %s
                   ORDER BY booking_date DESC
                   LIMIT 1""",
                (pet_id, grm_id)
            )
            last_groom = cursor.fetchone()

            if not last_groom:
                reminders.append({
                    "pet_name": pet_name,
                    "message": "✂️ Grooming not booked yet — schedule one soon!",
                    "type": "info",
                    "date": None
                })
            else:
                d = last_groom['booking_date']
                if isinstance(d, datetime):
                    d = d.date()

                days_since = (today - d).days
                if days_since > 30:
                    reminders.append({
                        "pet_name": pet_name,
                        "message": f"✂️ Last grooming was {days_since} days ago — overdue!",
                        "type": "overdue",
                        "date": d
                    })
                elif days_since > 21:
                    reminders.append({
                        "pet_name": pet_name,
                        "message": f"✂️ Grooming due soon (last was {days_since} days ago)",
                        "type": "upcoming",
                        "date": d
                    })

        # ─────────────────────────────
        #  BOOKING reminders (upcoming appointments)
        # ─────────────────────────────
        cursor.execute(
            """SELECT b.booking_date, s.service_name
               FROM bookings b
               JOIN services s ON b.service_id = s.id
               WHERE b.pet_id = %s
                 AND b.booking_date >= %s
                 AND b.booking_date <= %s
               ORDER BY b.booking_date ASC""",
            (pet_id, today, today + timedelta(days=7))
        )
        upcoming = cursor.fetchall()
        for appt in upcoming:
            d = appt['booking_date']
            if isinstance(d, datetime):
                d = d.date()
            svc = appt['service_name']
            if d == today:
                reminders.append({
                    "pet_name": pet_name,
                    "message": f"📅 {svc} appointment is TODAY!",
                    "type": "upcoming",
                    "date": d
                })
            else:
                days_left = (d - today).days
                reminders.append({
                    "pet_name": pet_name,
                    "message": f"📅 {svc} in {days_left} day{'s' if days_left > 1 else ''} ({d.strftime('%d %b')})",
                    "type": "info",
                    "date": d
                })

    cursor.close()
    conn.close()

    # Sort: overdue first, then upcoming, then info
    order = {'overdue': 0, 'upcoming': 1, 'info': 2}
    reminders.sort(key=lambda r: order.get(r['type'], 3))

    return reminders


# ──────────────────────────────────────────────
#  AUTO REMINDER  (called by APScheduler every hour)
#  Logs to console — replace with email/push later
# ──────────────────────────────────────────────
def auto_reminder_job():
    """
    Scans ALL users and prints reminders to console.
    Replace print() with email/SMS sending later.
    """
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, first_name FROM users")
        users = cursor.fetchall()

        cursor.close()
        conn.close()

        for user in users:
            reminders = get_reminders_for_user(user['id'])
            for r in reminders:
                if r['type'] in ('overdue', 'upcoming'):
                    print(
                         f"[REMINDER] User: {user['first_name']} | "
                         f"Pet: {r['pet_name']} | {r['message']}"
                    )

    except Exception as e:
        print(f"[REMINDER ERROR] auto_reminder_job failed: {e}")