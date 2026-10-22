interface Project {
  id: number;
  name: string;
  status: "pending" | "in_progress" | "completed";
  updatedAt: string;
}

// Stub data — replace with a GET /tasks call once that endpoint exists.
const STUB_PROJECTS: Project[] = [
  { id: 1, name: "Customer churn analysis", status: "in_progress", updatedAt: "2026-09-14" },
  { id: 2, name: "Quarterly report generator", status: "completed", updatedAt: "2026-09-10" },
  { id: 3, name: "Support ticket triage", status: "pending", updatedAt: "2026-09-05" },
];

const STATUS_STYLES: Record<Project["status"], string> = {
  pending: "bg-gray-100 text-gray-700",
  in_progress: "bg-blue-100 text-blue-700",
  completed: "bg-green-100 text-green-700",
};

export default function ProjectList(): JSX.Element {
  return (
    <section id="projects" aria-label="Projects" className="bg-white rounded-lg shadow-sm p-4 sm:p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Projects</h2>
      <ul className="divide-y divide-gray-100">
        {STUB_PROJECTS.map((project) => (
          <li key={project.id} className="flex flex-wrap items-center justify-between gap-2 py-3">
            <strong className="text-gray-800 font-medium">{project.name}</strong>
            <div className="flex items-center gap-3 text-sm text-gray-500">
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_STYLES[project.status]}`}>
                {project.status}
              </span>
              <span>updated {project.updatedAt}</span>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
