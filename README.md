# CareerTrack — Job & Internship Application Manager

CareerTrack is a responsive Flask web application that helps students and job seekers organise their job and internship applications in one place.

## Live Demo

**[Open CareerTrack Live Website](https://careertrack-job-application-manager.onrender.com)**

> The hosted service may take a little time to wake up after a period of inactivity.

## Features
- Dashboard showing total, active, interview and selected application counts.
- Add, edit and delete job or internship applications.
- Track Wishlist, Applied, Assessment, Interview, Selected and Rejected statuses.
- Search by company, role or location; filter by status and sort by date.
- View upcoming follow-up reminders.
- Export application records to CSV.
- Store records locally in SQLite; database is created automatically.
- Responsive desktop and mobile interface.

## Tech stack
Python, Flask, SQLite, HTML, CSS, JavaScript and Jinja templates.

## Project structure
```text
careertrack-job-application-manager/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   └── form.html
└── static/
    ├── app.js
    └── style.css
```

## Run locally
```bash
git clone https://github.com/kanchipatle/careertrack-job-application-manager.git
cd careertrack-job-application-manager
python -m venv .venv
```
Activate the environment on Windows:
```powershell
.venv\Scripts\activate
```
Install dependencies and run:
```bash
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000 in your browser.

For deployments, set a strong random `CAREERTRACK_SECRET_KEY` environment variable. `FLASK_DEBUG` defaults to `0`; only enable debug mode for local development. Never commit real secrets or `.env` files.

## Data and privacy
Application records are stored in a local SQLite file named `careertrack.db`. It is ignored by Git so personal company and application details are not uploaded.

## Manual test checklist
- [ ] Add an application with company, role and date.
- [ ] Edit its details and status.
- [ ] Add a future follow-up date and check reminders.
- [ ] Search, filter and change sort order.
- [ ] Export records with Export CSV.
- [ ] Delete a test record.

## Resume description
**CareerTrack — Job & Internship Application Manager** | Python, Flask, SQLite, HTML, CSS, JavaScript
- Developed a responsive web application to manage job and internship applications with create, update, delete, search and status filtering.
- Implemented SQLite persistence for company, role, work mode, stipend, status and follow-up details.
- Built dashboard metrics, upcoming follow-up reminders and CSV export.

## Scope
This is a personal portfolio project. It currently uses a local SQLite database and does not include user authentication, cloud database persistence, email notifications or AI-powered features.
