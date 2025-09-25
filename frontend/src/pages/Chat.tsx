import React, { useState, useRef, useEffect } from 'react';
import { Layout } from '../components/layout';
import { Card, Button, Alert } from '../components/ui';
import { ChatMessage, ChatRequest } from '../types';
import apiService from '../services/api';

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI assistant for business rules and compliance. How can I help you today?',
      timestamp: new Date().toISOString(),
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const scrollToBottom = () => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ 
        behavior: 'smooth',
        block: 'end'
      });
    }, 100);
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  useEffect(() => {
    // Force scroll to bottom when loading state changes
    if (!loading) {
      scrollToBottom();
    }
  }, [loading]);
  
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || loading) return;
    
    const userMessage: ChatMessage = {
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);
    setError(null);
    
    try {
      const chatRequest: ChatRequest = {
        message: userMessage.content,
        conversation_history: messages,
      };
      
      const response = await apiService.chatWithAgent(chatRequest);
      
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
      // Add suggested actions if provided
      if (response.suggested_actions && response.suggested_actions.length > 0) {
        const suggestionsMessage: ChatMessage = {
          role: 'assistant',
          content: `**Suggested Actions:**\n${response.suggested_actions.map(action => `• ${action}`).join('\n')}`,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, suggestionsMessage]);
      }
    } catch (err: unknown) {
      console.error('Chat error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      
      const errorResponseMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your message. Please try again.',
        timestamp: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, errorResponseMessage]);
    } finally {
      setLoading(false);
    }
  };
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  const clearChat = () => {
    setMessages([
      {
        role: 'assistant',
        content: 'Hello! I\'m your AI assistant for business rules and compliance. How can I help you today?',
        timestamp: new Date().toISOString(),
      }
    ]);
    setError(null);
  };
  
  const formatMessage = (content: string) => {
    // Simple markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br />');
  };
  
  const exampleQuestions = [
    "What rules apply to loan applications?",
    "How do I handle GDPR compliance for customer data?",
    "What are the requirements for financial transactions?",
    "Explain the inventory management rules",
    "What should I do when a customer complaint is escalated?",
  ];
  
  const handleExampleClick = (question: string) => {
    setInputMessage(question);
  };
  
  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Chat Assistant</h1>
            <p className="mt-1 text-gray-600">
              Ask questions about business rules, compliance, and regulations
            </p>
          </div>
          <Button onClick={clearChat} variant="outline">
            Clear Chat
          </Button>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-200px)]">
          {/* Chat Interface */}
          <div className="lg:col-span-3 flex flex-col">
            <Card className="flex-1 flex flex-col min-h-0">
              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0" style={{ maxHeight: 'calc(100vh - 350px)' }}>
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-3 break-words ${
                        message.role === 'user'
                          ? 'bg-primary-500 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <div
                        className="text-sm leading-relaxed whitespace-pre-wrap"
                        dangerouslySetInnerHTML={{ __html: formatMessage(message.content) }}
                      />
                      {message.timestamp && (
                        <div className={`text-xs mt-1 ${
                          message.role === 'user' ? 'text-primary-100' : 'text-gray-500'
                        }`}>
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                
                {/* Loading indicator */}
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 text-gray-900 rounded-lg p-3">
                      <div className="flex items-center space-x-2">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                        <span className="text-sm text-gray-500">Assistant is typing...</span>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>
              
              {/* Error Display */}
              {error && (
                <div className="p-4 border-t">
                  <Alert type="error" title="Chat Error">
                    {error}
                  </Alert>
                </div>
              )}
              
              {/* Input Area */}
              <div className="border-t p-4">
                <div className="flex space-x-3">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
                    rows={2}
                    className="flex-1 px-3 py-2 bg-gray-50 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent focus:bg-white transition-colors duration-200 resize-none"
                    disabled={loading}
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim() || loading}
                    loading={loading}
                    className="px-6"
                  >
                    Send
                  </Button>
                </div>
              </div>
            </Card>
          </div>
          
          {/* Sidebar with Examples */}
          <div className="lg:col-span-1 flex flex-col">
            <Card title="Example Questions" className="flex-1">
              <div className="space-y-2">
                {exampleQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleExampleClick(question)}
                    className="w-full text-left p-2 text-sm text-gray-700 hover:bg-gray-50 rounded border border-gray-200 transition-colors duration-200"
                    disabled={loading}
                  >
                    {question}
                  </button>
                ))}
              </div>
              
              <div className="mt-6 pt-4 border-t border-gray-200">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Tips:</h4>
                <ul className="text-xs text-gray-600 space-y-1">
                  <li>• Ask about specific business rules</li>
                  <li>• Request compliance guidance</li>
                  <li>• Get help with rule interpretation</li>
                  <li>• Ask for examples or scenarios</li>
                  <li>• Use "Explain" for detailed responses</li>
                </ul>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Chat;