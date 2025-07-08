# 🔗 Link-in-Bio Fullstack App

A full-featured **Link-in-Bio** platform powered by:

- ⚡ FastAPI (Python backend)
- 🖥️ For the full-stack version, check out [Frontend – Next.js]: [linkin-bio-nextjs](https://github.com/amritkarma/linkin-bio-nextjs)

Built for creators, influencers, and anyone who wants to manage a single profile with multiple social or promotional links.

---

## ✨ Features

### 🔐 Authentication
- User registration and login with **JWT**
- Secure password hashing
- Token-based auth (Bearer)
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
| **Auth**    | JWT, OAuth2 Password Flow |
| **Database**| SQLite (default), PostgreSQL (recommended) |
| **Media**   | File uploads via FastAPI |
| **Rate-Limiting** | SlowAPI middleware |

---

## 🚀 Getting Started

### 📦 Backend (FastAPI)

1. **Clone the repo**

```bash
git clone https://github.com/amritkarma/linkin-bio-fastapi.git
cd your-backend-repo
```
## Create a virtual environment & install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
## Create a .env file
```bash
DEBUG=true
PORT=8000

SECRET_KEY=yoursecretkey

# For PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password

# For CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Run the development server
```bash
uvicorn main:app --reload
```

### App will be available at: http://localhost:8000




# 🖥️ Frontend
### 👉 Frontend GitHub Repository (Next.js) [linkin-bio-nextjs](https://github.com/amritkarma/linkin-bio-nextjs)

### Make sure your .env backend CORS config includes your frontend domain:

```bash
CORS_ORIGINS=http://localhost:3000
```
### The frontend will interact with this backend using token-based API authentication.

# 🧰 API Endpoints

## 🟢 Auth

| Method | Endpoint   | Description           | Rate Limit |
|--------|------------|-----------------------|------------|
| POST   | /register  | Register a new user   | 5 req/min  |
| POST   | /login     | Authenticate user     | 10 req/min |

## 🔐 User

| Method | Endpoint           | Description                   | Auth |
|--------|--------------------|-------------------------------|------|
| GET    | /me                | Get authenticated user info   | ✅    |
| PATCH  | /me                | Update profile & avatar       | ✅    |
| GET    | /users/{username}  | Public profile                | ❌    |

## 🔗 Links

| Method | Endpoint                       | Description                   | Auth |
|--------|--------------------------------|-------------------------------|------|
| GET    | /users/{username}/links        | Public links for user         | ❌    |
| GET    | /links                         | List authenticated user's links | ✅  |
| POST   | /links                         | Create a new link             | ✅    |
| GET    | /links/{id}                    | Get a single link             | ✅    |
| PUT    | /links/{id}                    | Update a link                 | ✅    |
| DELETE | /links/{id}                    | Delete a link                 | ✅    |


# 🔒 Authentication & Rate Limiting

## 🔐 Authentication

All authenticated routes require a **Bearer token** in the `Authorization` header.

## ⚠️ Rate Limiting (Backend)

Rate limiting is implemented using **SlowAPI**. If the limit is exceeded, the API returns:




| Endpoint   | Limit            |
|------------|------------------|
| /register  | 5 requests/min   |
| /login     | 10 requests/min  |

---

# 🧾 Example Request (Using cURL)

### 📥 Register

```bash
curl -X POST http://localhost:8000/register \
-H "Content-Type: application/json" \
-d '{"username": "johndoe", "password": "secret"}'
```

### Login

```bash
curl -X POST http://localhost:8000/login \
-H "Content-Type: application/json" \
-d '{"username": "johndoe", "password": "secret"}'
```
## Response
```bash
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer"
}
```

### Use this token for all authenticated requests:
```bash
Authorization: Bearer <your_token>
```


---

## 📄 License

Licensed under the [MIT License](https://github.com/amritkarma/linkin-bio-fastapi/blob/main/LICENSE.txt).  
You are free to use, modify, and distribute this project for personal or commercial purposes.

---

## 👨‍💻 Author

Crafted with care by [Amrit Vishwakarma](https://github.com/amritkarma) 🛠️  
For the full-stack version, check out: [linkin-bio-fullstack](https://github.com/amritkarma/linkin-bio-fastapi)


## 🤝 Contributions

Pull requests and feature suggestions are welcome!  
Please open an issue to discuss any major changes beforehand.



