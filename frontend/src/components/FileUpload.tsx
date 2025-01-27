import React, { useState } from 'react';
import { uploadFile } from '../services/api';
import axios from 'axios';

interface FileUploadProps {
  sessionId: string | null;
}

const FileUpload: React.FC<FileUploadProps> = ({ sessionId }) => {
  const [uploading, setUploading] = useState(false);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!sessionId) {
      alert('Please select or create a chat session first');
      return;
    }

    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);
      formData.append('session_id', sessionId);
      
      console.log('Uploading file:', file.name, 'type:', file.type);
      console.log('Session ID:', sessionId);
      
      await uploadFile(formData, sessionId);
      console.log('Upload response:', formData);
      
      alert('File uploaded successfully!');
    } catch (error) {
      console.error('Error uploading file:', error);
      if (axios.isAxiosError(error)) {
        console.error('Response:', error.response?.data);
      }
      alert('Failed to upload file');
    } finally {
      setUploading(false);
      // Reset file input
      event.target.value = '';
    }
  };

  return (
    <div className="mb-4">
      <input
        type="file"
        onChange={handleFileUpload}
        disabled={uploading || !sessionId}
        className="hidden"
        id="file-upload"
        accept=".pdf,.txt,.csv,.json,.xlsx"
      />
      <label
        htmlFor="file-upload"
        className={`inline-block px-4 py-2 bg-gray-200 rounded cursor-pointer
          ${uploading || !sessionId ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-300'}
          ${!sessionId ? 'tooltip' : ''}`}
        data-tooltip={!sessionId ? 'Please start a chat first' : ''}
      >
        {uploading ? 'Uploading...' : 'Upload Document'}
      </label>
      <span className="ml-2 text-sm text-gray-600">
        Supported formats: PDF, TXT, CSV, JSON, XLSX
      </span>
    </div>
  );
};

export default FileUpload; 