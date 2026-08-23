# 🤖 Notes Generator AI

An AI-powered document processing and notes generation application built with **FastAPI, React, Python, MySQL, SQLAlchemy, Redis, JWT Authentication, Google OAuth, and LLM-based AI processing**.

The application allows users to securely register and log in, upload documents, extract document content, and generate AI-powered notes from their documents.

## 🌐 Repository

**GitHub:** [notes-generator-AI](https://github.com/duttasagar/notes-generator-AI)

---

## 📸 Screenshots

### 🔐 Login

<img width="1915" height="910" alt="Screenshot 2026-08-23 205510" src="https://github.com/user-attachments/assets/6eae766c-faa5-4d27-9822-6bc6e0cc228d" />


### 📝 Registration & OTP Verification
<img width="1918" height="912" alt="Screenshot 2026-08-23 205442" src="https://github.com/user-attachments/assets/8b05a74e-f4cf-4b0f-af2c-1539a5275450" />
<img width="1910" height="908" alt="Screenshot 2026-08-23 205627" src="https://github.com/user-attachments/assets/4938f384-efa6-428a-acc2-03dd49108569" />
<img width="1912" height="914" alt="Screenshot 2026-08-23 205653" src="https://github.com/user-attachments/assets/bc27bdd3-fd99-47ae-b5c4-5661633d6ec2" />
<img width="1918" height="912" alt="Screenshot 2026-08-23 205727" src="https://github.com/user-attachments/assets/11be2f09-61ce-4dea-a6e3-f8818849b7be" />


### 📚 Document Dashboard
<img width="1916" height="912" alt="Screenshot 2026-08-23 205537" src="https://github.com/user-attachments/assets/a2fd4bd1-c0c8-4bea-9246-2be465b04f68" />


---

## ✨ Features

### 👤 Authentication

* User registration and login
* Email OTP verification
* JWT authentication
* Access and refresh tokens
* Token refresh
* Logout
* Forgot password
* Password reset using OTP
* Resend registration OTP
* Google OAuth 2.0

### 📄 Document Management

* Upload documents
* List user documents
* Delete documents
* User-specific document authorization
* Document content extraction

### 🤖 AI Features

* AI-powered document processing
* Generate notes from documents
* Generate notes for individual documents
* Upload multiple documents for AI processing
* Background AI processing using FastAPI `BackgroundTasks`

### ⚡ Backend

* FastAPI REST API
* SQLAlchemy ORM
* MySQL database
* Redis for temporary authentication data
* Pydantic schemas
* Environment-based configuration

---

## 🛠️ Tech Stack

| Category                  | Technologies                                       |
| ------------------------- | -------------------------------------------------- |
| Frontend                  | React, Vite, Axios                                 |
| Backend                   | Python, FastAPI, SQLAlchemy, Pydantic, Uvicorn     |
| Database                  | MySQL                                              |
| Authentication            | JWT, Password Hashing, Email OTP, Google OAuth     |
| Cache / Temporary Storage | Redis                                              |
| AI                        | LLM-based document processing and notes generation |
| Tools                     | Git, GitHub, Postman, Swagger UI, VS Code          |

---

## 📂 Project Structure

```text
notes-generator-AI/
│
├── backend/
│   ├── src/
│   │   ├── auth/
│   │   ├── user/
│   │   ├── document/
│   │   ├── extraction/
│   │   ├── notes_ai/
│   │   ├── utils/
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── screenshots/
│   ├── login.png
│   ├── register.png
│   ├── dashboard.png
│   ├── document-upload.png
│   ├── ai-notes.png
│   └── swagger.png
│
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

### Prerequisites

Make sure the following are installed:

* Python 3.x
* Node.js
* npm
* MySQL
* Redis-compatible server
* Git

### 1. Clone the Repository

```bash
git clone https://github.com/duttasagar/notes-generator-AI.git
cd notes-generator-AI
```

---

### 2. Backend Setup

```bash
cd backend
```

Create a virtual environment:

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

### 3. Database Setup

The application uses **MySQL with SQLAlchemy**.

Create the database:

```sql
CREATE DATABASE notes_generator_ai;
```

Configure the database connection in `.env`:

```env
DATABASE_URL=mysql+pymysql://USERNAME:PASSWORD@localhost:3306/notes_generator_ai
```

---

### 4. Redis Setup

Redis is used for temporary authentication data such as OTPs and token-related data.

```env
REDIS_URL=redis://localhost:6379/0
```

Make sure your Redis-compatible server is running.

Test the connection:

```bash
redis-cli ping
```

Expected:

```text
PONG
```

---

### 5. Environment Variables

Create a `.env` file inside the `backend` directory.

Example:

```env
DATABASE_URL=mysql+pymysql://USERNAME:PASSWORD@localhost:3306/notes_generator_ai

SECRET_KEY=your_secret_key

ACCESS_TOKEN_EXPIRE_MINUTES=30

REFRESH_TOKEN_EXPIRE_DAYS=7

REDIS_URL=redis://localhost:6379/0

GROQ_API_KEY=your_groq_api_key

GOOGLE_CLIENT_ID=your_google_client_id

GOOGLE_CLIENT_SECRET=your_google_client_secret

GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/auth/google/callback
```

> Never commit your `.env` file or API keys to GitHub.

Add this to `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

---

### 6. Run the Backend

From the `backend` directory:

```bash
uvicorn src.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

---

### 7. Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## 📖 API Documentation

FastAPI provides interactive API documentation through Swagger UI and ReDoc.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

Swagger can be used to test the API directly from the browser.

---

# 🔐 API Endpoints

## 👤 User Authentication

| Method | Endpoint                 | Description               |
| ------ | ------------------------ | ------------------------- |
| `POST` | `/user/register`         | Register a new user       |
| `POST` | `/user/login`            | Login                     |
| `GET`  | `/user/is_auth`          | Check authentication      |
| `POST` | `/user/verify_otp`       | Verify registration OTP   |
| `POST` | `/user/resend-otp`       | Resend registration OTP   |
| `POST` | `/user/refresh`          | Refresh access token      |
| `POST` | `/user/logout`           | Logout                    |
| `POST` | `/user/forgot-password`  | Start password recovery   |
| `POST` | `/user/verify-reset-otp` | Verify password reset OTP |
| `POST` | `/user/reset-password`   | Reset password            |

---

## 🌐 Google OAuth

| Method | Endpoint                | Description                  |
| ------ | ----------------------- | ---------------------------- |
| `GET`  | `/auth/google/login`    | Start Google OAuth login     |
| `GET`  | `/auth/google/callback` | Handle Google OAuth callback |

---

## 📄 Document

| Method   | Endpoint                  | Description                         |
| -------- | ------------------------- | ----------------------------------- |
| `GET`    | `/document`               | List authenticated user's documents |
| `POST`   | `/document/upload`        | Upload a document                   |
| `DELETE` | `/document/{document_id}` | Delete a document                   |

### Upload Document

```http
POST /document/upload
```

Request type:

```text
multipart/form-data
```

Form field:

```text
file
```

---

## 🔍 Document Extraction

| Method | Endpoint                    | Description                     |
| ------ | --------------------------- | ------------------------------- |
| `POST` | `/extraction/{document_id}` | Extract content from a document |

Example:

```http
POST /extraction/1
```

The endpoint verifies that the document belongs to the authenticated user.

---

## 🤖 AI Notes

| Method | Endpoint                     | Description                                   |
| ------ | ---------------------------- | --------------------------------------------- |
| `POST` | `/ai/generate`               | Upload multiple files and start AI generation |
| `POST` | `/ai/generate/{document_id}` | Start AI processing for a document            |
| `POST` | `/ai/notes/{document_id}`    | Generate notes for a document                 |

For AI generation, FastAPI `BackgroundTasks` is used for background processing.

---

## 🔄 Application Flow

```text
Register
   ↓
Email OTP Verification
   ↓
Login
   ↓
JWT Authentication
   ↓
Upload Document
   ↓
Extract Document Content
   ↓
AI Processing
   ↓
Generate Notes
```

---

## 🔴 Redis

Redis is used for temporary authentication-related data, including:

* OTP storage
* OTP expiration
* Password reset OTP
* Token-related temporary data

Example:

```text
User Registration
       ↓
Generate OTP
       ↓
Store OTP in Redis
       ↓
Send OTP by Email
       ↓
Verify OTP
       ↓
Account Verification
```

---

## 📧 Email

Email functionality is used for:

* Registration OTP
* Resending registration OTP
* Password recovery OTP
* Password reset verification

---

## ⚡ Background Processing

FastAPI `BackgroundTasks` is used for operations such as:

* Sending emails
* AI document generation
* Processing multiple uploaded documents

This allows longer-running operations to execute in the background instead of blocking the API request.

---

## 🔒 Security

The application includes:

* JWT authentication
* Access and refresh tokens
* Password hashing
* OTP verification
* OTP expiration
* Redis-based temporary authentication data
* Google OAuth
* Protected API endpoints
* User-specific document authorization
* Environment variables for sensitive credentials

Users can only access documents associated with their own account.

---

## 🧪 API Testing

The API can be tested using:

* **Swagger UI**
* **Postman**

Recommended workflow:

```text
1. Register
2. Verify OTP
3. Login
4. Get Access Token
5. Authorize API
6. Upload Document
7. Extract Document
8. Generate AI Notes
```

---

## 🚀 Deployment

The application can be deployed using platforms such as:

* Render
* Railway
* AWS
* Azure
* Google Cloud
* DigitalOcean

Production deployment requires properly configured:

* FastAPI backend
* MySQL database
* Redis
* Email service
* LLM API
* Environment variables

---

## 🔮 Future Improvements

* [ ] Support additional document formats
* [ ] Download generated notes
* [ ] Export notes as PDF/DOCX
* [ ] Add AI chat functionality
* [ ] Add document processing progress
* [ ] Add document history
* [ ] Add automated tests
* [ ] Add Docker support
* [ ] Improve logging and monitoring
* [ ] Deploy production version

---

## 👨‍💻 Author

### Sagar Dutta

**Full Stack Developer | Python | FastAPI | React | SQL | AI**

**GitHub:** [duttasagar](https://github.com/duttasagar)

**Project:** [notes-generator-AI](https://github.com/duttasagar/notes-generator-AI)

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.
