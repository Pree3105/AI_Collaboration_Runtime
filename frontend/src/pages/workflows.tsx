import { useState } from "react";
import Navigation from "@/components/Navigation";
import TaskList from "@/components/TaskList";
import ExecutionStatus from "@/components/ExecutionStatus";
import { useWorkflows, type Task } from "@/hooks/useWorkflows";

export default function WorkflowsPage(): JSX.Element {
  const { tasks, workflow, error, runWorkflow } = useWorkflows();
  const [selected, setSelected] = useState<Task | null>(null);

  function handleExecute(task: Task): void {
    setSelected(task);
    runWorkflow(task.id);
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <main className="max-w-6xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">Workflows</h1>
        {error && (
          <p role="alert" className="text-red-600 text-sm mb-4">
            {error}
          </p>
        )}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TaskList tasks={tasks} selectedId={selected?.id ?? null} onSelect={setSelected} onExecute={handleExecute} />
          <ExecutionStatus
            task={selected}
            workflow={selected && workflow?.task_id === selected.id ? workflow : null}
            onRetry={() => selected && runWorkflow(selected.id)}
          />
        </div>
      </main>
    </div>
  );
}
