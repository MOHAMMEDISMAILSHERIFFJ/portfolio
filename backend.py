"""Python data and local API for the Ismail Sheriff portfolio."""

from __future__ import annotations

import os
import re
import sqlite3
import hashlib
import hmac
import ipaddress
import secrets
from datetime import datetime, timedelta, timezone
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from pydantic import BaseModel, Field, field_validator
from pathlib import Path

app = FastAPI(title="Ismail Sheriff Portfolio API", version="1.0.0")
ROOT = Path(__file__).resolve().parent
DATABASE_PATH = Path(os.environ.get("PORTFOLIO_DB_PATH", ROOT / "data" / "contact_inquiries.sqlite3"))


def initialize_contact_database() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS contact_inquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS admin_credentials (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                username TEXT NOT NULL UNIQUE,
                salt BLOB NOT NULL,
                password_hash BLOB NOT NULL
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS admin_sessions (
                token_hash TEXT PRIMARY KEY,
                expires_at TEXT NOT NULL
            )
        """)
        connection.commit()


initialize_contact_database()

PORTFOLIO = {
    "navigation": [
        {"id": "about", "label": "About"},
        {"id": "projects", "label": "Projects"},
        {"id": "skills", "label": "Skills"},
        {"id": "experience", "label": "Experience"},
        {"id": "achievements", "label": "Achievements"},
        {"id": "contact", "label": "Contact"},
    ],
    "assistant_intro": "Hey! Ask me about Ismail’s projects, skills, education or experience. I’ll point you to the right place.",
    "assistant_suggestions": [
        {"label": "Skills", "question": "Tell me about your skills"},
        {"label": "Projects", "question": "Show me your projects"},
        {"label": "Contact", "question": "How can I contact you?"},
    ],
    "short_name": "ISMAIL SHERIFF",
    "full_name": "Mohammed Ismail Sheriff J.",
    "role": "Aspiring AI / ML Engineer",
    "year_line": "SECOND-YEAR ENGINEERING STUDENT",
    "location": "Salem, India",
    "location_detail": "Salem, Tamil Nadu",
    "graduation": "2029",
    "cgpa": "9.35",
    "university": "Jain University",
    "degree": "B.Tech · Computer Science & Engineering (AI / ML)",
    "about": [
        "I’m Mohammed Ismail Sheriff J, a second-year Computer Science and Engineering student specializing in AI & Machine Learning at Jain University.",
        "I’m interested in how intelligent systems can solve practical problems. I’m building my foundations through coursework, hands-on projects, and an industry internship.",
    ],
    "projects_intro": "Four projects across emergency response, student wellness, nutrition, and Java fundamentals.",
    "projects": [
        {
            "id": "01",
            "title": "Ambulance to Hospital",
            "type": "EMERGENCY RESPONSE · CAUSAL-FLOW",
            "note": "A traffic-intelligence and emergency-response application with an ambulance corridor workflow.",
            "problem": "Ambulances can lose valuable time reaching a suitable hospital.",
            "solution": "The repository documents an emergency corridor for Ambulance 07 from J-A to J-D and incident coordination through a six-stage response lifecycle.",
            "contribution": "The repository documents the implementation; the individual/team contribution split is not specified in its README.",
            "technologies": "React 19, Vite 8, TypeScript, FastAPI, SQLite, SQLAlchemy, WebSockets",
            "status": "README documents deterministic mock mode by default and a FastAPI backend.",
            "repository": "https://github.com/MOHAMMEDISMAILSHERIFFJ/casual_engine",
            "demo": None,
            "tags": ["Healthcare", "Mobility"],
            "symbol": "✳",
        },
        {
            "id": "02",
            "title": "Malnutrition Detection",
            "type": "NUTRITION & HEALTH · NUTRIGUARD",
            "note": "A public repository called NutriGuard describes a multilingual nutrition and health-monitoring platform. This is the closest repository match found for this project.",
            "problem": "The project focuses on identifying possible signs of malnutrition.",
            "solution": "The README lists nutrition plans, health analysis, growth trends, and AI image-scan screens; it does not document clinical validation or confirm which modules are fully operational.",
            "contribution": "The repository does not specify your individual contribution or team split.",
            "technologies": "React 18, Vite 5, Recharts",
            "status": "A live demo is linked in the README; user data is described as browser-local.",
            "repository": "https://github.com/MOHAMMEDISMAILSHERIFFJ/fuel_the_future",
            "demo": "https://fuelthefuture-lake.vercel.app/",
            "tags": ["AI / ML", "Health"],
            "symbol": "◉",
        },
        {
            "id": "03",
            "title": "Student Depression Calculator",
            "type": "STUDENT WELLNESS CONCEPT",
            "note": "An in-progress concept exploring movement, physical-health indicators, mental-wellness signals, and phone-use patterns to help identify students who may need support. It is not a clinical diagnosis.",
            "problem": "The concept explores patterns that may indicate a student needs support.",
            "solution": "A student-wellness concept considering movement, physical health, mental wellness, and phone-use patterns. It is not a clinical diagnosis.",
            "contribution": "Project-specific implementation details have not yet been confirmed.",
            "technologies": "Not yet confirmed",
            "status": "Concept in progress",
            "repository": None,
            "demo": None,
            "tags": ["Wellness", "Movement", "Phone use"],
            "symbol": "✧",
        },
        {
            "id": "04",
            "title": "Student Management System",
            "type": "ACADEMIC PROJECT · JAVA",
            "note": "A Java mini project that stores and displays student information using classes and functions.",
            "problem": "Student information needs a clear structure for entry and display.",
            "solution": "The resume describes a Java program that stores and displays student information through classes and functions.",
            "contribution": "Developed as an academic mini project.",
            "technologies": "Java, classes, functions",
            "status": "Academic project described in resume",
            "repository": None,
            "demo": None,
            "tags": ["Java", "Academic project"],
            "symbol": "▤",
        },
    ],
    "skills": [
        {"label": "LANGUAGES", "items": ["Python", "Java", "MySQL"]},
        {"label": "FRAMEWORKS", "items": ["FastAPI"]},
        {"label": "IN PROGRESS", "items": ["Data Structures & Algorithms · Java"]},
    ],
    "internship": {
        "organization": "Lumbini Technologies",
        "website": "https://www.lumbinitechnologies.com/",
        "title": "Industry Internship",
        "description": "Currently contributing to a project intended for the film industry. The specific assignment and responsibilities have not been confirmed for publication yet.",
    },
    "achievement": {
        "title": "HackNova Winner",
        "label": "HACKATHON WINNER",
        "year": "2026",
        "details": "HackNova · KIOT College, Salem · 2026",
    },
    "contact": {
        "email": "ismailsheriff1612@gmail.com",
        "phone": "+919363510655",
        "github": "https://github.com/MOHAMMEDISMAILSHERIFFJ",
        "linkedin": "https://www.linkedin.com/in/mohammed-ismail-sheriff-5033b1363/",
    },
}

SECTION_KEYWORDS = {
    "projects": ("project", "ambulance", "malnutrition", "depression", "student", "student management", "wellness", "mental health", "phone use", "movement", "work", "build"),
    "skills": ("skill", "python", "java", "mysql", "fastapi", "learn", "language", "technology"),
    "about": ("about", "who", "education", "cgpa", "college", "study", "university", "degree", "year", "graduat"),
    "experience": ("experience", "intern", "lumbini", "company"),
    "achievement": ("hackathon", "hackfusion", "hacknova", "achievement", "award", "won", "winner", "winning"),
    "contact": ("contact", "email", "phone", "github", "linkedin", "resume"),
}


class AssistantQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class AdminLogin(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


def hash_admin_password(password: str, salt: bytes) -> bytes:
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=64)


def is_local_admin_request(request: Request) -> bool:
    host = request.client.host if request.client else ""
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def admin_session(request: Request) -> bool:
    if not is_local_admin_request(request):
        return False
    token = request.cookies.get("portfolio_admin_session")
    if not token:
        return False
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with sqlite3.connect(DATABASE_PATH, timeout=5) as connection:
        row = connection.execute(
            "SELECT expires_at FROM admin_sessions WHERE token_hash = ?", (token_hash,)
        ).fetchone()
    if not row:
        return False
    try:
        if datetime.fromisoformat(row[0]) <= datetime.now(timezone.utc):
            with sqlite3.connect(DATABASE_PATH, timeout=5) as connection:
                connection.execute("DELETE FROM admin_sessions WHERE token_hash = ?", (token_hash,))
                connection.commit()
            return False
    except ValueError:
        return False
    return True


def require_admin(request: Request) -> None:
    if not admin_session(request):
        raise HTTPException(status_code=401, detail="Please sign in to view inquiries.")


class ContactInquiry(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=6, max_length=254)
    phone: str | None = Field(default=None, max_length=32)
    company: str = Field(min_length=2, max_length=120)
    role: str = Field(min_length=2, max_length=120)
    message: str = Field(min_length=5, max_length=2000)
    consent: bool
    website: str = Field(default="", max_length=200)

    @field_validator("name", "company", "role", "message", mode="before")
    @classmethod
    def trim_required_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("Enter a valid email address.")
        return value

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value and not re.fullmatch(r"[+()\d.\-\s]{7,32}", value):
            raise ValueError("Enter a valid phone number or leave it blank.")
        return value

    @field_validator("consent")
    @classmethod
    def require_contact_consent(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Consent is required to send this inquiry.")
        return value


@app.get("/api/portfolio")
def get_portfolio() -> dict:
    """Return the portfolio copy and sections used by the browser UI."""
    return PORTFOLIO


@app.get("/api/admin/session")
def get_admin_session(request: Request) -> dict[str, bool]:
    with sqlite3.connect(DATABASE_PATH, timeout=5) as connection:
        configured = connection.execute("SELECT 1 FROM admin_credentials WHERE id = 1").fetchone() is not None
    return {"authenticated": admin_session(request), "configured": configured}


@app.post("/api/admin/login")
def login_admin(payload: AdminLogin, request: Request, response: Response) -> dict[str, str | bool]:
    if not is_local_admin_request(request):
        raise HTTPException(status_code=403, detail="Admin sign-in is available only from this computer.")
    with sqlite3.connect(DATABASE_PATH, timeout=5) as connection:
        row = connection.execute(
            "SELECT username, salt, password_hash FROM admin_credentials WHERE id = 1"
        ).fetchone()

    salt = row[1] if row else b"portfolio-admin-dummy-salt"
    candidate = hash_admin_password(payload.password, salt)
    valid = bool(
        row
        and hmac.compare_digest(payload.username.strip().casefold(), row[0].casefold())
        and hmac.compare_digest(candidate, row[2])
    )
    if not valid:
        raise HTTPException(status_code=401, detail="Username or password is incorrect.")

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=12)).isoformat(timespec="seconds")
    with sqlite3.connect(DATABASE_PATH, timeout=5) as connection:
        connection.execute("DELETE FROM admin_sessions WHERE expires_at <= ?", (datetime.now(timezone.utc).isoformat(timespec="seconds"),))
        connection.execute("INSERT INTO admin_sessions (token_hash, expires_at) VALUES (?, ?)", (token_hash, expires_at))
        connection.commit()
    response.set_cookie(
        key="portfolio_admin_session",
        value=token,
        max_age=12 * 60 * 60,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="strict",
        path="/api/admin",
    )
    return {"ok": True, "username": row[0]}


@app.post("/api/admin/setup")
def setup_admin(payload: AdminLogin, request: Request, response: Response) -> dict[str, str | bool]:
    if not is_local_admin_request(request):
        raise HTTPException(status_code=403, detail="Admin setup is available only from this computer.")
    username = payload.username.strip()
    if not username:
        raise HTTPException(status_code=422, detail="Choose a username.")
    if len(payload.password) < 12:
        raise HTTPException(status_code=422, detail="Use a password with at least 12 characters.")

    salt = secrets.token_bytes(16)
    password_hash = hash_admin_password(payload.password, salt)
    with sqlite3.connect(DATABASE_PATH, timeout=5) as connection:
        connection.execute("BEGIN IMMEDIATE")
        existing = connection.execute("SELECT 1 FROM admin_credentials WHERE id = 1").fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="An admin account already exists. Sign in instead.")
        connection.execute(
            "INSERT INTO admin_credentials (id, username, salt, password_hash) VALUES (1, ?, ?, ?)",
            (username, salt, password_hash),
        )
        connection.commit()
    return login_admin(AdminLogin(username=username, password=payload.password), request, response)


@app.post("/api/admin/logout")
def logout_admin(request: Request, response: Response) -> dict[str, bool]:
    token = request.cookies.get("portfolio_admin_session")
    if token:
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        with sqlite3.connect(DATABASE_PATH, timeout=5) as connection:
            connection.execute("DELETE FROM admin_sessions WHERE token_hash = ?", (token_hash,))
            connection.commit()
    response.delete_cookie("portfolio_admin_session", path="/api/admin", httponly=True, samesite="strict")
    return {"ok": True}


@app.get("/api/admin/inquiries")
def get_admin_inquiries(_: None = Depends(require_admin)) -> list[dict[str, str | int | None]]:
    with sqlite3.connect(DATABASE_PATH, timeout=5) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """SELECT id, created_at, name, email, phone, company, role, message
               FROM contact_inquiries ORDER BY id DESC"""
        ).fetchall()
    return [dict(row) for row in rows]


@app.post("/api/assistant")
def answer_question(payload: AssistantQuestion) -> dict[str, str | None]:
    """Return a local portfolio answer and optional section destination."""
    question = payload.question.strip().lower()
    if not question:
        return {"text": "Ask me something about Ismail’s portfolio.", "target": None}

    def has(*terms: str) -> bool:
        return any(term in question for term in terms)

    if has("hackathon", "hackfusion", "hacknova", "achievement", "award", "won", "winner", "winning"):
        award = PORTFOLIO["achievement"]
        return {"text": f"Ismail won HackNova in {award['year']} at KIOT College in Salem.", "target": "achievement"}
    if has("email", "phone", "contact", "linkedin", "github", "resume"):
        return {"text": f"You can contact Ismail at {PORTFOLIO['contact']['email']}, or use the links in the Contact section.", "target": "contact"}
    if has("intern", "lumbini", "experience", "company"):
        internship = PORTFOLIO["internship"]
        return {"text": f"Ismail is currently completing an industry internship at {internship['organization']}. He has described contributing to a film-industry project; further role and project details are not confirmed yet.", "target": "experience"}
    if has("cgpa", "grade", "academic", "university", "college", "education", "degree", "year", "graduat", "study"):
        return {"text": f"Ismail is a second-year {PORTFOLIO['degree']} student at {PORTFOLIO['university']}. His confirmed CGPA is {PORTFOLIO['cgpa']}, and he expects to graduate in {PORTFOLIO['graduation']}.", "target": "about"}
    if has("skill", "python", "java", "mysql", "fastapi", "learn", "language", "technology", "stack"):
        return {"text": "His listed skills are Python, Java, MySQL, and FastAPI. He is currently learning Data Structures and Algorithms in Java.", "target": "skills"}
    if has("student management", "management system"):
        project = PORTFOLIO["projects"][3]
        return {"text": f"{project['note']} The resume lists Java, classes, and functions as the project foundation.", "target": "projects"}
    if has("ambulance", "emergency response", "causal-flow"):
        project = PORTFOLIO["projects"][0]
        return {"text": f"{project['note']} The README describes Ambulance 07 on corridor J-A to J-D, a six-stage incident workflow, and a stack of {project['technologies']}. It documents mock mode by default and a FastAPI backend.", "target": "projects"}
    if has("malnutrition", "nutrition", "nutriguard"):
        project = PORTFOLIO["projects"][1]
        return {"text": f"{project['note']} Its README lists nutrition plans, health analysis, growth trends, and AI image-scan screens, using {project['technologies']}. It does not establish clinical validation or Ismail’s individual contribution split.", "target": "projects"}
    if has("depression", "student wellness", "mental health", "phone use", "movement"):
        project = PORTFOLIO["projects"][2]
        return {"text": f"{project['note']} The specific implementation and technology details have not been confirmed.", "target": "projects"}
    if has("project", "wellness", "build"):
        return {"text": "Ismail’s portfolio includes projects in ambulance response, nutrition and health monitoring, student wellness, and a Java Student Management System. Each case study marks details that still need confirmation.", "target": "projects"}

    target = next((section for section, terms in SECTION_KEYWORDS.items() if any(term in question for term in terms)), None)
    if target:
        return {"text": f"I can help with {target}: ask about Ismail’s education, skills, projects, internship, achievement, or contact details.", "target": target}
    return {"text": "I can answer questions about Ismail’s education, skills, projects, internship, hackathon achievement, and contact details. What would you like to know?", "target": None}


@app.post("/api/contact", status_code=201)
def save_contact_inquiry(payload: ContactInquiry) -> dict[str, str | bool]:
    """Store an opportunity inquiry locally; the honeypot silently drops bots."""
    if payload.website:
        return {"ok": True, "message": "Thanks — your inquiry has been received."}

    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        with sqlite3.connect(DATABASE_PATH, timeout=5) as connection:
            connection.execute(
                """INSERT INTO contact_inquiries
                   (created_at, name, email, phone, company, role, message)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (created_at, payload.name, payload.email, payload.phone, payload.company,
                 payload.role, payload.message),
            )
            connection.commit()
    except sqlite3.Error as error:
        raise HTTPException(status_code=503, detail="The inquiry could not be saved just now. Please try again later.") from error
    return {"ok": True, "message": "Thanks — your inquiry has been saved for Ismail to review."}


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


DIST = ROOT / "dist"
if DIST.is_dir():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="portfolio-site")
