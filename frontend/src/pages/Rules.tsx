import React, { useState, useEffect } from 'react';
import { Layout } from '../components/layout';
import { Card, Badge, LoadingSpinner, Alert, Input, Button } from '../components/ui';
import { useBusinessRules, useDomains, useCategories, useRuleSearch } from '../hooks/useApi';
import { useDebounce } from '../hooks/useApi';
import { BusinessRule } from '../types';
import { getPriorityLabel, getPriorityColor, capitalize } from '../utils';

const Rules: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedRule, setSelectedRule] = useState<BusinessRule | null>(null);
  
  const debouncedSearch = useDebounce(searchQuery, 300);
  
  const { data: allRules, loading: allRulesLoading, error: rulesError } = useBusinessRules();
  const { data: domains, loading: domainsLoading } = useDomains();
  const { data: categories, loading: categoriesLoading } = useCategories();
  const { data: searchResults, loading: searchLoading, searchRules, filterRules } = useRuleSearch();
  
  // Filtered rules based on current filters
  const [filteredRules, setFilteredRules] = useState<BusinessRule[]>([]);
  const [filterLoading, setFilterLoading] = useState(false);
  
  useEffect(() => {
    const applyFilters = async () => {
      setFilterLoading(true);
      try {
        if (debouncedSearch || selectedDomain || selectedCategory) {
          // Apply filters
          const results = await filterRules({
            search: debouncedSearch || undefined,
            domain: selectedDomain || undefined,
            category: selectedCategory || undefined,
          });
          setFilteredRules(results);
        } else {
          // No filters, show all rules
          setFilteredRules(allRules || []);
        }
      } catch (error) {
        console.error('Filter error:', error);
        setFilteredRules(allRules || []);
      } finally {
        setFilterLoading(false);
      }
    };

    // Always apply filters when allRules is available or filters change
    applyFilters();
  }, [debouncedSearch, selectedDomain, selectedCategory, allRules, filterRules]);
  
  const clearFilters = () => {
    setSearchQuery('');
    setSelectedDomain('');
    setSelectedCategory('');
  };
  
  if (rulesError) {
    return (
      <Layout>
        <Alert type="error" title="Error Loading Rules">
          {rulesError}
        </Alert>
      </Layout>
    );
  }
  
  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Business Rules</h1>
            <p className="mt-1 text-gray-600">
              {filteredRules.length} of {allRules?.length || 0} rules
            </p>
          </div>
          <Button onClick={clearFilters} variant="outline">
            Clear Filters
          </Button>
        </div>
        
        {/* Filters */}
        <Card title="Filters">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <Input
              placeholder="Search rules..."
              value={searchQuery}
              onChange={setSearchQuery}
              className="md:col-span-1"
            />
            
            {/* Domain Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Domain
              </label>
              <select
                value={selectedDomain}
                onChange={(e) => setSelectedDomain(e.target.value)}
                className="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent focus:bg-white transition-colors duration-200"
                disabled={domainsLoading}
              >
                <option value="">All Domains</option>
                {domains?.map((domain) => (
                  <option key={domain} value={domain}>
                    {capitalize(domain)}
                  </option>
                ))}
              </select>
            </div>
            
            {/* Category Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent focus:bg-white transition-colors duration-200"
                disabled={categoriesLoading}
              >
                <option value="">All Categories</option>
                {categories?.map((category) => (
                  <option key={category} value={category}>
                    {capitalize(category.replace('_', ' '))}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </Card>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Rules List */}
          <Card title="Rules List">
            {allRulesLoading || filterLoading ? (
              <LoadingSpinner />
            ) : filteredRules.length > 0 ? (
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {filteredRules.map((rule) => (
                  <div
                    key={rule.id}
                    onClick={() => setSelectedRule(rule)}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors hover:bg-gray-50 ${
                      selectedRule?.id === rule.id ? 'border-primary-500 bg-primary-50' : 'border-gray-200'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900 mb-1">
                          {rule.name}
                        </h3>
                        <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                          {rule.description}
                        </p>
                        <div className="flex items-center space-x-2">
                          <Badge variant="default">
                            {capitalize(rule.domain)}
                          </Badge>
                          <Badge
                            variant="priority"
                            className={getPriorityColor(rule.priority)}
                          >
                            {getPriorityLabel(rule.priority)}
                          </Badge>
                        </div>
                      </div>
                      <div className="text-xs text-gray-500 ml-4">
                        Priority: {rule.priority}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">
                {allRules?.length === 0 ? 'No rules available' : 'No rules match your filters'}
              </div>
            )}
          </Card>
          
          {/* Rule Details */}
          <Card title="Rule Details">
            {selectedRule ? (
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {selectedRule.name}
                  </h3>
                  <p className="text-gray-600 mb-4">
                    {selectedRule.description}
                  </p>
                </div>
                
                {/* Meta Information */}
                <div className="grid grid-cols-2 gap-4 py-4 border-t border-gray-200">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Domain</label>
                    <div className="mt-1">
                      <Badge variant="default">
                        {capitalize(selectedRule.domain)}
                      </Badge>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Category</label>
                    <div className="mt-1">
                      <Badge variant="default">
                        {capitalize(selectedRule.category.replace('_', ' '))}
                      </Badge>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Priority</label>
                    <div className="mt-1">
                      <Badge
                        variant="priority"
                        className={getPriorityColor(selectedRule.priority)}
                      >
                        {getPriorityLabel(selectedRule.priority)} ({selectedRule.priority})
                      </Badge>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Rule ID</label>
                    <div className="mt-1 text-sm font-mono text-gray-700">
                      {selectedRule.id}
                    </div>
                  </div>
                </div>
                
                {/* Condition */}
                {selectedRule.condition && (
                  <div className="border-t border-gray-200 pt-4">
                    <label className="text-sm font-medium text-gray-500">Condition</label>
                    <div className="mt-2">
                      <div className="text-sm bg-gray-50 p-2 rounded font-mono">
                        {selectedRule.condition}
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Action */}
                {selectedRule.action && (
                  <div className="border-t border-gray-200 pt-4">
                    <label className="text-sm font-medium text-gray-500">Action</label>
                    <div className="mt-2">
                      <div className="text-sm bg-blue-50 p-2 rounded font-mono">
                        {selectedRule.action}
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Metadata */}
                {selectedRule.metadata && Object.keys(selectedRule.metadata).length > 0 && (
                  <div className="border-t border-gray-200 pt-4">
                    <label className="text-sm font-medium text-gray-500">Metadata</label>
                    <div className="mt-2">
                      <pre className="text-sm bg-gray-50 p-2 rounded overflow-auto">
                        {JSON.stringify(selectedRule.metadata, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
                
                {/* Metadata & Details */}
                <div className="border-t border-gray-200 pt-4 text-sm text-gray-500">
                  <div className="grid grid-cols-1 gap-2">
                    <div>
                      <span className="font-medium">Confidence:</span> {selectedRule.confidence}%
                    </div>
                    {selectedRule.reasoning && (
                      <div>
                        <span className="font-medium">Reasoning:</span> {selectedRule.reasoning}
                      </div>
                    )}
                    {selectedRule.parameters && Object.keys(selectedRule.parameters).length > 0 && (
                      <div>
                        <span className="font-medium">Parameters:</span>
                        <pre className="mt-1 text-xs bg-gray-50 p-2 rounded overflow-auto">
                          {JSON.stringify(selectedRule.parameters, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">
                Select a rule to view details
              </div>
            )}
          </Card>
        </div>
      </div>
    </Layout>
  );
};

export default Rules;