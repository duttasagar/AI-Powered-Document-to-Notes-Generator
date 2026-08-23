import { useState } from "react";
import Field from "./Field";
import { sendForgotPasswordOtp } from "../service/authService";

export default function SendOtpPage({ onSent, onBack }) {
  const [status, setStatus] = useState({ message: "", error: false });
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setStatus({ message: "Sending verification code...", error: false });
    setIsSubmitting(true);
    const email = new FormData(event.currentTarget).get("email");
    try {
      await sendForgotPasswordOtp(email);
      onSent(email);
    } catch (error) {
      setStatus({ message: error.message, error: true });
    } finally {
      setIsSubmitting(false);
    }
  }

  return <form onSubmit={handleSubmit}><Field label="Email address" name="email" type="email" placeholder="you@example.com" autoComplete="email" required /><button className="submit-button" type="submit" disabled={isSubmitting}>Send OTP <span aria-hidden="true">→</span></button><button className="back-link" type="button" onClick={onBack}>Back to sign in</button><p className={`form-status${status.error ? " error" : ""}`} role="status">{status.message}</p></form>;
}
