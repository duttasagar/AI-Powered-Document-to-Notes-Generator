import { useState } from "react";
import Field from "./Field";
import { loginUser } from "../service/authService";

export default function LoginPage({ onForgotPassword, onLogin }) {
  const [showPassword, setShowPassword] = useState(false);
  const [status, setStatus] = useState({ message: "", error: false });
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setStatus({ message: "Signing you in...", error: false });
    setIsSubmitting(true);
    const formData = new FormData(event.currentTarget);
    try {
      const result = await loginUser({ email: formData.get("email"), password: formData.get("password") });
      localStorage.setItem("notely_access_token", result.access_token);
      localStorage.setItem("notely_refresh_token", result.refresh_token);
      setStatus({ message: "Login successful.", error: false });
      onLogin?.(formData.get("email"));
    } catch (error) {
      setStatus({ message: error.message, error: true });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form id="login-form" onSubmit={handleSubmit}>
      <Field label="Email address" name="email" type="email" placeholder="you@example.com" autoComplete="email" required />
      <label className="field"><span>Password</span><span className="password-wrap"><input name="password" type={showPassword ? "text" : "password"} autoComplete="current-password" placeholder="Your password" required /><button type="button" className="password-toggle" aria-label={`${showPassword ? "Hide" : "Show"} password`} onClick={() => setShowPassword((visible) => !visible)}>{showPassword ? "Hide" : "Show"}</button></span></label>
      <button className="forgot-link" type="button" onClick={onForgotPassword}>Forgot password?</button>
      <button className="submit-button" type="submit" disabled={isSubmitting}>Sign in <span aria-hidden="true">→</span></button>
      <p className={`form-status${status.error ? " error" : ""}`} role="status">{status.message}</p>
    </form>
  );
}
