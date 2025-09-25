import axios, { AxiosResponse } from 'axios';
import {
  SystemHealth,
  BusinessRule,
  AnalysisRequest,
  AnalysisResponse,
  ExecutionRequest,
  ExecutionResponse,
  ChatRequest,
  ChatResponse
} from '../types';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging and auth
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    
    if (error.response?.status === 401) {
      // Handle unauthorized access
      console.error('Unauthorized access');
    } else if (error.response?.status >= 500) {
      // Handle server errors
      console.error('Server error');
    } else if (!error.response) {
      // Handle network errors
      console.error('Network error - API server may be down');
    }
    
    return Promise.reject(error);
  }
);

// API Service Class
export class ApiService {
  /**
   * Get system health status
   */
  static async getHealth(): Promise<SystemHealth> {
    const response: AxiosResponse<SystemHealth> = await apiClient.get('/health');
    return response.data;
  }

  /**
   * Get all business rules
   */
  static async getRules(): Promise<BusinessRule[]> {
    const response: AxiosResponse<{ rules: BusinessRule[] }> = await apiClient.get('/rules');
    return Array.isArray(response.data.rules) ? response.data.rules : [];
  }

  /**
   * Get rules by domain
   */
  static async getRulesByDomain(domain: string): Promise<BusinessRule[]> {
    const response: AxiosResponse<{ rules: BusinessRule[] }> = await apiClient.get(
      `/rules?domain=${encodeURIComponent(domain)}`
    );
    return Array.isArray(response.data.rules) ? response.data.rules : [];
  }

  /**
   * Get rules by category
   */
  static async getRulesByCategory(category: string): Promise<BusinessRule[]> {
    const response: AxiosResponse<{ rules: BusinessRule[] }> = await apiClient.get(
      `/rules?category=${encodeURIComponent(category)}`
    );
    return Array.isArray(response.data.rules) ? response.data.rules : [];
  }

  /**
   * Get rule by ID
   */
  static async getRuleById(ruleId: string): Promise<BusinessRule> {
    const response: AxiosResponse<BusinessRule> = await apiClient.get(
      `/rules/${encodeURIComponent(ruleId)}`
    );
    return response.data;
  }

  /**
   * Analyze a business scenario
   */
  static async analyzeScenario(request: AnalysisRequest): Promise<AnalysisResponse> {
    const response: AxiosResponse<AnalysisResponse> = await apiClient.post(
      '/analyze',
      request
    );
    return response.data;
  }

  /**
   * Execute business rules for a scenario
   */
  static async executeRules(request: ExecutionRequest): Promise<ExecutionResponse> {
    const response: AxiosResponse<ExecutionResponse> = await apiClient.post(
      '/execute',
      request
    );
    return response.data;
  }

  /**
   * Execute a single rule
   */
  static async executeRule(request: { rule_id: string; parameters: Record<string, unknown>; context?: Record<string, unknown>; scenario?: string }): Promise<ExecutionResponse> {
    // Convert single rule execution to the backend's scenario-based format
    const executionRequest: ExecutionRequest = {
      scenario: request.scenario || `Execute rule ${request.rule_id} with provided parameters`,
      context: request.context,
      rule_ids: [request.rule_id],
      parameters: request.parameters
    };
    
    const response: AxiosResponse<ExecutionResponse> = await apiClient.post('/execute', executionRequest);
    return response.data;
  }

  /**
   * Chat with the agentic system
   */
  static async chatWithAgent(request: ChatRequest): Promise<ChatResponse> {
    const response: AxiosResponse<ChatResponse> = await apiClient.post(
      '/chat',
      request
    );
    return response.data;
  }

  /**
   * Get available domains
   */
  static async getDomains(): Promise<string[]> {
    const rules = await this.getRules();
    const domains = [...new Set(rules.map(rule => rule.domain))];
    return domains.sort();
  }

  /**
   * Get available categories
   */
  static async getCategories(): Promise<string[]> {
    const rules = await this.getRules();
    const categories = [...new Set(rules.map(rule => rule.category))];
    return categories.sort();
  }

  /**
   * Search rules by text
   */
  static async searchRules(query: string): Promise<BusinessRule[]> {
    const rules = await this.getRules();
    const lowercaseQuery = query.toLowerCase();
    
    return rules.filter(rule => 
      rule.name.toLowerCase().includes(lowercaseQuery) ||
      rule.description.toLowerCase().includes(lowercaseQuery) ||
      rule.domain.toLowerCase().includes(lowercaseQuery) ||
      rule.category.toLowerCase().includes(lowercaseQuery)
    );
  }

  /**
   * Filter rules by multiple criteria
   */
  static async filterRules(filters: {
    domain?: string;
    category?: string;
    priority?: number;
    search?: string;
  }): Promise<BusinessRule[]> {
    let rules = await this.getRules();
    
    // Ensure rules is an array
    if (!Array.isArray(rules)) {
      console.error('getRules() did not return an array:', rules);
      return [];
    }

    // Apply domain filter
    if (filters.domain) {
      rules = rules.filter(rule => rule.domain === filters.domain);
    }

    // Apply category filter
    if (filters.category) {
      rules = rules.filter(rule => rule.category === filters.category);
    }

    // Apply priority filter
    if (filters.priority !== undefined) {
      rules = rules.filter(rule => rule.priority >= filters.priority!);
    }

    // Apply search filter
    if (filters.search) {
      const query = filters.search.toLowerCase();
      rules = rules.filter(rule => 
        rule.name.toLowerCase().includes(query) ||
        rule.description.toLowerCase().includes(query) ||
        rule.domain.toLowerCase().includes(query) ||
        rule.category.toLowerCase().includes(query)
      );
    }

    return rules;
  }
}

// Error handling utility
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Utility function to handle API errors
export const handleApiError = (error: any): ApiError => {
  if (error.response) {
    return new ApiError(
      error.response.data?.detail || error.response.data?.message || 'API Error',
      error.response.status,
      error.response.data?.code
    );
  } else if (error.request) {
    return new ApiError('Network error - Unable to reach the server');
  } else {
    return new ApiError(error.message || 'Unknown error occurred');
  }
};

export default ApiService;