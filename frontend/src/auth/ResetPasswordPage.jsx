import { useState } from "react";
import Field from "./Field";
import { resetPassword } from "../service/authService";

export default function ResetPasswordPage({ email, onComplete }) {
  const [showPassword, setShowPassword] = useState(false);
  const [confirmPassword, setConfirmPassword] = useState("");
  const [status, setStatus] = useState({ message: "", error: false });
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const newPassword = formData.get("new_password");
    if (newPassword !== confirmPassword) {
      setStatus({ message: "Passwords do not match.", error: true });
      return;
    }
    setStatus({ message: "Updating your password...", error: false });
    setIsSubmitting(true);
    try {
      const result = await resetPassword({ email, new_password: newPassword });
      onComplete(result.message || "Password reset successfully.");
    } catch (error) {
      setStatus({ message: error.message, error: true });
    } finally {
      setIsSubmitting(false);
    }
  }

  return <form onSubmit={handleSubmit}><div className="otp-context">Create a new password for <strong>{email}</strong></div><label className="field"><span>New password</span><span className="password-wrap"><input name="new_password" type={showPassword ? "text" : "password"} autoComplete="new-password" placeholder="At least 8 characters" minLength="8" required /><button type="button" className="password-toggle" aria-label={`${showPassword ? "Hide" : "Show"} password`} onClick={() => setShowPassword((visible) => !visible)}>{showPassword ? "Hide" : "Show"}</button></span></label><label className="field"><span>Confirm new password</span><input name="confirm_new_password" type={showPassword ? "text" : "password"} autoComplete="new-password" placeholder="Repeat your password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} required /></label><button className="submit-button" type="submit" disabled={isSubmitting}>Save new password <span aria-hidden="true">→</span></button><p className={`form-status${status.error ? " error" : ""}`} role="status">{status.message}</p></form>;
}
