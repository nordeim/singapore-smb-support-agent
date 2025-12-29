/**
 * Zustand store for chat state management
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type {
  Message,
  MessageRole,
  ChatRequest,
  ChatResponse,
} from '@/types';

interface ChatStore {
  // Session state
  sessionId: string | null;
  isConnected: boolean;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';

  // Messages
  messages: Message[];
  isTyping: boolean;

  // Actions
  setSessionId: (id: string) => void;
  addMessage: (message: Message) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  clearMessages: () => void;
  setConnected: (connected: boolean) => void;
  setConnectionStatus: (
    status: 'connecting' | 'connected' | 'disconnected' | 'error',
  ) => void;
  setTyping: (typing: boolean) => void;

  // Async actions
  sendMessage: (content: string) => Promise<void>;
  createSession: () => Promise<void>;
  disconnect: () => void;
}

export const useChatStore = create<ChatStore>()(
  devtools(
    (set, get) => ({
      // Initial state
      sessionId: null,
      isConnected: false,
      connectionStatus: 'disconnected',
      messages: [],
      isTyping: false,

      // Session actions
      setSessionId: (id) => set({ sessionId: id }),

      // Message actions
      addMessage: (message) =>
        set((state) => ({
          messages: [...state.messages, message],
        })),

      updateMessage: (id, updates) =>
        set((state) => ({
          messages: state.messages.map((msg) =>
            msg.id === id ? { ...msg, ...updates } : msg,
          ),
        })),

      clearMessages: () => set({ messages: [] }),

      // Connection actions
      setConnected: (connected) => set({ isConnected: connected }),

      setConnectionStatus: (status) =>
        set({
          connectionStatus: status,
          isConnected: status === 'connected',
        }),

      setTyping: (typing) => set({ isTyping: typing }),

      // Async actions
      sendMessage: async (content) => {
        const { sessionId, addMessage, setTyping } = get();

        if (!sessionId) {
          console.error('No session ID. Cannot send message.');
          return;
        }

        // Add user message
        const userMessage: Message = {
          id: `msg-${Date.now()}-user`,
          role: 'user' as MessageRole,
          content,
          timestamp: new Date(),
        };

        addMessage(userMessage);
        setTyping(true);

        try {
          const { chatService } = await import('@/lib/api');

          const request: ChatRequest = {
            session_id: sessionId,
            message: content,
          };

          const response: ChatResponse = await chatService.sendMessage(request);

          // Add assistant message
          const assistantMessage: Message = {
            id: `msg-${Date.now()}-assistant`,
            role: 'assistant' as MessageRole,
            content: response.message,
            timestamp: new Date(),
            confidence: response.confidence,
            sources: response.sources,
          };

          addMessage(assistantMessage);

          if (response.escalated) {
            const escalatedMessage: Message = {
              id: `msg-${Date.now()}-system`,
              role: 'system' as MessageRole,
              content: response.ticket_id
                ? `Ticket created: ${response.ticket_id}`
                : 'Escalated to human support.',
              timestamp: new Date(),
            };
            addMessage(escalatedMessage);
          }
        } catch (error) {
          console.error('Failed to send message:', error);

          const errorMessage: Message = {
            id: `msg-${Date.now()}-error`,
            role: 'system' as MessageRole,
            content:
              'Failed to send message. Please try again.',
            timestamp: new Date(),
          };
          addMessage(errorMessage);
        } finally {
          setTyping(false);
        }
      },

      createSession: async () => {
        try {
          const { authService } = await import('@/lib/api');

          const session = await authService.createSession();
          const { sessionId } = session;

          set({ sessionId });
          localStorage.setItem('session_id', sessionId);

          return session;
        } catch (error) {
          console.error('Failed to create session:', error);
          throw error;
        }
      },

      disconnect: () => {
        const { sessionId } = get();

        if (sessionId) {
          try {
            const { authService } = await import('@/lib/api');
            await authService.logout(sessionId);
          } catch (error) {
            console.error('Failed to disconnect:', error);
          }
        }

        localStorage.removeItem('session_id');
        set({
          sessionId: null,
          isConnected: false,
          connectionStatus: 'disconnected',
          messages: [],
          isTyping: false,
        });
      },
    }),
    { name: 'chat-store' },
  ),
);

// Selectors
export const selectMessages = (state: ChatStore) => state.messages;
export const selectIsTyping = (state: ChatStore) => state.isTyping;
export const selectIsConnected = (state: ChatStore) => state.isConnected;
export const selectConnectionStatus = (state: ChatStore) => state.connectionStatus;
export const selectSessionId = (state: ChatStore) => state.sessionId;
