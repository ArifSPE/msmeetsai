import React, { useState } from 'react';
import { Layout } from '../components/layout';
import { Card, Button, LoadingSpinner, Alert, Badge } from '../components/ui';
import { useScenarioAnalysis } from '../hooks/useApi';
import { AnalysisRequest } from '../types';
import { getPriorityLabel, getPriorityColor, capitalize } from '../utils';

const Analyze: React.FC = () => {
  const [scenario, setScenario] = useState('');
  const [context, setContext] = useState('');
  const [domain, setDomain] = useState('');
  
  const { data: analysis, loading, error, analyzeScenario } = useScenarioAnalysis();
  
  const handleAnalyze = async () => {
    if (!scenario.trim()) return;
    
    try {
      const contextObj = context.trim() ? JSON.parse(context) : {};
      const analysisRequest: AnalysisRequest = {
        scenario: scenario.trim(),
      };
      
      // Only include context if it's not empty
      if (Object.keys(contextObj).length > 0) {
        analysisRequest.context = contextObj;
      }
      
      // Only include domain if it's specified
      if (domain) {
        analysisRequest.domain = domain;
      }
      
      await analyzeScenario(analysisRequest);
    } catch (err) {
      console.error('Analysis error:', err);
    }
  };
  
  const handleExampleScenario = (exampleScenario: string) => {
    setScenario(exampleScenario);
  };
  
  const exampleScenarios = [
    'Customer wants a loan of $50,000 with a credit score of 720',
    'Employee is requesting access to sensitive financial data',
    'Inventory level for product XYZ has fallen below 100 units',
    'Customer complaint about delayed shipment needs to be escalated',
    'New customer registration from a high-risk country',
    'Payment of $10,000 needs to be processed urgently',
  ];
  
  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Scenario Analysis</h1>
          <p className="mt-1 text-gray-600">
            Analyze business scenarios and get rule recommendations from the agentic system
          </p>
        </div>
        
        {/* Input Form */}
        <Card title="Analyze Business Scenario">
          <div className="space-y-4">
            {/* Scenario Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Business Scenario *
              </label>
              <textarea
                value={scenario}
                onChange={(e) => setScenario(e.target.value)}
                placeholder="Describe the business scenario you want to analyze..."
                rows={4}
                className="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent focus:bg-white transition-colors duration-200 resize-none"
                required
              />
            </div>
            
            {/* Optional Context */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Context (JSON, optional)
              </label>
              <textarea
                value={context}
                onChange={(e) => setContext(e.target.value)}
                placeholder='{"amount": 50000, "creditScore": 720, "customerType": "premium"}'
                rows={3}
                className="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent focus:bg-white transition-colors duration-200 resize-none font-mono text-sm"
              />
            </div>
            
            {/* Optional Domain */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Domain (optional)
              </label>
              <select
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                className="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent focus:bg-white transition-colors duration-200"
              >
                <option value="">All Domains</option>
                <option value="finance">Finance</option>
                <option value="inventory">Inventory</option>
                <option value="compliance">Compliance</option>
                <option value="customer_service">Customer Service</option>
              </select>
            </div>
            
            {/* Action Buttons */}
            <div className="flex space-x-3">
              <Button
                onClick={handleAnalyze}
                loading={loading}
                disabled={!scenario.trim() || loading}
                className="flex-1"
              >
                Analyze Scenario
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setScenario('');
                  setContext('');
                  setDomain('');
                }}
              >
                Clear
              </Button>
            </div>
          </div>
        </Card>
        
        {/* Example Scenarios */}
        <Card title="Example Scenarios">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {exampleScenarios.map((example, index) => (
              <button
                key={index}
                onClick={() => handleExampleScenario(example)}
                className="text-left p-3 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
              >
                <div className="text-sm text-gray-700">{example}</div>
              </button>
            ))}
          </div>
        </Card>
        
        {/* Results */}
        {error && (
          <Alert type="error" title="Analysis Error">
            {error}
          </Alert>
        )}
        
        {analysis && (
          <div className="space-y-6">
            {/* Analysis Summary */}
            <Card title="Analysis Results">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Status</span>
                  <Badge variant="status" status={analysis.decision_outcome}>
                    {analysis.decision_outcome}
                  </Badge>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <div className="text-sm text-gray-600">Applicable Rules</div>
                    <div className="text-2xl font-bold text-gray-900">
                      {analysis.applicable_rules?.length || 0}
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <div className="text-sm text-gray-600">Confidence Score</div>
                    <div className="text-2xl font-bold text-gray-900">
                      {((analysis.overall_confidence || 0) * 100).toFixed(1)}%
                    </div>
                    {/* Debug info */}
                    <div className="text-xs text-gray-400 mt-1">
                      Raw: {analysis.overall_confidence} | Type: {typeof analysis.overall_confidence}
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <div className="text-sm text-gray-600">Recommendations</div>
                    <div className="text-2xl font-bold text-gray-900">
                      {analysis.metadata?.recommended_actions?.length || 0}
                    </div>
                  </div>
                </div>
                
                {/* AI Reasoning */}
                {analysis.reasoning && (
                  <div className="border-t pt-4">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">AI Reasoning</h4>
                    <div className="text-sm text-gray-700 bg-blue-50 p-3 rounded-lg">
                      {analysis.reasoning}
                    </div>
                  </div>
                )}
                
                {analysis.metadata?.overall_assessment && (
                  <div className="border-t pt-4">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Overall Assessment</h4>
                    <div className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">
                      {analysis.metadata.overall_assessment}
                    </div>
                  </div>
                )}
              </div>
            </Card>
            
            {/* Applicable Rules */}
            {analysis.applicable_rules && analysis.applicable_rules.length > 0 && (
              <Card title="Applicable Rules">
                <div className="space-y-4">
                  {analysis.applicable_rules.map((rule) => (
                    <div
                      key={rule.id}
                      className="border border-gray-200 rounded-lg p-4"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900 mb-1">
                            {rule.name}
                          </h3>
                          <p className="text-sm text-gray-600 mb-2">
                            {rule.description}
                          </p>
                          <div className="flex items-center space-x-2">
                            <Badge variant="default">
                              {capitalize(rule.domain)}
                            </Badge>
                            <Badge variant="default">
                              {capitalize(rule.category.replace('_', ' '))}
                            </Badge>
                            <Badge
                              variant="priority"
                              className={getPriorityColor(rule.priority)}
                            >
                              {getPriorityLabel(rule.priority)}
                            </Badge>
                          </div>
                        </div>
                        <div className="flex flex-col text-xs text-gray-500 ml-4 text-right">
                          <div>Priority: {rule.priority}</div>
                          {rule.confidence !== null && rule.confidence !== undefined && (
                            <div className="mt-1">
                              <span className="font-medium">Confidence:</span>{' '}
                              <span className={`px-2 py-1 rounded text-xs font-medium ${
                                rule.confidence >= 0.8 ? 'bg-green-100 text-green-800' :
                                rule.confidence >= 0.6 ? 'bg-yellow-100 text-yellow-800' :
                                rule.confidence >= 0.4 ? 'bg-orange-100 text-orange-800' :
                                'bg-red-100 text-red-800'
                              }`}>
                                {(rule.confidence * 100).toFixed(1)}%
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      {/* Rule Condition */}
                      {rule.condition && (
                        <div className="mt-3 border-t pt-3">
                          <label className="text-xs font-medium text-gray-500">CONDITION</label>
                          <div className="mt-1">
                            <div className="text-xs bg-gray-50 p-2 rounded font-mono">
                              {rule.condition}
                            </div>
                          </div>
                        </div>
                      )}
                      
                      {/* Rule Action */}
                      {rule.action && (
                        <div className="mt-3 border-t pt-3">
                          <label className="text-xs font-medium text-gray-500">ACTION</label>
                          <div className="mt-1">
                            <div className="text-xs bg-blue-50 p-2 rounded font-mono">
                              {rule.action}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </Card>
            )}
            
            {/* Recommendations */}
            {analysis.metadata?.recommended_actions && analysis.metadata.recommended_actions.length > 0 && (
              <Card title="Recommendations">
                <div className="space-y-3">
                  {analysis.metadata.recommended_actions.map((recommendation, index) => (
                    <div
                      key={index}
                      className="flex items-start p-3 bg-green-50 border border-green-200 rounded-lg"
                    >
                      <div className="text-green-600 mr-3 mt-0.5">
                        <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </div>
                      <div className="text-sm text-green-800">{recommendation}</div>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>
        )}
        
        {loading && (
          <Card title="Analyzing...">
            <div className="flex items-center justify-center py-8">
              <LoadingSpinner />
              <span className="ml-3 text-gray-600">
                Analyzing scenario and finding applicable rules...
              </span>
            </div>
          </Card>
        )}
      </div>
    </Layout>
  );
};

export default Analyze;