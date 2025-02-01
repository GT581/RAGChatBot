import React from 'react';
import { ChatSession } from '../types';
import { TrashIcon } from '@heroicons/react/24/outline';

interface SidebarProps {
  sessions: ChatSession[];
  currentSession: ChatSession | null;
  onSessionSelect: (session: ChatSession) => void;
  onNewSession: () => void;
  onDeleteSession: (sessionId: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  currentSession,
  onSessionSelect,
  onNewSession,
  onDeleteSession,
}) => {
  const formatTitle = (session: ChatSession) => {
    if (session.title) {
      return session.title;
    }
    const date = new Date(session.created_at);
    return `Chat from ${date.toLocaleDateString()}`;
  };

  return (
    <div className="w-64 bg-white border-r h-full p-4">
      <button
        onClick={onNewSession}
        className="w-full bg-blue-500 text-white rounded-lg py-2 px-4 mb-4 hover:bg-blue-600"
      >
        New Chat
      </button>
      <div className="space-y-2 overflow-y-auto max-h-[calc(100vh-150px)]">
        {sessions.map((session) => (
          <div
            key={session.id}
            className={`flex justify-between items-center p-2 rounded-lg cursor-pointer ${
              currentSession?.id === session.id
                ? 'bg-blue-100'
                : 'hover:bg-gray-100'
            }`}
          >
            <div onClick={() => onSessionSelect(session)}>
              {formatTitle(session)}
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDeleteSession(session.id);
              }}
              className="p-1 hover:bg-gray-200 rounded"
            >
              <TrashIcon className="h-4 w-4 text-gray-500" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Sidebar; 