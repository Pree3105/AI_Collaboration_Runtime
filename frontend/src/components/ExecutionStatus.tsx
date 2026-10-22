import type { Task, WorkflowStatus } from "@/hooks/useWorkflows";
import ExecuteButton from "./ExecuteButton";

const STEP_LABELS: Record<string, string> = {
  pending: "Planning...",
  planned: "Planning complete",
  executing: "Executing...",
  executed: "Execution complete",
  completed: "Completed",
  failed: "Error",
  error: "Error",
};

interface Props {
  task: Task | null;
  workflow: WorkflowStatus | null;
  onRetry: () => void;
}

export default function ExecutionStatus({ task, workflow, onRetry }: Props): JSX.Element {
  if (!task) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 text-gray-500">
        Select a task to view execution details.
      </div>
    );
  }

  const isError = workflow?.status === "failed" || workflow?.status === "error";

  return (
    <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-800">Task #{task.id}</h2>
        <p className="text-gray-600 text-sm">{task.description}</p>
      </div>

      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-1">Current step</h3>
        <p className="text-blue-600 font-medium">
          {workflow ? STEP_LABELS[workflow.status] ?? workflow.status : "Not started"}
        </p>
      </div>

      {workflow && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-1">Execution log</h3>
          <ol className="text-sm text-gray-600 list-decimal list-inside space-y-0.5">
            <li>Task submitted (workflow #{workflow.id})</li>
            <li>{STEP_LABELS[workflow.status] ?? workflow.status}</li>
          </ol>
        </div>
      )}

      {isError && (
        <div className="space-y-2">
          <p role="alert" className="text-red-600 text-sm">
            {workflow?.error ?? "Workflow failed."}
          </p>
          <ExecuteButton onClick={onRetry} label="Retry" />
        </div>
      )}

      {workflow?.status === "completed" && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-1">Results</h3>
          <pre className="bg-gray-50 border border-gray-200 rounded-md p-3 text-xs text-gray-800 overflow-x-auto">
            {JSON.stringify(workflow.execution_graph, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
