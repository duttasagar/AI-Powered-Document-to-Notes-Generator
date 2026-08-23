import { useState } from "react";
import BrandPanel from "./auth/BrandPanel";
import LoginPage from "./auth/LoginPage";
import RegisterPage from "./auth/RegisterPage";
import ResetPasswordPage from "./auth/ResetPasswordPage";
import SendOtpPage from "./auth/SendOtpPage";
import VerifyOtpPage from "./auth/VerifyOtpPage";
import Dashboard from "./dashboard/Dashboard";
import { getGoogleLoginUrl } from "./service/authService";

function googleCallbackParams() {
  if (!window.location.hash.startsWith("#google-callback")) return null;
  return new URLSearchParams(window.location.hash.split("?")[1] || "");
}

function initialView() {
  const callbackParams = googleCallbackParams();
  if (callbackParams?.get("token") && callbackParams.get("email")) return "dashboard";
  if (window.location.hash === "#dashboard") return "dashboard";
  if (window.location.hash === "#login") return "login";
  if (window.location.hash === "#forgot-password") return "forgot-password";
  return "register";
}

export default function App() {
  const [view, setView] = useState(initialView);
  const [flowEmail, setFlowEmail] = useState("");
  const [userEmail, setUserEmail] = useState(() => {
    const callbackParams = googleCallbackParams();
    const token = callbackParams?.get("token");
    const refreshToken = callbackParams?.get("refresh_token");
    const email = callbackParams?.get("email");
    if (token && email) {
      localStorage.setItem("notely_access_token", token);
      if (refreshToken) localStorage.setItem("notely_refresh_token", refreshToken);
      window.history.replaceState(null, "", "#dashboard");
      return email;
    }
    return "";
  });
  const [otpMode, setOtpMode] = useState("registration");

  function switchView(nextView) {
    setView(nextView);
    window.history.replaceState(null, "", `#${nextView}`);
  }

  const isAuthFlow = ["login", "forgot-password", "verify", "reset"].includes(view);
  const supportsGoogleLogin = view === "login" || view === "register";
  if (view === "dashboard") return <Dashboard userName={userEmail || "there"} onLogout={() => switchView("login")} />;
  const pageContent = {
    login: { heading: "Welcome back", subtitle: "Sign in to turn your documents into useful notes." },
    "forgot-password": { heading: "Reset your password", subtitle: "We will send a one-time password to your email." },
    verify: { heading: "Check your email", subtitle: "Enter the verification code we just sent you." },
    reset: { heading: "Choose a new password", subtitle: "Your account is almost ready for a fresh start." },
    register: { heading: "Create your free account", subtitle: "Start turning long documents into clear study notes." },
  }[view];

  function startRegistrationVerification(email) {
    setFlowEmail(email);
    setOtpMode("registration");
    switchView("verify");
  }

  function startResetVerification(email) {
    setFlowEmail(email);
    setOtpMode("reset");
    switchView("verify");
  }

  function renderPage() {
    if (view === "login") return <LoginPage onForgotPassword={() => switchView("forgot-password")} onLogin={(email) => { setUserEmail(email); switchView("dashboard"); }} />;
    if (view === "register") return <RegisterPage onRegistered={startRegistrationVerification} />;
    if (view === "forgot-password") return <SendOtpPage onSent={startResetVerification} onBack={() => switchView("login")} />;
    if (view === "verify") return <VerifyOtpPage email={flowEmail} mode={otpMode} onVerified={() => switchView(otpMode === "reset" ? "reset" : "login")} onBack={() => switchView(otpMode === "reset" ? "forgot-password" : "register")} />;
    return <ResetPasswordPage email={flowEmail} onComplete={() => switchView("login")} />;
  }

  return (
    <main className="auth-shell">
      <BrandPanel />
      <section className="form-panel" aria-labelledby="form-heading">
        <div className="top-nav"><span>{isAuthFlow ? "New to Notely?" : "Already have an account?"}</span><button type="button" onClick={() => switchView(isAuthFlow ? "register" : "login")}>{isAuthFlow ? "Create account" : "Sign in"} <span aria-hidden="true">↗</span></button></div>
        <div className="form-wrap">
          <p className="mobile-kicker">WELCOME TO NOTELY</p>
          <h2 id="form-heading">{pageContent.heading}</h2>
          <p className="form-subtitle">{pageContent.subtitle}</p>
          {supportsGoogleLogin && <div className="social-actions"><button className="social-button" type="button" onClick={() => { window.location.href = getGoogleLoginUrl(); }}><span className="google-g">G</span>Continue with Google</button></div>}
          {supportsGoogleLogin && <div className="divider"><span>{view === "login" ? "or sign in with email" : "or sign up with email"}</span></div>}
          {renderPage()}
        </div>
        <p className="footer-note">Your notes are private by default.</p>
      </section>
    </main>
  );
}
