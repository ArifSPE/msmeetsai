// API Types
export interface ApiResponse<T = any> {
  status: string;
  data?: T;
  message?: string;
  error?: string;
}

// Business Rule Types
export interface BusinessRule {
  id: string;
  name: string;
  description: string;
  domain: string;
  category: string;
  condition: string;
  action: string;
  priority: number;
  confidence: number | null;
  reasoning: string | null;
  parameters: Record<string, unknown> | null;
  metadata: Record<string, unknown> | null;
}

export interface RuleCondition {
  field: string;
  operator: string;
  value: any;
  type: 'string' | 'number' | 'boolean' | 'date';
}

export interface RuleAction {
  type: string;
  parameters: Record<string, any>;
}

// System Health Types
export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  message: string;
  system_info: {
    initialized: boolean;
    total_rules: number;
    domains: string[];
    categories: string[];
    vector_db_info: {
      status: string;
      collection_name: string;
      points_count: number;
      vector_size: number;
      distance: string;
    };
    embedding_model: string;
    vector_dimension: number;
  };
}

// Analysis Types
export interface AnalysisRequest {
  scenario: string;
  context?: Record<string, any>;
  domain?: string;
}

export interface AnalysisResponse {
  scenario: string;
  applicable_rules: BusinessRule[];
  decision_outcome: string;
  overall_confidence: number;
  reasoning: string;
  execution_plan: unknown[];
  metadata: {
    analysis_timestamp: string | null;
    total_rules_considered: number;
    rules_above_threshold: number;
    overall_assessment: string;
    recommended_actions: string[];
    context_provided: boolean;
    agent_iterations: number;
  };
}

// Execution Types
export interface ExecutionRequest {
  scenario: string;
  parameters: Record<string, unknown>;
  context?: Record<string, unknown>;
  rule_ids?: string[];
}

export interface ExecutionResult {
  rule_id: string;
  rule_name: string;
  status: string;
  duration: number;
  output: any;
  error: string | null;
}

export interface ExecutionResponse {
  scenario: string;
  execution_plan_id: string;
  overall_status: string;
  total_rules: number | null;
  successful_rules: number | null;
  failed_rules: number | null;
  execution_time: number | null;
  results: ExecutionResult[] | null;
  message: string;
}

// Chat Types
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  message: string;
  context?: Record<string, any>;
  conversation_history?: ChatMessage[];
}

export interface ChatResponse {
  response: string;
  context?: Record<string, any>;
  suggested_actions: string[];
}

// UI State Types
export interface LoadingState {
  loading: boolean;
  error: string | null;
}

export interface FilterOptions {
  domain?: string;
  category?: string;
  priority?: number;
  search?: string;
}

// Navigation Types
export interface NavItem {
  name: string;
  href: string;
  icon?: React.ComponentType<any>;
  current?: boolean;
}

// Component Props Types
export interface PageProps {
  title: string;
  children: React.ReactNode;
}

export interface CardProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
  actions?: React.ReactNode;
}

export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
}

export interface InputProps {
  label?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';
  className?: string;
}