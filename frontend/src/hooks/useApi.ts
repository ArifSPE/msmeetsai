import { useState, useEffect, useCallback } from 'react';
import { ApiService, handleApiError, ApiError } from '../services/api';
import {
  SystemHealth,
  BusinessRule,
  AnalysisRequest,
  AnalysisResponse,
  ExecutionRequest,
  ExecutionResponse,
  ChatRequest,
  ChatResponse,
} from '../types';

// Generic hook state interface
interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

// Custom hook for system health
export const useSystemHealth = () => {
  const [state, setState] = useState<UseApiState<SystemHealth>>({
    data: null,
    loading: true,
    error: null,
  });

  const fetchHealth = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const data = await ApiService.getHealth();
      setState({ data, loading: false, error: null });
    } catch (error) {
      const apiError = handleApiError(error);
      setState({ data: null, loading: false, error: apiError.message });
    }
  }, []);

  useEffect(() => {
    fetchHealth();
  }, [fetchHealth]);

  return { ...state, refetch: fetchHealth };
};

// Custom hook for business rules
export const useBusinessRules = (domain?: string, category?: string) => {
  const [state, setState] = useState<UseApiState<BusinessRule[]>>({
    data: null,
    loading: true,
    error: null,
  });

  const fetchRules = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      let data: BusinessRule[];
      if (domain) {
        data = await ApiService.getRulesByDomain(domain);
      } else if (category) {
        data = await ApiService.getRulesByCategory(category);
      } else {
        data = await ApiService.getRules();
      }
      setState({ data, loading: false, error: null });
    } catch (error) {
      const apiError = handleApiError(error);
      setState({ data: null, loading: false, error: apiError.message });
    }
  }, [domain, category]);

  useEffect(() => {
    fetchRules();
  }, [fetchRules]);

  return { ...state, refetch: fetchRules };
};

// Custom hook for domains
export const useDomains = () => {
  const [state, setState] = useState<UseApiState<string[]>>({
    data: null,
    loading: true,
    error: null,
  });

  const fetchDomains = async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const data = await ApiService.getDomains();
      setState({ data, loading: false, error: null });
    } catch (error) {
      const apiError = handleApiError(error);
      setState({ data: null, loading: false, error: apiError.message });
    }
  };

  useEffect(() => {
    fetchDomains();
  }, []);

  return { ...state, refetch: fetchDomains };
};

// Custom hook for categories
export const useCategories = () => {
  const [state, setState] = useState<UseApiState<string[]>>({
    data: null,
    loading: true,
    error: null,
  });

  const fetchCategories = async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const data = await ApiService.getCategories();
      setState({ data, loading: false, error: null });
    } catch (error) {
      const apiError = handleApiError(error);
      setState({ data: null, loading: false, error: apiError.message });
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  return { ...state, refetch: fetchCategories };
};

// Custom hook for scenario analysis
export const useScenarioAnalysis = () => {
  const [state, setState] = useState<UseApiState<AnalysisResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  const analyzeScenario = async (request: AnalysisRequest) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const data = await ApiService.analyzeScenario(request);
      setState({ data, loading: false, error: null });
      return data;
    } catch (error) {
      const apiError = handleApiError(error);
      setState({ data: null, loading: false, error: apiError.message });
      throw apiError;
    }
  };

  return { ...state, analyzeScenario };
};

// Custom hook for rule execution
export const useRuleExecution = () => {
  const [state, setState] = useState<UseApiState<ExecutionResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  const executeRules = async (request: ExecutionRequest) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const data = await ApiService.executeRules(request);
      setState({ data, loading: false, error: null });
      return data;
    } catch (error) {
      const apiError = handleApiError(error);
      setState({ data: null, loading: false, error: apiError.message });
      throw apiError;
    }
  };

  return { ...state, executeRules };
};

// Custom hook for chat functionality
export const useChat = () => {
  const [state, setState] = useState<UseApiState<ChatResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  const sendMessage = async (request: ChatRequest) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const data = await ApiService.chatWithAgent(request);
      setState({ data, loading: false, error: null });
      return data;
    } catch (error) {
      const apiError = handleApiError(error);
      setState({ data: null, loading: false, error: apiError.message });
      throw apiError;
    }
  };

  return { ...state, sendMessage };
};

// Custom hook for rule search and filtering
export const useRuleSearch = () => {
  const [state, setState] = useState<UseApiState<BusinessRule[]>>({
    data: null,
    loading: false,
    error: null,
  });

  const searchRules = useCallback(async (query: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const data = await ApiService.searchRules(query);
      setState({ data, loading: false, error: null });
      return data;
    } catch (error) {
      const apiError = handleApiError(error);
      setState({ data: null, loading: false, error: apiError.message });
      throw apiError;
    }
  }, []);

  const filterRules = useCallback(async (filters: {
    domain?: string;
    category?: string;
    priority?: number;
    search?: string;
  }) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const data = await ApiService.filterRules(filters);
      setState({ data, loading: false, error: null });
      return data;
    } catch (error) {
      const apiError = handleApiError(error);
      setState({ data: null, loading: false, error: apiError.message });
      throw apiError;
    }
  }, []);

  return { ...state, searchRules, filterRules };
};

// Generic debounced hook
export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// Hook for local storage
export const useLocalStorage = <T>(key: string, initialValue: T) => {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue] as const;
};