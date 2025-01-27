export interface ChatSession {
  id: string;
  user_id: string;
  title: string | null;
  hidden: boolean;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  meta_info?: {
    source_documents?: Array<{
      filename: string;
      chunk_index: number;
    }>;
  };
} 