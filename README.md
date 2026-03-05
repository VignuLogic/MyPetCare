# PetCare Project

## Description
PetCare is a web application that helps pet owners manage their pets' health, grooming, and service bookings.

## Technologies Used
- Python Flask
- MySQL
- HTML / CSS / Bootstrap

## Database Tables
- users
- pets
- services
- bookings

## Features
- User Signup & Login
- Pet registration
- Service booking
- Grooming schedule
- Vaccination tracking

## Future Improvements
- Reminder notifications
- Pet health records
- Admin dashboard



# PetCare Project

## Project Structure

```
PetCare/
│
├── backend/
│   │
│   ├── app.py                # Main Flask backend
│   ├── db_config.py          # MySQL database connection
│   │
│   └── modules/              # Backend logic
│       ├── auth.py           # Login & Signup logic
│       ├── pets.py           # Pet management
│       ├── vaccination.py    # Vaccination tracker
│       ├── grooming.py       # Grooming scheduler
│       └── reminders.py      # Reminder system
│
├── frontend/
│   │
│   ├── css/
│   │   └── PC style.css
│   │
│   ├── images/
│   │   ├── LOGO-My PetCare.png
│   │   ├── All pets.png
│   │   ├── C1.jpeg
│   │   ├── C2.png
│   │   ├── C3.jpg
│   │   ├── C4.jpg
│   │   └── pets.png
│   │
│   └── templates/
│       │
│       ├── PetCare.html      # Home page
│       ├── Login.html        # Login page
│       ├── Signup.html       # Signup page
│       ├── MyAcc.html        # User dashboard
│       │
│       ├── Grooming.html
│       ├── Vaccination.html
│       ├── Care.html
│       ├── Health.html
│       └── AboutUs.html
│
├── database/
│   └── petcare.sql           # MySQL database schema
│
├── requirements.txt          # Python packages
└── README.md                 # Project documentation
```
