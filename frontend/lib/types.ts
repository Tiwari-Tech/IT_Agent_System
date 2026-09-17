export type Role = "employee" | "it_support" | "it_admin";

export type User = {
  id: string;
  email: string;
  name: string;
  role: Role;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type Ticket = {
  id: string;
  external_ticket_id: string | null;
  title: string;
  description: string;
  status: "open" | "in_progress" | "resolved" | "closed";
  priority: "low" | "medium" | "high" | "critical";
  category: string | null;
  created_by: string;
  assigned_to: string | null;
  created_at: string;
  updated_at: string;
  creator: User;
  assignee: User | null;
};

export type TicketList = { items: Ticket[]; total: number; page: number; limit: number };
export type Message = { id: string; ticket_id: string | null; user_id: string | null; role: string; content: string; created_at: string };
export type DocumentItem = { id: string; title: string; source: string | null; file_type: string | null; storage_path: string | null; content_hash: string | null; metadata_: Record<string, unknown>; created_at: string; updated_at: string };
export type WorkflowResult = { ticket_id: string; workflow_id: string; status: string; requires_human_approval: boolean; review_result: string | null; resolution_plan: string | null; jira_issue_key: string | null; agent_run_ids: string[]; errors: string[]; state: Record<string, unknown> };
