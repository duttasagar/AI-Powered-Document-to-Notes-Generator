import { useState } from "react";
import Field from "./Field";
import { resendRegistrationOtp, verifyRegistrationOtp, verifyResetOtp } from "../service/authService";

export default function VerifyOtpPage({ email, mode, onVerified, onBack }) {
  const [status, setStatus] = useState({ message: "", error: false });
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setStatus({ message: "Verifying code...", error: false });
    setIsSubmitting(true);
    const otp = new FormData(event.currentTarget).get("otp");
    try {
      const result = mode === "registration"
        ? await verifyRegistrationOtp({ email, otp })
        : await verifyResetOtp({ email, otp });
      onVerified(result.message || "OTP verified successfully.");
    } catch (error) {
      setStatus({ message: error.message, error: true });
    } finally {
      setIsSubmitting(false);
    }
  }

  async function resendOtp() {
    setStatus({ message: "Sending a new OTP...", error: false });
    try {
      const result = await resendRegistrationOtp(email);
      setStatus({ message: result.message, error: false });
    } catch (error) {
      setStatus({ message: error.message, error: true });
    }
  }

  return <form onSubmit={handleSubmit}><div className="otp-context">Code sent to <strong>{email}</strong></div><Field label="One-time password" name="otp" inputMode="numeric" pattern="[0-9]{4,8}" maxLength="8" placeholder="Enter your OTP" required /><button className="submit-button" type="submit" disabled={isSubmitting}>Verify OTP <span aria-hidden="true">→</span></button>{mode === "registration" && <button className="back-link" type="button" onClick={resendOtp}>Resend OTP</button>}<button className="back-link" type="button" onClick={onBack}>Use a different email</button><p className={`form-status${status.error ? " error" : ""}`} role="status">{status.message}</p></form>;
}
