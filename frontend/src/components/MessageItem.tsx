import React from 'react';
import { Message } from '../types';
import { DocumentTextIcon } from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';

interface MessageItemProps {
  message: Message;
}

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const sourceDocuments = message.meta_info?.source_documents ?? [];
  const hasSourceDocuments = sourceDocuments.length > 0;

  return (
    <div
      className={`chat-message ${
        message.role === 'user' ? 'user-message' : 'assistant-message'
      }`}
    >
      <div className="message-content">
        <ReactMarkdown>{message.content}</ReactMarkdown>
      </div>
      {hasSourceDocuments && (
        <div className="mt-2 text-sm">
          <div className="font-semibold flex items-center gap-1 text-gray-700">
            <DocumentTextIcon className="h-4 w-4" />
            Sources:
          </div>
          <ul className="list-disc list-inside ml-2">
            {sourceDocuments.map((doc, index) => (
              <li key={index} className="text-sm opacity-75">
                {doc.filename} {doc.chunk_index !== undefined && `(Chunk ${doc.chunk_index + 1})`}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default MessageItem; 