# Ismail Sheriff — Portfolio

A responsive portfolio with a Python FastAPI content and assistant backend, a React/Vite browser interface, and a Three.js hero scene. Python owns the portfolio profile, projects, skills, education, contact data, and chatbot routing. HTML, CSS, and browser JavaScript render the site and its interactive visual effects.

## Run locally

Requires Python 3.10+, Node.js 20.19+ or 22.12+, and the packages in `requirements.txt`.

```sh
npm install
python -m pip install -r requirements.txt
npm run dev
```

The Python launcher starts FastAPI and Vite together. It selects free local ports so it can run alongside other projects; the exact preview and API URLs are printed at startup. The contact form saves submissions to `data/contact_inquiries.sqlite3` using Python's built-in SQLite support. The database is local and is never returned by a public API route. Create a production build with `npm run build`; FastAPI can serve the built `dist/` site and its API with `python -m uvicorn backend:app --host 127.0.0.1 --port 8000`.

### Admin inquiry dashboard

The local demo login is shown on the Admin sign-in screen: username `ISMAIL`, password `ISMAILSHERIFF16`. Admin access is restricted to localhost because these demo credentials are displayed openly. The password is stored as a salted scrypt hash in the local SQLite database. Sessions expire after 12 hours, and inquiry records are available only to an authenticated local admin. To set a different username and password, run `python setup_admin.py` from the project folder; this also signs out existing sessions.

Export saved inquiries to a CSV file when needed:

```sh
python export_inquiries.py
```

The default output is `contact-inquiries.csv`, which is excluded from version control. Choose a different private output path with `python export_inquiries.py path/to/inquiries.csv`.

## Free deployment

Deploy the Python app with its built `dist/` folder and install `requirements.txt`. FastAPI serves the site assets and `/api` endpoints from the same origin. A static-only host will need a separate Python API service and a matching API URL configuration.

## Updating content

Edit `PORTFOLIO` and `SECTION_KEYWORDS` in `backend.py` to update profile data, projects, skills, education, contact details, and chatbot routes. Replace `public/portrait.png` to update the transparent portrait and `public/resume.pdf` to update the resume. The assistant and contact form run through Python and do not send visitor messages to an external service. Contact inquiries are stored locally; do not commit the database or exported CSV because they contain personal contact information. Project repository and implementation fields are intentionally left unconfirmed until matching evidence is available.
