import React, { useState, useEffect } from 'react';
import { createSession, sendMessage, getUserSessions, getChatHistory, deleteSession } from '../services/api';
import FileUpload from './FileUpload';
import Sidebar from './Sidebar';
import { Message, ChatSession } from '../types';
import MessageInput from './MessageInput';
import MessageList from './MessageList';

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadSessions = async () => {
      try {
        const userSessions = await getUserSessions('user-1');
        setSessions(userSessions);
      } catch (error) {
        console.error('Error loading sessions:', error);
      }
    };
    loadSessions();
  }, []);

  useEffect(() => {
    const loadChatHistory = async () => {
      if (currentSession) {
        try {
          const history = await getChatHistory(currentSession.id);
          setMessages(history);
        } catch (error) {
          console.error('Error loading chat history:', error);
        }
      }
    };
    loadChatHistory();
  }, [currentSession]);

  const handleNewSession = async () => {
    try {
      const session = await createSession('user-1');
      setSessions([...sessions, session]);
      setCurrentSession(session);
      setMessages([]);
    } catch (error) {
      console.error('Error creating session:', error);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!currentSession) return;
    
    setLoading(true);
    try {
      // Show message immediately in UI
      const tempMessage: Message = {
        id: 'temp-' + Date.now(),
        role: 'user',
        content,
        session_id: currentSession.id,
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, tempMessage]);

      // Send to API and get response
      const messages = await sendMessage(currentSession.id, content);
      
      // Replace temp message and add both messages
      setMessages(prev => [
        ...prev.filter(m => m.id !== tempMessage.id),
        ...messages
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      await deleteSession(sessionId);
      setSessions(sessions.filter(s => s.id !== sessionId));
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  };

  return (
    <div className="flex h-screen">
      <Sidebar
        sessions={sessions}
        currentSession={currentSession}
        onSessionSelect={setCurrentSession}
        onNewSession={handleNewSession}
        onDeleteSession={handleDeleteSession}
      />
      <div className="flex-1 flex flex-col p-4">
        <div className="mb-4">
          <FileUpload sessionId={currentSession?.id || null} />
        </div>
        <div className="flex-1 overflow-y-auto mb-4 space-y-4">
          <MessageList messages={messages} />
        </div>
        <div className="sticky bottom-0 bg-white p-4 border-t">
          <MessageInput 
            onSendMessage={handleSendMessage}
            disabled={loading || !currentSession}
          />
        </div>
      </div>
    </div>
  );
};

export default ChatInterface; 