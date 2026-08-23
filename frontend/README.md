# Notely frontend

Install dependencies and start the React development server:

```bash
npm install
npm run dev
```

The app runs on the Vite URL shown in the terminal while the FastAPI server is running on `http://127.0.0.1:8000`.

The backend URL is configured in `.env` with `VITE_API_BASE_URL`. All auth requests are defined in `src/service/authService.js` and use the Axios client in `src/api/axios/axiosInstance.js`.

The registration form posts `name`, `username`, `email`, and `password` to `/user/register`. Google sign-up uses `/auth/google/login`.
