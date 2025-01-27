import axios from 'axios';
import { createSession, getUserSessions, sendMessage, uploadFile } from '../api';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('API Service', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('creates a chat session', async () => {
    const mockSession = {
      id: '123',
      title: 'New Chat',
      user_id: 'test_user'
    };
    
    mockedAxios.post.mockResolvedValueOnce({ data: mockSession });
    
    const result = await createSession('test_user');
    expect(result).toEqual(mockSession);
    expect(mockedAxios.post).toHaveBeenCalledWith('/chat/sessions/', {
      user_id: 'test_user'
    });
  });

  it('gets user sessions', async () => {
    const mockSessions = [
      { id: '123', title: 'Chat 1', user_id: 'test_user' },
      { id: '456', title: 'Chat 2', user_id: 'test_user' }
    ];
    
    mockedAxios.get.mockResolvedValueOnce({ data: mockSessions });
    
    const result = await getUserSessions('test_user');
    expect(result).toEqual(mockSessions);
    expect(mockedAxios.get).toHaveBeenCalledWith('/chat/sessions/test_user');
  });

  it('sends a message', async () => {
    const mockResponse = {
      id: '789',
      content: 'Hello!',
      role: 'assistant'
    };
    
    mockedAxios.post.mockResolvedValueOnce({ data: mockResponse });
    
    const result = await sendMessage('123', 'Hello');
    expect(result).toEqual(mockResponse);
    expect(mockedAxios.post).toHaveBeenCalledWith('/chat/sessions/123/messages', {
      message: 'Hello'
    });
  });

  it('uploads a file', async () => {
    const mockResponse = {
      id: '123',
      filename: 'test.pdf'
    };
    
    mockedAxios.post.mockResolvedValueOnce({ data: mockResponse });
    
    const formData = new FormData();
    formData.append('file', new File([''], 'test.pdf'));
    
    const result = await uploadFile(formData, 'sessionId');
    expect(result).toEqual(mockResponse);
    expect(mockedAxios.post).toHaveBeenCalledWith('/ingest/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  });

  it('handles API errors', async () => {
    mockedAxios.post.mockRejectedValueOnce(new Error('API Error'));
    
    await expect(createSession('test_user')).rejects.toThrow('API Error');
  });
}); 