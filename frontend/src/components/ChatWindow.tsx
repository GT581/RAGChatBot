import React, { useState, useRef, useEffect } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import { Message } from '../types';

interface ChatWindowProps {
  messages: Message[];
  onSendMessage: (content: string) => void;
  loading: boolean;
}

const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  onSendMessage,
  loading,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 flex flex-col h-screen">
      <div className="flex-1 relative">
        <div className="overflow-y-auto scrollbar-thin p-4 pb-20 h-full">
          <MessageList messages={messages} />
          <div ref={messagesEndRef} />
        </div>
        <div className="sticky bottom-0 bg-white p-4 border-t border-primary-dark z-10">
          <MessageInput onSendMessage={onSendMessage} disabled={loading} />
        </div>
      </div>
    </div>
  );
};

export default ChatWindow; 