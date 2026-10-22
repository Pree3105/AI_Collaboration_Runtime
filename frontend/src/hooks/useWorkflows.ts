import { useCallback, useEffect, useRef, useState } from "react";
import api from "@/utils/api";

export interface Task {
  id: number;
  description: string;
  status: "pending" | "executing" | "completed" | "error";
}

export interface WorkflowStatus {
  id: number;
  task_id: number;
  status: string;
  execution_graph: Record<string, unknown> | null;
  error?: string | null;
}

export function useWorkflows() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [workflow, setWorkflow] = useState<WorkflowStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      const { data } = await api.get<Task[]>("/tasks");
      setTasks(data);
    } catch (err) {
      setError("Failed to load tasks");
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const pollWorkflow = useCallback(
    (workflowId: number) => {
      stopPolling();
      pollRef.current = setInterval(async () => {
        try {
          const { data } = await api.get<WorkflowStatus>(`/workflows/${workflowId}`);
          setWorkflow(data);
          if (data.status === "completed" || data.status === "failed" || data.status === "error") {
            stopPolling();
            fetchTasks();
          }
        } catch {
          stopPolling();
        }
      }, 2000);
    },
    [fetchTasks, stopPolling]
  );

  const runWorkflow = useCallback(
    async (taskId: number) => {
      setError(null);
      setWorkflow(null);
      try {
        const { data } = await api.post<{ workflow_id: number; status: string }>("/workflows/run", {
          task_id: taskId,
        });
        setWorkflow({ id: data.workflow_id, task_id: taskId, status: data.status, execution_graph: null });
        pollWorkflow(data.workflow_id);
      } catch (err) {
        setError("Failed to start workflow");
      }
    },
    [pollWorkflow]
  );

  useEffect(() => stopPolling, [stopPolling]);

  return { tasks, workflow, error, runWorkflow, refetchTasks: fetchTasks };
}
