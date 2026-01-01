/**
 * Zustand store for chat state management with WebSocket integration
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type {
  Message,
  MessageRole,
  ChatRequest,
  ChatResponse,
  WSMessage,
} from '@/types';
import { WebSocketClient } from '@/lib/websocket';

interface ChatStore {
  // Session state
  sessionId: string | null;
  isConnected: boolean;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';

  // Messages
  messages: Message[];
  isTyping: boolean;

  // Trust & Thinking
  isThinking: boolean;

  // Evidence Sheet
  expandedCitation: number | null;

  // WebSocket client
  socketClient: WebSocketClient | null;

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

  // Trust & Thinking actions
  setThinking: (thinking: boolean) => void;

  // Evidence actions
  setExpandedCitation: (citation: number | null) => void;

  // WebSocket actions
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
  handleWSMessage: (message: WSMessage) => void;

  // Async actions
  sendMessage: (content: string) => Promise<void>;
  createSession: () => Promise<void>;
  disconnect: () => Promise<void>;
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
      isThinking: false,
      socketClient: null,
      expandedCitation: null,

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

      setConnectionStatus: (
        status: 'connecting' | 'connected' | 'disconnected' | 'error',
      ) => set({
        connectionStatus: status,
        isConnected: status === 'connected',
      }),

      setTyping: (typing) => set({ isTyping: typing }),

      // Trust & Thinking actions
      setThinking: (thinking: boolean) => set({ isThinking: thinking }),

      // Evidence actions
      setExpandedCitation: (citation: number | null) => set({ expandedCitation: citation }),

      // WebSocket actions
      connectWebSocket: () => {
        const { sessionId } = get();
        if (!sessionId) {
          console.warn('Cannot connect WebSocket: no session ID');
          return;
        }

        const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/v1/chat/ws';
        console.log(`[WebSocket] Attempting connection to: ${wsUrl}?session_id=${sessionId}`);

        const wsClient = new WebSocketClient({
          url: wsUrl,
          session_id: sessionId,
          onMessage: (message: WSMessage) => {
            get().handleWSMessage(message);
          },
          onOpen: () => {
            set({ connectionStatus: 'connected', isConnected: true });
            console.log('[WebSocket] Connected');
          },
          onError: (error: any, details?: any) => {
            const errorInfo = {
              type: error?.type || details?.type || 'unknown',
              message: error?.message || details?.message || 'No message provided',
              timestamp: new Date().toISOString(),
            };
            
            if (details?.target) {
              (errorInfo as any).readyState = details.target.readyState;
              (errorInfo as any).url = details.target.url;
              (errorInfo as any).protocol = details.target.protocol;
            }
            
            console.error('[WebSocket] Error:', errorInfo);
            set({ connectionStatus: 'error', isConnected: false });
          },
          onClose: (event: CloseEvent) => {
            const closeInfo = {
              code: event.code,
              reason: event.reason || 'No reason provided',
              wasClean: event.wasClean,
              timestamp: new Date().toISOString(),
            };
            
            console.log('[WebSocket] Closed:', closeInfo);
            set({ connectionStatus: 'disconnected', isConnected: false });
          },
          reconnectInterval: 3000,
          maxReconnectAttempts: 10,
          heartbeatInterval: 30000,
        });

        set({ socketClient: wsClient });
        wsClient.connect();
      },

      disconnectWebSocket: () => {
        const { socketClient } = get();
        if (socketClient) {
          socketClient.disconnect();
          set({ socketClient: null, connectionStatus: 'disconnected', isConnected: false });
        }
      },

      handleWSMessage: (message: WSMessage) => {
        const { addMessage, setThinking, setTyping } = get();

        switch (message.type) {
          case 'connected':
            console.log('[WebSocket] Connected event:', message.message);
            break;

          case 'response':
            const assistantMessage: Message = {
              id: `msg-${Date.now()}-assistant`,
              role: 'assistant' as MessageRole,
              content: message.message,
              timestamp: new Date(),
              confidence: message.confidence,
              sources: message.sources,
            };
            addMessage(assistantMessage);

            if (message.escalated) {
              const escalatedMessage: Message = {
                id: `msg-${Date.now()}-system`,
                role: 'system' as MessageRole,
                content: message.ticket_id
                  ? `Ticket created: ${message.ticket_id}`
                  : 'Escalated to human support.',
                timestamp: new Date(),
              };
              addMessage(escalatedMessage);
            }

            setTyping(false);
            setThinking(false);
            break;

          case 'thought':
            setThinking(true);
            console.log('[WebSocket] Thought:', message.step);
            break;

          case 'error':
            const errorMessage: Message = {
              id: `msg-${Date.now()}-error`,
              role: 'system' as MessageRole,
              content: message.message,
              timestamp: new Date(),
            };
            addMessage(errorMessage);
            setTyping(false);
            setThinking(false);
            break;

          default:
            console.log('[WebSocket] Unknown message type:', message);
        }
      },

      // Async actions
      sendMessage: async (content) => {
        const { sessionId, addMessage, setTyping, socketClient } = get();

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
          // Use WebSocket if available and not disabled, otherwise fall back to REST
          if (socketClient && 
              socketClient.getStatus() === 'connected' && 
              !socketClient.isWebSocketDisabled()) {
            socketClient.sendChatMessage(content);
          } else {
            // Fallback to REST API
            if (socketClient?.isWebSocketDisabled()) {
              console.info('[WebSocket] Using REST API fallback (WebSocket disabled)');
            } else {
              console.info('[WebSocket] Using REST API fallback (not connected)');
            }
            
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
          const { session_id } = session;

          set({ sessionId: session_id });
          localStorage.setItem('session_id', session_id);

          // Auto-connect WebSocket after session creation
          get().connectWebSocket();

          return session;
        } catch (error) {
          console.error('Failed to create session:', error);
          throw error;
        }
      },

      disconnect: async () => {
        const { sessionId, disconnectWebSocket } = get();

        // Disconnect WebSocket first
        disconnectWebSocket();

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
          isThinking: false,
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
export const selectIsThinking = (state: ChatStore) => state.isThinking;
