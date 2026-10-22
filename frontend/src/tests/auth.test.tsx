import { render, screen, fireEvent, waitFor, renderHook, act } from "@testing-library/react";
import type { ReactNode } from "react";
import { AuthProvider, useAuth } from "@/context/AuthContext";
import LoginPage from "@/pages/login";
import { getAuthCookie, clearAuthCookie } from "@/utils/auth";

const mockPush = jest.fn();

jest.mock("next/router", () => ({
  useRouter: () => ({ push: mockPush }),
}));

const mockLoginRequest = jest.fn();
const mockRegisterRequest = jest.fn();

jest.mock("@/utils/api", () => ({
  loginRequest: (...args: unknown[]) => mockLoginRequest(...args),
  registerRequest: (...args: unknown[]) => mockRegisterRequest(...args),
}));

function base64url(value: string): string {
  return Buffer.from(value).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function makeToken(overrides: Partial<{ sub: string; email: string; role: string; exp: number }> = {}): string {
  const payload = {
    sub: "1",
    email: "alice@example.com",
    role: "user",
    exp: Math.floor(Date.now() / 1000) + 3600,
    ...overrides,
  };
  return `${base64url(JSON.stringify({ alg: "HS256" }))}.${base64url(JSON.stringify(payload))}.signature`;
}

function Wrapper({ children }: { children: ReactNode }): JSX.Element {
  return <AuthProvider>{children}</AuthProvider>;
}

beforeEach(() => {
  mockPush.mockClear();
  mockLoginRequest.mockReset();
  mockRegisterRequest.mockReset();
  clearAuthCookie();
});

describe("LoginPage", () => {
  it("renders the login form", () => {
    render(<LoginPage />, { wrapper: Wrapper });

    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /log in/i })).toBeInTheDocument();
  });

  it("submits the form with the entered credentials", async () => {
    mockLoginRequest.mockResolvedValue({
      access_token: makeToken(),
      token_type: "bearer",
      user_id: 1,
      role: "user",
    });

    render(<LoginPage />, { wrapper: Wrapper });

    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "alice@example.com" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "supersecret" } });
    fireEvent.click(screen.getByRole("button", { name: /log in/i }));

    await waitFor(() => {
      expect(mockLoginRequest).toHaveBeenCalledWith("alice@example.com", "supersecret");
    });
  });

  it("stores the JWT in a cookie after a successful login", async () => {
    const token = makeToken();
    mockLoginRequest.mockResolvedValue({
      access_token: token,
      token_type: "bearer",
      user_id: 1,
      role: "user",
    });

    render(<LoginPage />, { wrapper: Wrapper });

    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "alice@example.com" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "supersecret" } });
    fireEvent.click(screen.getByRole("button", { name: /log in/i }));

    await waitFor(() => {
      expect(getAuthCookie()).toBe(token);
    });
  });

  it("redirects to /dashboard on successful login", async () => {
    mockLoginRequest.mockResolvedValue({
      access_token: makeToken(),
      token_type: "bearer",
      user_id: 1,
      role: "user",
    });

    render(<LoginPage />, { wrapper: Wrapper });

    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "alice@example.com" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "supersecret" } });
    fireEvent.click(screen.getByRole("button", { name: /log in/i }));

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/dashboard");
    });
  });

  it("shows an error message and does not redirect on failed login", async () => {
    mockLoginRequest.mockRejectedValue({
      isAxiosError: true,
      response: { data: { detail: "Invalid email or password" } },
    });

    render(<LoginPage />, { wrapper: Wrapper });

    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "alice@example.com" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "wrongpass" } });
    fireEvent.click(screen.getByRole("button", { name: /log in/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Invalid email or password");
    expect(mockPush).not.toHaveBeenCalled();
  });
});

describe("useAuth", () => {
  it("throws when used outside of an AuthProvider", () => {
    const { result } = renderHook(() => {
      try {
        return useAuth();
      } catch (err) {
        return err;
      }
    });

    expect(result.current).toBeInstanceOf(Error);
  });

  it("starts unauthenticated with no cookie, then loading turns false", async () => {
    const { result } = renderHook(() => useAuth(), { wrapper: Wrapper });

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
  });

  it("restores the user from an existing cookie on mount", async () => {
    document.cookie = `access_token=${encodeURIComponent(makeToken({ email: "bob@example.com", role: "admin" }))}; path=/`;

    const { result } = renderHook(() => useAuth(), { wrapper: Wrapper });

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual({ id: 1, email: "bob@example.com", role: "admin" });
  });

  it("clears user and cookie, and redirects to /login, on logout", async () => {
    document.cookie = `access_token=${encodeURIComponent(makeToken())}; path=/`;

    const { result } = renderHook(() => useAuth(), { wrapper: Wrapper });
    await waitFor(() => expect(result.current.isAuthenticated).toBe(true));

    act(() => {
      result.current.logout();
    });

    await waitFor(() => expect(getAuthCookie()).toBeNull());
    expect(mockPush).toHaveBeenCalledWith("/login");
  });
});
