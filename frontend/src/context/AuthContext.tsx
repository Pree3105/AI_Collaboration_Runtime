import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useRouter } from "next/router";
import axios from "axios";
import { loginRequest, registerRequest } from "@/utils/api";
import {
  clearAuthCookie,
  decodeJwtPayload,
  getAuthCookie,
  isTokenExpired,
  setAuthCookie,
} from "@/utils/auth";

export interface AuthUser {
  id: number;
  email: string;
  role: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function userFromToken(token: string): AuthUser | null {
  const payload = decodeJwtPayload(token);
  if (!payload || isTokenExpired(payload)) return null;
  return { id: Number(payload.sub), email: payload.email, role: payload.role };
}

function extractErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err) && typeof err.response?.data?.detail === "string") {
    return err.response.data.detail;
  }
  if (err instanceof Error) return err.message;
  return "Something went wrong. Please try again.";
}

export function AuthProvider({ children }: { children: ReactNode }): JSX.Element {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const token = getAuthCookie();
    if (token) {
      const restoredUser = userFromToken(token);
      if (restoredUser) {
        setUser(restoredUser);
      } else {
        clearAuthCookie();
      }
    }
    setLoading(false);
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      setError(null);
      try {
        const response = await loginRequest(email, password);
        setAuthCookie(response.access_token);
        setUser(userFromToken(response.access_token));
        await router.push("/dashboard");
      } catch (err) {
        setError(extractErrorMessage(err));
        throw err;
      }
    },
    [router]
  );

  const register = useCallback(
    async (email: string, password: string) => {
      setError(null);
      try {
        const response = await registerRequest(email, password);
        setAuthCookie(response.access_token);
        setUser(userFromToken(response.access_token));
        await router.push("/dashboard");
      } catch (err) {
        setError(extractErrorMessage(err));
        throw err;
      }
    },
    [router]
  );

  const logout = useCallback(() => {
    clearAuthCookie();
    setUser(null);
    router.push("/login");
  }, [router]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: user !== null,
      loading,
      error,
      login,
      register,
      logout,
    }),
    [user, loading, error, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
