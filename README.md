# 🔗 Link-in-Bio Fullstack App

A full-featured **Link-in-Bio** platform powered by:

- ⚡ FastAPI (Python backend)
- 🖥️ For the full-stack version, check out [Frontend – Next.js](https://github.com/amritkarma/linkin-bio-nextjs)

Built for creators, influencers, and anyone who wants to manage a single profile with multiple social or promotional links.

---

## ✨ Features

### 🔐 Authentication
- User registration and login with **JWT**
- Secure password hashing
- Access + Refresh token flow (Bearer)
- Token refresh endpoint
- Auto-expiring access tokens
- **Rate-limited endpoints** to prevent abuse

### 👤 User Profiles
- Public user profile (`/{username}`)
- Editable bio and avatar (PNG/JPEG only)
- Authenticated "Me" endpoint to update personal info

### 🔗 Links Management
- Create, update, delete personal links
- View public links by username
- Authenticated view of personal links

---

## 🧪 Tech Stack

| Layer       | Tech                      |
|-------------|---------------------------|
| **Frontend**| [Next.js](https://nextjs.org/), Tailwind CSS |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/), SQLAlchemy |
| **Auth**    | JWT (access + refresh), OAuth2 |
| **Database**| SQLite (default), PostgreSQL (via Supabase) |
| **Media**   | File uploads via FastAPI |
| **Rate-Limiting** | SlowAPI middleware |

---

## 🚀 Getting Started

### 📦 Backend (FastAPI)

#### 1. Clone the repo

```bash
git clone https://github.com/amritkarma/linkin-bio-fastapi.git
cd linkin-bio-fastapi
```

#### 2. Create a virtual environment & install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Create a `.env` file

```ini
DEBUG=true
PORT=8000
SECRET_KEY=your_secret_key

# PostgreSQL / Supabase connection
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password

# CORS config
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### 4. Run the dev server

```bash
uvicorn main:app --reload
```

App will be live at: [http://localhost:8000](http://localhost:8000)

---

## 🔧 Database Setup with Alembic

#### 5. Create the First Migration

```bash
alembic revision --autogenerate -m "Initial tables"
```

Check the generated migration file under `alembic/versions/` to confirm table structure.

#### 6. Apply the Migration

```bash
alembic upgrade head
```

✅ This will create all necessary tables in your Supabase PostgreSQL database.

---

## 🖥️ Frontend

GitHub Repository → [linkin-bio-nextjs](https://github.com/amritkarma/linkin-bio-nextjs)

Ensure backend CORS settings allow your frontend domain:

```bash
CORS_ORIGINS=http://localhost:3000
```

---

## 🔐 Token-based Authentication

- Access tokens expire after 15 minutes.
- Refresh tokens valid for 7 days.
- Frontend auto-refreshes access tokens every 10 minutes via `/refresh`.

### Refresh Endpoint (Backend)

```http
POST /refresh
Content-Type: multipart/form-data
Body: refresh_token=<your_token>
```

Returns new access and refresh tokens.

---

## 🧰 API Endpoints

### 🟢 Auth

| Method | Endpoint   | Description           | Rate Limit |
|--------|------------|-----------------------|------------|
| POST   | /register  | Register a new user   | 5 req/min  |
| POST   | /login     | Authenticate user     | 10 req/min |
| POST   | /refresh   | Refresh JWT tokens    | ✅ Secure  |

### 🔐 User

| Method | Endpoint           | Description                   | Auth |
|--------|--------------------|-------------------------------|------|
| GET    | /me                | Get authenticated user info   | ✅    |
| PATCH  | /me                | Update profile & avatar       | ✅    |
| GET    | /users/{username}  | Public profile                | ❌    |

### 🔗 Links

| Method | Endpoint                       | Description                   | Auth |
|--------|--------------------------------|-------------------------------|------|
| GET    | /users/{username}/links        | Public links for user         | ❌    |
| GET    | /links                         | List authenticated user's links | ✅  |
| POST   | /links                         | Create a new link             | ✅    |
| GET    | /links/{id}                    | Get a single link             | ✅    |
| PUT    | /links/{id}                    | Update a link                 | ✅    |
| DELETE | /links/{id}                    | Delete a link                 | ✅    |

---

## 🧾 Example cURL Requests

### Register

```bash
curl -X POST http://localhost:8000/register -H "Content-Type: application/json" -d '{"username": "johndoe", "password": "secret"}'
```

### Login

```bash
curl -X POST http://localhost:8000/login -H "Content-Type: application/json" -d '{"username": "johndoe", "password": "secret"}'
```

**Response:**

```json
{
  "access_token": "<JWT_TOKEN>",
  "refresh_token": "<REFRESH_TOKEN>",
  "token_type": "bearer"
}
```

Use this token for authenticated requests:

```bash
Authorization: Bearer <access_token>
```

---

## 🔒 Rate Limiting

Rate limiting is enabled using **SlowAPI**.

| Endpoint   | Limit            |
|------------|------------------|
| /register  | 5 requests/min   |
| /login     | 10 requests/min  |

---

## 📄 License

Licensed under the [MIT License](https://github.com/amritkarma/linkin-bio-fastapi/blob/main/LICENSE.txt).  
You are free to use, modify, and distribute this project for personal or commercial purposes.

---

## 👨‍💻 Author

Crafted with care by [Your Name](https://github.com/amritkarma) 🛠️  
Frontend: [linkin-bio-nextjs](https://github.com/amritkarma/linkin-bio-nextjs)  
Backend: [linkin-bio-fastapi](https://github.com/amritkarma/linkin-bio-fastapi)

---

## 🤝 Contributions

Pull requests and feature suggestions are welcome!  
Open an issue to discuss any improvements or bugs.
