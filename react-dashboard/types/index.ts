export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'done';
  created?: string;
  updated?: string;
  queue?: string;
  comments?: Array<{
    id: number;
    text: string;
    created_at?: number;
    updated_at?: number;
  }>;
  links?: {
    [relation: string]: string[];
  };
  epics?: string[];
  created_at?: number;
  updated_at?: number;
  started_at?: number | null;
  closed_at?: number | null;
}

export interface Epic {
  id: string;
  title: string;
  description?: string;
  status: 'open' | 'closed';
  child_tasks: string[];
  child_epics: string[];
  parent_epic?: string | null;
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
  csrfToken: string | null;
  login: () => Promise<void>;
  logout: () => void;
  refreshToken: () => void;
}
