import type { IncomingMessage } from "http";

const AUTH_COOKIE_NAME = "access_token";
const COOKIE_MAX_AGE_SECONDS = 60 * 60 * 24; // 24h, matches backend token expiry

function isProduction(): boolean {
  return process.env.NODE_ENV === "production";
}

/**
 * A true HttpOnly cookie can only be set by a server response header — client
 * JavaScript cannot set the HttpOnly flag on a cookie it writes itself. This
 * app calls the FastAPI backend directly from the browser, and the backend
 * authenticates via an `Authorization: Bearer <token>` header (not a cookie),
 * so the token is kept in a Secure/SameSite cookie that JS can read back out
 * and attach to requests (see utils/api.ts).
 */
export function setAuthCookie(token: string): void {
  if (typeof document === "undefined") return;
  const secure = isProduction() ? "; Secure" : "";
  document.cookie = `${AUTH_COOKIE_NAME}=${encodeURIComponent(token)}; path=/; max-age=${COOKIE_MAX_AGE_SECONDS}; SameSite=Lax${secure}`;
}

export function getAuthCookie(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.split("; ").find((row) => row.startsWith(`${AUTH_COOKIE_NAME}=`));
  return match ? decodeURIComponent(match.slice(AUTH_COOKIE_NAME.length + 1)) : null;
}

export function clearAuthCookie(): void {
  if (typeof document === "undefined") return;
  document.cookie = `${AUTH_COOKIE_NAME}=; path=/; max-age=0; SameSite=Lax`;
}

/**
 * Server-side cookie read for `getServerSideProps`. Pages Router has no
 * `next/headers` (that API is App Router-only) — reading `req.headers.cookie`
 * inside `getServerSideProps` is the Pages Router equivalent.
 */
export function getAuthCookieFromRequest(req: IncomingMessage): string | null {
  const header = req.headers.cookie;
  if (!header) return null;
  const match = header.split("; ").find((row) => row.startsWith(`${AUTH_COOKIE_NAME}=`));
  return match ? decodeURIComponent(match.slice(AUTH_COOKIE_NAME.length + 1)) : null;
}

export interface JwtPayload {
  sub: string;
  email: string;
  role: string;
  exp: number;
}

export function decodeJwtPayload(token: string): JwtPayload | null {
  try {
    const [, payload] = token.split(".");
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const json = decodeURIComponent(
      atob(normalized)
        .split("")
        .map((c) => "%" + c.charCodeAt(0).toString(16).padStart(2, "0"))
        .join("")
    );
    return JSON.parse(json) as JwtPayload;
  } catch {
    return null;
  }
}

export function isTokenExpired(payload: JwtPayload): boolean {
  return payload.exp * 1000 < Date.now();
}
