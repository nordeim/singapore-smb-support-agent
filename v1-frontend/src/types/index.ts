/**
 * TypeScript type definitions for Singapore SMB Support Agent frontend
 */

// Message types
export type MessageRole = 'user' | 'assistant' | 'system';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  confidence?: number;
  sources?: Source[];
}

// Source type for RAG citations
export interface Source {
  content: string;
  metadata: Record<string, unknown>;
  score: number;
}

// Chat API types
export interface ChatRequest {
  session_id: string;
  message: string;
  language?: string;
}

export interface ChatResponse {
  session_id: string;
  message: string;
  role: string;
  confidence: number;
  sources: Source[];
  requires_followup: boolean;
  escalated: boolean;
  ticket_id?: string;
}

// Authentication types
export interface UserRegisterRequest {
  email: string;
  password: string;
  consent_given: boolean;
}

export interface UserLoginRequest {
  email: string;
  password: string;
}

export interface User {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface Session {
  session_id: string;
  user_id?: number;
  email?: string;
  created_at: string;
  expires_in?: string;
}

// WebSocket message types
export interface WSConnected {
  type: 'connected';
  session_id: string;
  message: string;
}

export interface WSResponse {
  type: 'response';
  session_id: string;
  message: string;
  confidence: number;
  sources: Source[];
  requires_followup: boolean;
  escalated: boolean;
  ticket_id?: string;
}

export interface WSError {
  type: 'error';
  message: string;
}

export interface WSPong {
  type: 'pong';
}

export interface WSPing {
  type: 'ping';
}

export interface WSMessageRequest {
  type: 'message';
  message: string;
}

export interface WSDisconnect {
  type: 'disconnect';
}

export type WSMessage = WSConnected | WSResponse | WSError | WSPong;
export type WSRequest = WSMessageRequest | WSPing | WSDisconnect;

// Business hours type
export interface BusinessHours {
  is_open: boolean;
  business_hours: string;
  current_time: string;
  timezone: string;
}

// Health check type
export interface HealthCheck {
  status: string;
  timestamp: string;
  services: Record<string, string>;
}

// Error types
export interface ErrorResponse {
  detail: string;
  error_code?: string;
  timestamp: string;
}

// UI component types
export interface ChatHeaderProps {
  isOnline?: boolean;
  businessHours?: BusinessHours;
  agentName?: string;
}

export interface ChatMessageProps {
  message: Message;
  showSources?: boolean;
}

export interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  isLoading?: boolean;
  maxLength?: number;
  placeholder?: string;
}

export interface TypingIndicatorProps {
  isVisible?: boolean;
  text?: string;
}
