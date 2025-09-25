import React from 'react';
import { Layout } from '../components/layout';
import { Card, Badge, LoadingSpinner, Alert } from '../components/ui';
import { useSystemHealth, useBusinessRules } from '../hooks/useApi';
import { formatNumber } from '../utils';

const Dashboard: React.FC = () => {
  const { data: health, loading: healthLoading, error: healthError } = useSystemHealth();
  const { data: rules, loading: rulesLoading, error: rulesError } = useBusinessRules();
  
  // Calculate statistics
  const stats = React.useMemo(() => {
    if (!rules || !Array.isArray(rules) || rules.length === 0) {
      return {
        domainStats: {},
        categoryStats: {},
        priorityStats: {},
        totalRules: 0,
        activeRules: 0,
      };
    }
    
    const domainStats = rules.reduce((acc, rule) => {
      acc[rule.domain] = (acc[rule.domain] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    const categoryStats = rules.reduce((acc, rule) => {
      acc[rule.category] = (acc[rule.category] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    const priorityStats = rules.reduce((acc, rule) => {
      const priority = rule.priority >= 8 ? 'Critical' : 
                     rule.priority >= 5 ? 'High' : 
                     rule.priority >= 3 ? 'Medium' : 'Low';
      acc[priority] = (acc[priority] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    return {
      domainStats: domainStats,
      categoryStats: categoryStats,
      priorityStats: priorityStats,
      totalRules: rules.length,
      activeRules: rules.length, // All rules are considered active since there's no status field
    };
  }, [rules]);
  
  if (healthError) {
    return (
      <Layout title="Dashboard">
        <Alert type="error" title="Connection Error">
          Unable to connect to the backend service. Please ensure the API server is running.
        </Alert>
      </Layout>
    );
  }
  
  return (
    <Layout title="Dashboard">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-gray-600">
            Overview of your agentic business rules system
          </p>
        </div>
        
        {/* System Health */}
        <Card title="System Health">
          {healthLoading ? (
            <LoadingSpinner />
          ) : health ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Status</span>
                <Badge variant="status" status={health.status}>
                  {health.status.charAt(0).toUpperCase() + health.status.slice(1)}
                </Badge>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">Total Rules</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {formatNumber(health.system_info.total_rules)}
                  </div>
                </div>
                
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">Domains</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {health.system_info.domains.length}
                  </div>
                </div>
                
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">Categories</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {health.system_info.categories.length}
                  </div>
                </div>
                
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">Vector Points</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {formatNumber(health.system_info.vector_db_info.points_count)}
                  </div>
                </div>
              </div>
              
              {/* Vector DB Info */}
              <div className="border-t pt-4">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Vector Database</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Collection:</span>
                    <span className="ml-2 font-mono">{health.system_info.vector_db_info.collection_name}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Vector Size:</span>
                    <span className="ml-2 font-mono">{health.system_info.vector_db_info.vector_size}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Distance Metric:</span>
                    <span className="ml-2 font-mono">{health.system_info.vector_db_info.distance}</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-gray-500">No health data available</div>
          )}
        </Card>
        
        {/* Rules Statistics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Domain Distribution */}
          <Card title="Rules by Domain">
            {rulesLoading ? (
              <LoadingSpinner />
            ) : stats ? (
              <div className="space-y-3">
                {Object.entries(stats.domainStats).map(([domain, count]) => (
                  <div key={domain} className="flex items-center justify-between">
                    <span className="text-sm font-medium capitalize">{domain}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600">{count as number}</span>
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-primary-600 h-2 rounded-full"
                          style={{
                            width: `${((count as number) / stats.totalRules) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-gray-500">No rules data available</div>
            )}
          </Card>
          
          {/* Category Distribution */}
          <Card title="Rules by Category">
            {rulesLoading ? (
              <LoadingSpinner />
            ) : stats ? (
              <div className="space-y-3">
                {Object.entries(stats.categoryStats).map(([category, count]) => (
                  <div key={category} className="flex items-center justify-between">
                    <span className="text-sm font-medium capitalize">{category.replace('_', ' ')}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600">{count as number}</span>
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-secondary-600 h-2 rounded-full"
                          style={{
                            width: `${((count as number) / stats.totalRules) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-gray-500">No rules data available</div>
            )}
          </Card>
          
          {/* Priority Distribution */}
          <Card title="Rules by Priority">
            {rulesLoading ? (
              <LoadingSpinner />
            ) : stats ? (
              <div className="space-y-3">
                {Object.entries(stats.priorityStats).map(([priority, count]) => (
                  <div key={priority} className="flex items-center justify-between">
                    <span className="text-sm font-medium">{priority}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600">{count as number}</span>
                      <Badge
                        variant="priority"
                        className={
                          priority === 'Critical' ? 'bg-red-100 text-red-800' :
                          priority === 'High' ? 'bg-orange-100 text-orange-800' :
                          priority === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }
                      >
                        {count as number}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-gray-500">No rules data available</div>
            )}
          </Card>
        </div>
        
        {/* Quick Actions */}
        <Card title="Quick Actions">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <a
              href="/rules"
              className="group bg-gradient-to-r from-primary-50 to-primary-100 p-4 rounded-lg border border-primary-200 hover:from-primary-100 hover:to-primary-200 transition-colors"
            >
              <div className="text-primary-600 mb-2">
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="font-medium text-gray-900 group-hover:text-primary-700">View Rules</h3>
              <p className="text-sm text-gray-600 mt-1">Browse and manage business rules</p>
            </a>
            
            <a
              href="/analyze"
              className="group bg-gradient-to-r from-green-50 to-green-100 p-4 rounded-lg border border-green-200 hover:from-green-100 hover:to-green-200 transition-colors"
            >
              <div className="text-green-600 mb-2">
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="font-medium text-gray-900 group-hover:text-green-700">Analyze Scenario</h3>
              <p className="text-sm text-gray-600 mt-1">Get rule recommendations</p>
            </a>
            
            <a
              href="/execute"
              className="group bg-gradient-to-r from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200 hover:from-purple-100 hover:to-purple-200 transition-colors"
            >
              <div className="text-purple-600 mb-2">
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="font-medium text-gray-900 group-hover:text-purple-700">Execute Rules</h3>
              <p className="text-sm text-gray-600 mt-1">Run business rule scenarios</p>
            </a>
            
            <a
              href="/chat"
              className="group bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200 hover:from-blue-100 hover:to-blue-200 transition-colors"
            >
              <div className="text-blue-600 mb-2">
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="font-medium text-gray-900 group-hover:text-blue-700">Chat Assistant</h3>
              <p className="text-sm text-gray-600 mt-1">Ask questions about rules</p>
            </a>
          </div>
        </Card>
      </div>
    </Layout>
  );
};

export default Dashboard;