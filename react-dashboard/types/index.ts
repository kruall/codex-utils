export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'done';
  created?: string;
  updated?: string;
  queue?: string;
}

export interface TaskContextType {
  tasks: Task[];
  setTasks: (tasks: Task[] | ((prevTasks: Task[]) => Task[])) => void;
}

export interface TaskTableProps {
  tasks?: Task[];
}

export interface AuthContextType {
  token: string | null;
  login: () => Promise<void>;
  logout: () => void;
}
