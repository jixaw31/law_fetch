"use client";

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { useMessage } from '../contexts/MessageContext';
import 'highlight.js/styles/github-dark.css';

interface MarkdownRendererProps {
  content: string;
  messageId: string;
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content, messageId }) => {
  const { streamingMessageId } = useMessage();
  const isStreaming = streamingMessageId === messageId;
  const [copiedCodeBlock, setCopiedCodeBlock] = useState<string | null>(null);

  const copyToClipboard = async (code: string, id: string) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopiedCodeBlock(id);
      setTimeout(() => setCopiedCodeBlock(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
      setCopiedCodeBlock('error');
      setTimeout(() => setCopiedCodeBlock(null), 2000);
    }
  };

  // Track code blocks by their content + className for stable IDs
  let codeBlockCounter = 0;
  const codeBlockMap = new Map();

  return (
    <div className={`prose prose-invert max-w-none ${isStreaming ? 'streaming-text' : ''}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={{
          p: ({ children, ...props }) => (
            <p className="mb-2 leading-relaxed" {...props}>
              {children}
            </p>
          ),
          code: ({ className, children, ...props }) => {
            const isInline = !className || !className.includes('language-');
            const codeContent = String(children).replace(/\n$/, '');
            
            // Create a stable key based on content
            const stableKey = `${codeContent.substring(0, 50)}_${className || ''}`;
            if (!codeBlockMap.has(stableKey)) {
              codeBlockMap.set(stableKey, `code_${codeBlockCounter++}`);
            }
            const stableId = codeBlockMap.get(stableKey);
            
            if (!isInline) {
              return (
                <div className="relative group my-2">
                  <pre className="bg-gray-800 rounded-md p-3 overflow-x-auto">
                    <code className={className} {...props}>
                      {children}
                    </code>
                  </pre>
                  <button
                    onClick={() => copyToClipboard(codeContent, stableId)}
                    className="absolute top-2 right-2 px-2 py-1 text-xs rounded 
                               bg-gray-700 text-gray-200 opacity-0 group-hover:opacity-100 
                               transition-opacity hover:bg-gray-600 whitespace-nowrap"
                  >
                    {copiedCodeBlock === stableId 
                      ? '✓ Copied!' 
                      : '📋 Copy'}
                  </button>
                </div>
              );
            }
            
            return (
              <code className="bg-gray-800 px-1 rounded text-sm" {...props}>
                {children}
              </code>
            );
          },
          ul: ({ children }) => <ul className="list-disc pl-5 my-2">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal pl-5 my-2">{children}</ol>,
          li: ({ children }) => <li className="mb-1">{children}</li>,
          h1: ({ children }) => <h1 className="text-2xl font-bold my-3">{children}</h1>,
          h2: ({ children }) => <h2 className="text-xl font-bold my-2">{children}</h2>,
          h3: ({ children }) => <h3 className="text-lg font-bold my-2">{children}</h3>,
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">
              {children}
            </a>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-gray-500 pl-4 my-2 italic">
              {children}
            </blockquote>
          ),
          // Table components with proper props spreading
          table: ({ children, ...props }) => (
            <div className="overflow-x-auto my-4">
              <table className="min-w-full border-collapse border border-gray-600" {...props}>
                {children}
              </table>
            </div>
          ),
          thead: ({ children, ...props }) => (
            <thead className="bg-gray-800" {...props}>{children}</thead>
          ),
          tbody: ({ children, ...props }) => (
            <tbody className="bg-gray-900/50" {...props}>{children}</tbody>
          ),
          tr: ({ children, ...props }) => (
            <tr className="border-b border-gray-700 hover:bg-gray-800/50 transition-colors" {...props}>
              {children}
            </tr>
          ),
          th: ({ children, ...props }) => (
            <th className="border border-gray-600 px-4 py-2 text-left font-semibold text-gray-200" {...props}>
              {children}
            </th>
          ),
          td: ({ children, ...props }) => (
            <td className="border border-gray-600 px-4 py-2 text-gray-300" {...props}>
              {children}
            </td>
          ),
          // Task list support (checkboxes)
          input: (props: React.InputHTMLAttributes<HTMLInputElement>) => {
            if (props.type === 'checkbox') {
              return (
                <input 
                  type="checkbox"
                  checked={props.checked}
                  disabled={props.disabled}
                  className="mr-2 h-4 w-4 rounded border-gray-600 
                             bg-gray-800 text-blue-500 focus:ring-blue-500
                             cursor-pointer disabled:cursor-not-allowed"
                  onChange={() => {}} // No-op for read-only display
                />
              );
            }
            return <input {...props} />;
          },
        }}
      >
        {content}
      </ReactMarkdown>
      
      {/* Enhanced streaming animation */}
      {isStreaming && (
        <div className="inline-flex items-center gap-1 ml-1">
          <span 
            className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" 
            style={{ animationDelay: '0ms' }} 
          />
          <span 
            className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" 
            style={{ animationDelay: '150ms' }} 
          />
          <span 
            className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" 
            style={{ animationDelay: '300ms' }} 
          />
        </div>
      )}
    </div>
  );
};

export default MarkdownRenderer;