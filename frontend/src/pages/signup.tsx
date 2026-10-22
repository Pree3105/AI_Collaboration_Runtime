import { useMemo, useState, type FormEvent } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

type Strength = "weak" | "fair" | "strong";

function getPasswordStrength(password: string): Strength {
  const hasUpper = /[A-Z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSpecial = /[^A-Za-z0-9]/.test(password);

  if (password.length < 8 || !hasUpper || !hasNumber) return "weak";
  if (password.length >= 12 && hasSpecial) return "strong";
  return "fair";
}

const STRENGTH_STYLES: Record<Strength, { label: string; className: string }> = {
  weak: { label: "Weak", className: "text-red-600" },
  fair: { label: "Fair", className: "text-yellow-600" },
  strong: { label: "Strong", className: "text-green-600" },
};

export default function SignupPage(): JSX.Element {
  const { register, error } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [touched, setTouched] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const emailValid = email.length === 0 || EMAIL_REGEX.test(email);
  const strength = useMemo(() => getPasswordStrength(password), [password]);
  const passwordValid =password.length > 0;
  // const passwordValid = strength !== "weak" && password.length > 0;
  const passwordsMatch = confirmPassword.length > 0 && confirmPassword === password;

  const formValid =
    EMAIL_REGEX.test(email) && passwordValid && passwordsMatch && termsAccepted;

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setTouched(true);
    if (!formValid) return;
    setSubmitting(true);
    try {
      await register(email, password);
    } catch {
      // error message is surfaced via the `error` field from useAuth()
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-[400px] bg-white shadow-md rounded-lg p-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-6 text-center">Sign up</h1>
        <form onSubmit={handleSubmit} aria-label="Signup form" className="space-y-4" noValidate>
          {error && (
            <p role="alert" className="text-red-600 text-sm">
              {error}
            </p>
          )}

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              aria-invalid={!emailValid}
              aria-describedby="email-error"
              className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            />
            {!emailValid && (
              <p id="email-error" className="mt-1 text-sm text-red-600">
                Invalid email
              </p>
            )}
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              aria-describedby="password-strength"
              className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            />
            {password.length > 0
            //  && (
            //   <p id="password-strength" className={`mt-1 text-sm font-medium ${STRENGTH_STYLES[strength].className}`}>
            //     {STRENGTH_STYLES[strength].label}
            //   </p>
            // )
            }
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
              Confirm password
            </label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              required
              aria-describedby="confirm-password-status"
              className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            />
            {confirmPassword.length > 0 && (
              <p
                id="confirm-password-status"
                className={`mt-1 text-sm ${passwordsMatch ? "text-green-600" : "text-red-600"}`}
              >
                {passwordsMatch ? "✓ Passwords match" : "✗ Passwords do not match"}
              </p>
            )}
          </div>

          <div>
            <div className="flex items-center gap-2">
              <input
                id="termsAccepted"
                name="termsAccepted"
                type="checkbox"
                checked={termsAccepted}
                onChange={(event) => setTermsAccepted(event.target.checked)}
                required
                aria-describedby="terms-error"
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <label htmlFor="termsAccepted" className="text-sm text-gray-700">
                I accept the{" "}
                <Link href="/terms" className="text-blue-600 hover:underline">
                  terms and conditions
                </Link>
              </label>
            </div>
            {touched && !termsAccepted && (
              <p id="terms-error" className="mt-1 text-sm text-red-600">
                Accept terms
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={!formValid || submitting}
            className="w-full flex items-center justify-center gap-2 rounded-md bg-blue-600 text-white font-medium py-2 hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
          >
            {submitting && (
              <span
                className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"
                aria-hidden="true"
              />
            )}
            {submitting ? "Signing up..." : "Sign up"}
          </button>
        </form>

        <p className="mt-4 text-sm text-center text-gray-600">
          Already have an account?{" "}
          <Link href="/login" className="text-blue-600 hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </main>
  );
}
