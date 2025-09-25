import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-500">
            © 2025 Business Rules POC. Built with React + Vite.
          </div>
          <div className="flex space-x-6">
            <div className="text-sm text-gray-500">
              Powered by LlamaIndex & Ollama
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;