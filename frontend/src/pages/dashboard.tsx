import type { GetServerSideProps } from "next";
import { useEffect } from "react";
import { useRouter } from "next/router";
import Navigation from "@/components/Navigation";
import ProjectList from "@/components/ProjectList";
import SkillRegistry from "@/components/SkillRegistry";
import { useAuth } from "@/context/AuthContext";
import { getAuthCookieFromRequest } from "@/utils/auth";

export const getServerSideProps: GetServerSideProps = async ({ req }) => {
  const token = getAuthCookieFromRequest(req);
  if (!token) {
    return { redirect: { destination: "/login", permanent: false } };
  }
  return { props: {} };
};

export default function DashboardPage(): JSX.Element {
  const { user, isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push("/login");
    }
  }, [loading, isAuthenticated, router]);

  if (loading || !user) {
    return <p className="p-6 text-gray-600">Loading...</p>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <main className="max-w-5xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Dashboard</h1>
        <p className="text-gray-600 mb-6">
          Signed in as {user.email} ({user.role})
        </p>
        <div className="space-y-8">
          <ProjectList />
          <SkillRegistry />
        </div>
      </main>
    </div>
  );
}
