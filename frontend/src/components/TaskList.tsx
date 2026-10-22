import type { Task } from "@/hooks/useWorkflows";
import ExecuteButton from "./ExecuteButton";

const STATUS_STYLES: Record<string, string> = {
  pending: "bg-gray-100 text-gray-700",
  executing: "bg-blue-100 text-blue-700",
  completed: "bg-green-100 text-green-700",
  error: "bg-red-100 text-red-700",
};

interface Props {
  tasks: Task[];
  selectedId: number | null;
  onSelect: (task: Task) => void;
  onExecute: (task: Task) => void;
}

export default function TaskList({ tasks, selectedId, onSelect, onExecute }: Props): JSX.Element {
  return (
    <div className="overflow-x-auto bg-white rounded-lg shadow-sm">
      <table className="w-full text-sm text-left">
        <thead>
          <tr className="border-b border-gray-200 text-gray-500">
            <th className="py-2 px-3 font-medium">ID</th>
            <th className="py-2 px-3 font-medium">Description</th>
            <th className="py-2 px-3 font-medium">Status</th>
            <th className="py-2 px-3 font-medium">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {tasks.map((task) => (
            <tr
              key={task.id}
              onClick={() => onSelect(task)}
              className={`cursor-pointer hover:bg-gray-50 ${selectedId === task.id ? "bg-blue-50" : ""}`}
            >
              <td className="py-2 px-3 text-gray-800">{task.id}</td>
              <td className="py-2 px-3 text-gray-800">{task.description}</td>
              <td className="py-2 px-3">
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_STYLES[task.status] ?? STATUS_STYLES.pending}`}>
                  {task.status}
                </span>
              </td>
              <td className="py-2 px-3">
                <ExecuteButton onClick={() => onExecute(task)} />
              </td>
            </tr>
          ))}
          {tasks.length === 0 && (
            <tr>
              <td colSpan={4} className="py-4 px-3 text-center text-gray-500">
                No tasks found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
