interface Skill {
  id: number;
  name: string;
  description: string;
  usageCount: number;
}

// Stub data — replace with a GET /skills call once that endpoint exists.
const STUB_SKILLS: Skill[] = [
  { id: 1, name: "summarize-report", description: "Summarizes a document into key findings.", usageCount: 12 },
  { id: 2, name: "extract-action-items", description: "Pulls action items out of meeting notes.", usageCount: 7 },
  { id: 3, name: "classify-ticket", description: "Categorizes a support ticket by type.", usageCount: 21 },
];

export default function SkillRegistry(): JSX.Element {
  return (
    <section id="skills" aria-label="Skill registry" className="bg-white rounded-lg shadow-sm p-4 sm:p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Skill Registry</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead>
            <tr className="border-b border-gray-200 text-gray-500">
              <th className="py-2 pr-4 font-medium">Name</th>
              <th className="py-2 pr-4 font-medium">Description</th>
              <th className="py-2 font-medium">Used</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {STUB_SKILLS.map((skill) => (
              <tr key={skill.id}>
                <td className="py-2 pr-4 font-medium text-gray-800">{skill.name}</td>
                <td className="py-2 pr-4 text-gray-600">{skill.description}</td>
                <td className="py-2 text-gray-600">{skill.usageCount}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
