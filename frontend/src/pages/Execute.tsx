import React, { useState } from 'react';
import { Layout } from '../components/layout';
import { Card, Button, LoadingSpinner, Alert, Badge } from '../components/ui';
import { useBusinessRules } from '../hooks/useApi';
import { BusinessRule, ExecutionRequest, ExecutionResponse, AnalysisResponse, AnalysisRequest } from '../types';
import apiService from '../services/api';
import { getPriorityLabel, getPriorityColor, capitalize } from '../utils';

// Tree node component for rules hierarchy
const RuleTreeNode: React.FC<{
  title: string;
  rules: BusinessRule[];
  selectedRule: BusinessRule | null;
  onRuleSelect: (rule: BusinessRule) => void;
  isExpanded: boolean;
  onToggle: () => void;
}> = ({ title, rules, selectedRule, onRuleSelect, isExpanded, onToggle }) => {
  return (
    <div className="border rounded-lg mb-2 shadow-sm">
      <div 
        className="flex items-center justify-between p-3 bg-gradient-to-r from-gray-50 to-gray-100 hover:from-gray-100 hover:to-gray-200 cursor-pointer border-b transition-colors duration-150"
        onClick={onToggle}
      >
        <h3 className="font-semibold text-gray-900">{title}</h3>
        <div className="flex items-center gap-2">
          <Badge className="bg-blue-100 text-blue-800 text-xs">{rules.length}</Badge>
          <span className={`transition-transform duration-200 text-gray-500 ${isExpanded ? 'rotate-90' : ''}`}>
            ▶
          </span>
        </div>
      </div>
      
      {isExpanded && (
        <div className="p-2 bg-white">
          {rules.map((rule) => (
            <div
              key={rule.id}
              onClick={() => onRuleSelect(rule)}
              className={`p-3 rounded-lg cursor-pointer transition-all duration-150 mb-1 ${
                selectedRule?.id === rule.id
                  ? 'bg-blue-50 border-2 border-blue-400 shadow-sm'
                  : 'hover:bg-gray-50 border border-gray-200 hover:border-gray-300 hover:shadow-sm'
              }`}
            >
              <div className="flex items-start justify-between mb-1">
                <div>
                  <h4 className="font-medium text-sm text-gray-900">{rule.id}</h4>
                  <p className="text-xs text-gray-600 font-medium">{rule.name}</p>
                </div>
                <Badge className={getPriorityColor(rule.priority)}>
                  {getPriorityLabel(rule.priority)}
                </Badge>
              </div>
              <p className="text-xs text-gray-500 truncate mb-1">{rule.description}</p>
              <div className="flex gap-1 mt-1">
                <Badge className="bg-gray-100 text-gray-700 text-xs">{capitalize(rule.category)}</Badge>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const Execute: React.FC = () => {
  const [selectedRule, setSelectedRule] = useState<BusinessRule | null>(null);
  const [parametersJson, setParametersJson] = useState('{}');
  const [context, setContext] = useState('');
  const [scenario, setScenario] = useState('');
  const [executeResult, setExecuteResult] = useState<ExecutionResponse | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    finance: true,
    compliance: true,
    inventory: true,
    customer_service: true,
  });
  
  const { data: rules, loading: rulesLoading, error: rulesError } = useBusinessRules();
  
  // Group rules by domain
  const rulesByDomain = rules?.reduce((acc, rule) => {
    const domain = rule.domain.toLowerCase();
    if (!acc[domain]) {
      acc[domain] = [];
    }
    acc[domain].push(rule);
    return acc;
  }, {} as Record<string, BusinessRule[]>) || {};

  const domainLabels: Record<string, string> = {
    finance: '💰 Finance Rules',
    compliance: '📋 Compliance Rules',
    inventory: '📦 Inventory Rules',
    customer_service: '🎧 Customer Service Rules',
  };
  
  const generateSampleScenario = (rule: BusinessRule): string => {
    // Generate natural language scenarios that trigger specific rules - from Postman collection
    const scenarioExamples: Record<string, string> = {
      'LOAN_001': 'A customer with a credit score of 720 is applying for a loan of $50,000',
      'LOAN_002': 'A customer with a credit score of 650 and annual income of $75,000 has a debt-to-income ratio of 0.35',
      'LOAN_003': 'A customer with a credit score of 800 is applying for a $25,000 loan with excellent payment history',
      'LOAN_004': 'A customer is applying for a $150,000 loan against a property worth $200,000 with a down payment of $40,000',
      'GDPR_001': 'I have personal data that is 800 days old and the retention period is 730 days',
      'GDPR_002': 'User consent was given on 2023-01-01 with a validity period of 365 days and today is 2024-09-25',
      'GDPR_003': 'A user has submitted a verified data deletion request and wants their personal information completely removed',
      'SOX_001': 'An employee is trying to access financial data classification records without proper authorization',
      'PCI_001': 'Payment data is stored without encryption and needs to be secured according to PCI compliance',
      'INV_001': 'Product PROD_12345 has current stock of 25 units but minimum threshold is 50 units',
      'INV_002': 'Critical product has stock level of 5 units remaining and needs emergency reorder to avoid stockout',
      'INV_003': 'Warehouse has excess inventory that exceeds storage capacity and needs clearance action',
      'INV_004': 'Need to adjust inventory levels for seasonal demand changes during holiday season',
      'INV_005': 'Products in inventory are approaching their expiry dates within 30 days and need immediate action',
      'SUPP_001': 'VIP customer has submitted a support request and needs priority handling with dedicated agent',
      'SUPP_002': 'Complex technical issue requires escalation to specialized technical team for resolution',
      'SUPP_003': 'A high severity issue has response time of 48 hours but SLA requires 24 hours during after hours',
      'SUPP_004': 'Customer has a billing dispute over incorrect charges that needs specialized financial team review'
    };

    return scenarioExamples[rule.id] || `Execute ${rule.name} rule for business scenario`;
  };

  const generateSampleContext = (rule: BusinessRule): string => {
    // Context examples from Postman collection
    const contextExamples: Record<string, object> = {
      'LOAN_001': { domain: "finance", category: "loan_approval", customer_id: "CUST_12345", application_id: "APP_98765" },
      'LOAN_002': { domain: "finance", category: "loan_approval", customer_id: "CUST_12346", application_id: "APP_98766" },
      'LOAN_003': { domain: "finance", category: "loan_approval", customer_id: "CUST_12347", application_id: "APP_98767" },
      'LOAN_004': { domain: "finance", category: "loan_approval", customer_id: "CUST_12348", application_id: "APP_98768" },
      'GDPR_001': { domain: "compliance", category: "data_protection", regulation: "GDPR", user_location: "EU" },
      'GDPR_002': { domain: "compliance", category: "data_protection", regulation: "GDPR", user_location: "EU" },
      'GDPR_003': { domain: "compliance", category: "data_protection", regulation: "GDPR", user_location: "EU" },
      'SOX_001': { domain: "compliance", category: "data_protection", regulation: "SOX", user_role: "employee" },
      'PCI_001': { domain: "compliance", category: "data_protection", regulation: "PCI_DSS", data_classification: "payment" },
      'INV_001': { domain: "inventory", category: "stock_management", warehouse_id: "WH_001", location: "NYC" },
      'INV_002': { domain: "inventory", category: "stock_management", warehouse_id: "WH_001", urgency: "critical" },
      'INV_003': { domain: "inventory", category: "stock_management", warehouse_id: "WH_001", capacity_utilization: 0.95 },
      'INV_004': { domain: "inventory", category: "stock_management", season: "holiday", expected_demand_increase: 1.5 },
      'INV_005': { domain: "inventory", category: "stock_management", expiry_warning_days: 30, product_type: "perishable" },
      'SUPP_001': { domain: "customer_service", category: "support_routing", customer_id: "CUST_VIP_001", customer_tier: "VIP", channel: "phone" },
      'SUPP_002': { domain: "customer_service", category: "support_routing", customer_id: "CUST_12349", issue_type: "technical", complexity: "high" },
      'SUPP_003': { domain: "customer_service", category: "support_routing", customer_id: "CUST_12350", issue_severity: "high", business_hours: false },
      'SUPP_004': { domain: "customer_service", category: "support_routing", customer_id: "CUST_12351", issue_type: "billing_dispute", dispute_amount: 245.99 }
    };

    return JSON.stringify(contextExamples[rule.id] || { 
      domain: rule.domain,
      category: rule.category,
      request_id: "REQ_001"
    }, null, 2);
  };

  const handleRuleSelect = (rule: BusinessRule) => {
    setSelectedRule(rule);
    setScenario(generateSampleScenario(rule));
    setContext(generateSampleContext(rule));
    setParametersJson('{}'); // Always use explicit rule_ids - no auto-discovery
    setExecuteResult(null);
    setAnalysisResult(null);
    setError(null);
  };

  const toggleSection = (domain: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [domain]: !prev[domain]
    }));
  };

  const handleExecute = async () => {
    if (!selectedRule) return;
    
    setLoading(true);
    setError(null);
    setAnalysisResult(null);
    
    try {
      let parsedContext = {};
      if (context.trim()) {
        try {
          parsedContext = JSON.parse(context);
        } catch (e) {
          throw new Error('Invalid JSON in context field');
        }
      }

      // First, analyze the scenario to get confidence scores
      console.log('Analyzing scenario for confidence score...');
      const analysisRequest: AnalysisRequest = {
        scenario: scenario || generateSampleScenario(selectedRule)
      };
      
      // Only include context if it's not empty
      if (Object.keys(parsedContext).length > 0) {
        analysisRequest.context = parsedContext;
      }
      
      const analysis = await apiService.analyzeScenario(analysisRequest);
      console.log('Analysis result:', analysis);
      setAnalysisResult(analysis);
      
      // Then execute the rule with explicit rule_ids
      const request: ExecutionRequest = {
        scenario: scenario || generateSampleScenario(selectedRule),
        parameters: {}, // Let the backend infer parameters from the scenario
        rule_ids: [selectedRule.id] // CRITICAL: Always specify rule_ids explicitly
      };
      
      // Only include context if it's not empty
      if (Object.keys(parsedContext).length > 0) {
        request.context = parsedContext;
      }
      
      console.log('Executing rule with request:', request);
      const result = await apiService.executeRules(request);
      console.log('Execution result:', result);
      setExecuteResult(result);
      
    } catch (err) {
      console.error('Execution error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to execute rule';
      setError(errorMessage);
      setExecuteResult(null);
    } finally {
      setLoading(false);
    }
  };

  const renderExecutionResults = () => {
    if (!executeResult) return null;

    const getStatusBadgeColor = (status: string) => {
      switch (status.toLowerCase()) {
        case 'completed': return 'bg-green-100 text-green-800';
        case 'failed': return 'bg-red-100 text-red-800';
        case 'partial': return 'bg-yellow-100 text-yellow-800';
        case 'skipped': return 'bg-gray-100 text-gray-800';
        default: return 'bg-blue-100 text-blue-800';
      }
    };

    const getConfidenceColor = (confidence: number) => {
      if (confidence >= 0.8) return 'bg-green-100 text-green-800';
      if (confidence >= 0.6) return 'bg-yellow-100 text-yellow-800';
      if (confidence >= 0.4) return 'bg-orange-100 text-orange-800';
      return 'bg-red-100 text-red-800';
    };

    return (
      <div className="space-y-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <h4 className="font-semibold text-blue-900 mb-2">Execution Summary</h4>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
            <div>
              <span className="text-blue-600">Plan ID:</span>
              <p className="font-mono text-xs">{executeResult.execution_plan_id}</p>
            </div>
            <div>
              <span className="text-blue-600">Status:</span>
              <p className={`inline-block px-2 py-1 rounded text-xs font-medium ${getStatusBadgeColor(executeResult.overall_status)}`}>
                {executeResult.overall_status.toUpperCase()}
              </p>
            </div>
            <div>
              <span className="text-blue-600">Rules:</span>
              <p>{executeResult.successful_rules || 0}/{executeResult.total_rules || 0}</p>
            </div>
            <div>
              <span className="text-blue-600">Time:</span>
              <p>{executeResult.execution_time ? (executeResult.execution_time * 1000).toFixed(2) + 'ms' : 'N/A'}</p>
            </div>
            {analysisResult && (
              <div>
                <span className="text-blue-600">Confidence:</span>
                <p className={`inline-block px-2 py-1 rounded text-xs font-medium ${getConfidenceColor(analysisResult.overall_confidence)}`}>
                  {(analysisResult.overall_confidence * 100).toFixed(1)}%
                </p>
              </div>
            )}
          </div>
          {executeResult.message && (
            <div className="mt-3">
              <span className="text-blue-600">Message:</span>
              <p className="text-gray-700">{executeResult.message}</p>
            </div>
          )}
        </div>

        {analysisResult && (
          <div className="bg-purple-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-900 mb-2">Analysis Details</h4>
            <div className="space-y-3 text-sm">
              <div>
                <span className="text-purple-600">Overall Confidence:</span>
                <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${getConfidenceColor(analysisResult.overall_confidence)}`}>
                  {(analysisResult.overall_confidence * 100).toFixed(1)}%
                </span>
              </div>
              <div>
                <span className="text-purple-600">Decision Outcome:</span>
                <p className="text-gray-700 mt-1">{analysisResult.decision_outcome}</p>
              </div>
              {analysisResult.reasoning && (
                <div>
                  <span className="text-purple-600">Reasoning:</span>
                  <p className="text-gray-700 mt-1 whitespace-pre-wrap">{analysisResult.reasoning}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {executeResult.results && executeResult.results.length > 0 && (
          <div className="space-y-3">
            <h4 className="font-semibold text-gray-900">Rule Results</h4>
            {executeResult.results.map((result, index) => {
              // Find the corresponding rule in analysis for confidence score
              const analysisRule = analysisResult?.applicable_rules?.find(rule => rule.id === result.rule_id);
              
              return (
                <Card key={index} className="border-l-4 border-l-blue-500">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h5 className="font-semibold text-gray-900">{result.rule_name}</h5>
                      <p className="text-sm text-gray-600">ID: {result.rule_id}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusBadgeColor(result.status)}`}>
                        {result.status.toUpperCase()}
                      </span>
                      {analysisRule && (
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getConfidenceColor(analysisRule.confidence || 0)}`}>
                          {((analysisRule.confidence || 0) * 100).toFixed(1)}%
                        </span>
                      )}
                      <span className="text-xs text-gray-500">
                        {result.duration ? (result.duration * 1000).toFixed(2) + 'ms' : 'N/A'}
                      </span>
                    </div>
                  </div>

                  {analysisRule?.reasoning && (
                    <div className="bg-purple-50 p-3 rounded mb-3">
                      <h6 className="font-medium text-purple-700 mb-2">Rule Analysis:</h6>
                      <p className="text-sm text-purple-600">{analysisRule.reasoning}</p>
                    </div>
                  )}

                  {result.output && (
                    <div className="bg-gray-50 p-3 rounded">
                      <h6 className="font-medium text-gray-700 mb-2">Output:</h6>
                      <pre className="text-sm text-gray-600 whitespace-pre-wrap overflow-x-auto">
                        {JSON.stringify(result.output, null, 2)}
                      </pre>
                    </div>
                  )}

                  {result.error && (
                    <Alert type="error" className="mt-3">
                      <strong>Error:</strong> {result.error}
                    </Alert>
                  )}
                </Card>
              );
            })}
          </div>
        )}
      </div>
    );
  };

  if (rulesLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      </Layout>
    );
  }

  if (rulesError) {
    return (
      <Layout>
        <Alert type="error">
          Failed to load rules: {rulesError}
        </Alert>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Execute Rules</h1>
          <p className="mt-2 text-gray-600">
            Select rules from the tree structure and execute them with custom scenarios
          </p>
        </div>

        <div className="flex gap-6 h-screen">
          {/* Left Side - Rules Tree */}
          <div className="w-1/3 border-r pr-6 bg-gray-50">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 px-2">Business Rules</h2>
            <div className="space-y-2 overflow-y-auto bg-white rounded-lg border p-3" style={{ maxHeight: 'calc(100vh - 200px)' }}>
              {Object.entries(rulesByDomain).map(([domain, domainRules]) => (
                <RuleTreeNode
                  key={domain}
                  title={domainLabels[domain] || capitalize(domain)}
                  rules={domainRules}
                  selectedRule={selectedRule}
                  onRuleSelect={handleRuleSelect}
                  isExpanded={expandedSections[domain]}
                  onToggle={() => toggleSection(domain)}
                />
              ))}
            </div>
          </div>

          {/* Right Side - Execution Panel */}
          <div className="w-2/3 space-y-6 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 200px)' }}>
            {selectedRule ? (
              <>
                {/* Rule Details */}
                <Card>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Selected Rule Details</h2>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h3 className="font-medium text-gray-700 mb-2">Rule Information</h3>
                      <div className="space-y-2 text-sm">
                        <div><strong>ID:</strong> {selectedRule.id}</div>
                        <div><strong>Name:</strong> {selectedRule.name}</div>
                        <div><strong>Domain:</strong> {capitalize(selectedRule.domain)}</div>
                        <div><strong>Category:</strong> {capitalize(selectedRule.category)}</div>
                        <div className="flex items-center gap-2">
                          <strong>Priority:</strong> 
                          <Badge className={getPriorityColor(selectedRule.priority)}>
                            {getPriorityLabel(selectedRule.priority)}
                          </Badge>
                        </div>
                      </div>
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-700 mb-2">Description</h3>
                      <p className="text-sm text-gray-600">{selectedRule.description}</p>
                      
                      {selectedRule.condition && (
                        <div className="mt-3">
                          <h4 className="font-medium text-gray-700 text-sm">Condition</h4>
                          <code className="block p-2 bg-gray-100 rounded text-xs mt-1">
                            {selectedRule.condition}
                          </code>
                        </div>
                      )}
                    </div>
                  </div>
                </Card>

                {/* Execution Form */}
                <Card>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Execute Rule</h2>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Business Scenario *
                      </label>
                      <textarea
                        value={scenario}
                        onChange={(e) => setScenario(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white shadow-sm"
                        rows={3}
                        placeholder="Describe the business situation that should trigger this rule..."
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Describe the business scenario in natural language for rule execution.
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Context (JSON, Optional)
                      </label>
                      <textarea
                        value={context}
                        onChange={(e) => setContext(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 font-mono text-sm bg-gray-50 shadow-sm"
                        rows={4}
                        placeholder="Enter execution context as JSON..."
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Manual Parameters (JSON, Advanced)
                      </label>
                      <textarea
                        value={parametersJson}
                        onChange={(e) => setParametersJson(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 font-mono text-sm bg-gray-50 shadow-sm"
                        rows={4}
                        placeholder="Optional: Override with specific parameters as JSON..."
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Leave empty to let the system infer parameters from the scenario.
                      </p>
                    </div>

                    <Button 
                      onClick={handleExecute} 
                      disabled={loading || !selectedRule || !scenario.trim()}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg shadow-sm transition-colors duration-200"
                    >
                      {loading ? (
                        <div className="flex items-center justify-center gap-2">
                          <LoadingSpinner size="sm" />
                          <span>Executing...</span>
                        </div>
                      ) : (
                        'Execute Rule'
                      )}
                    </Button>

                    {error && (
                      <Alert type="error">
                        {error}
                      </Alert>
                    )}
                  </div>
                </Card>

                {/* Execution Results */}
                {executeResult && (
                  <Card>
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">Execution Results</h2>
                    {renderExecutionResults()}
                  </Card>
                )}
              </>
            ) : (
              <Card>
                <div className="text-center py-12">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Rule</h3>
                  <p className="text-gray-600">
                    Choose a rule from the tree structure on the left to view details and execute it.
                  </p>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Execute;