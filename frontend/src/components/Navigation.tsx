import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import { useAuth } from "@/context/AuthContext";

const LINKS = [
  { href: "/dashboard", label: "Home" },
  { href: "/dashboard#projects", label: "Projects" },
  { href: "/dashboard#skills", label: "Skills" },
  { href: "/workflows", label: "Workflows" },
];

export default function Navigation(): JSX.Element {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav aria-label="Main navigation" className="bg-white shadow-sm sticky top-0 z-10">
      <div className="flex items-center justify-between px-4 py-3">
        <span className="font-bold text-lg text-gray-800">AI Runtime</span>

        <ul className="hidden md:flex items-center gap-6">
          {LINKS.map((link) => {
            const active = router.asPath === link.href || router.pathname === link.href;
            return (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className={active ? "text-blue-600 font-semibold underline" : "text-gray-700 hover:text-blue-600"}
                >
                  {link.label}
                </Link>
              </li>
            );
          })}
        </ul>

        <div className="hidden md:flex items-center gap-4">
          {user && <span className="text-sm text-gray-600">{user.email}</span>}
          <button
            type="button"
            onClick={logout}
            className="rounded-md bg-gray-100 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-200"
          >
            Logout
          </button>
        </div>

        <button
          type="button"
          className="md:hidden flex flex-col gap-1.5 p-2"
          aria-label="Toggle menu"
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen((open) => !open)}
        >
          <span className="block h-0.5 w-6 bg-gray-800" />
          <span className="block h-0.5 w-6 bg-gray-800" />
          <span className="block h-0.5 w-6 bg-gray-800" />
        </button>
      </div>

      {menuOpen && (
        <div className="md:hidden border-t border-gray-100 px-4 py-3 space-y-3">
          <ul className="space-y-2">
            {LINKS.map((link) => (
              <li key={link.href}>
                <Link href={link.href} className="block text-gray-700 hover:text-blue-600">
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
          {user && <p className="text-sm text-gray-600">{user.email}</p>}
          <button
            type="button"
            onClick={logout}
            className="w-full rounded-md bg-gray-100 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"
          >
            Logout
          </button>
        </div>
      )}
    </nav>
  );
}
