import { useState } from "react";
import Field from "./Field";
import { registerUser } from "../service/authService";

export default function RegisterPage({ onRegistered }) {
  const [showPassword, setShowPassword] = useState(false);
  const [confirmPassword, setConfirmPassword] = useState("");
  const [status, setStatus] = useState({ message: "", error: false });
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    const password = formData.get("password");
    const payload = { name: formData.get("name"), username: formData.get("username"), email: formData.get("email"), password };
    if (password !== confirmPassword) {
      setStatus({ message: "Passwords do not match.", error: true });
      return;
    }
    setStatus({ message: "Creating your account...", error: false });
    setIsSubmitting(true);
    try {
      const result = await registerUser(payload);
      form.reset();
      setConfirmPassword("");
      onRegistered(payload.email, result.message);
    } catch (error) {
      setStatus({ message: error.message, error: true });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form id="register-form" onSubmit={handleSubmit}>
      <div className="field-row"><Field label="Full name" name="name" placeholder="Your name" autoComplete="name" required /><Field label="Username" name="username" placeholder="Choose a username" autoComplete="username" required /></div>
      <Field label="Email address" name="email" type="email" placeholder="you@example.com" autoComplete="email" required />
      <label className="field"><span>Password</span><span className="password-wrap"><input name="password" type={showPassword ? "text" : "password"} autoComplete="new-password" placeholder="At least 8 characters" minLength="8" required /><button type="button" className="password-toggle" aria-label={`${showPassword ? "Hide" : "Show"} password`} onClick={() => setShowPassword((visible) => !visible)}>{showPassword ? "Hide" : "Show"}</button></span></label>
      <label className="field"><span>Confirm password</span><span className="password-wrap"><input name="confirm_password" type={showPassword ? "text" : "password"} autoComplete="new-password" placeholder="Repeat your password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} required /><button type="button" className="password-toggle" aria-label={`${showPassword ? "Hide" : "Show"} password`} onClick={() => setShowPassword((visible) => !visible)}>{showPassword ? "Hide" : "Show"}</button></span></label>
      <label className="consent"><input name="consent" type="checkbox" required /><span>I agree to the <a href="#terms">Terms</a> and <a href="#privacy">Privacy Policy</a>.</span></label>
      <button className="submit-button" type="submit" disabled={isSubmitting}>Create account <span aria-hidden="true">→</span></button>
      <p className={`form-status${status.error ? " error" : ""}`} role="status">{status.message}</p>
    </form>
  );
}
