import * as React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { ChatHeader } from './ChatHeader';
import { ChatMessages } from './ChatMessages';
import { ChatInput } from './ChatInput';
import { useChatStore } from '@/stores/chatStore';
import { Button } from '@/components/ui/button';
import { LogOut, RefreshCw } from 'lucide-react';

export function ChatWidget() {
  const { sessionId, isTyping, createSession, disconnect } =
    useChatStore();

  const handleSessionCreate = async () => {
    try {
      await createSession();
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  React.useEffect(() => {
    const storedSessionId = localStorage.getItem('session_id');

    if (storedSessionId) {
      useChatStore.setState({ sessionId: storedSessionId });
    } else {
      handleSessionCreate();
    }
  }, []);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl h-[80vh] flex flex-col">
        <ChatHeader />

        <CardContent className="flex-1 overflow-hidden p-0">
          <ChatMessages />
        </CardContent>

        <ChatInput
          onSendMessage={async (content) => {
            const { sendMessage } = useChatStore.getState();
            await sendMessage(content);
          }}
          disabled={!sessionId || !isTyping}
          isLoading={isTyping}
        />

        <div className="border-t bg-muted px-4 py-2 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span>
              Session ID: {sessionId?.slice(0, 8)}...
            </span>
            {sessionId && (
              <span>• {useChatStore.getState().messages.length} messages</span>
            )}
          </div>
          <div className="flex items-center gap-2">
            {sessionId && (
              <Button
                variant="ghost"
                size="icon"
                onClick={handleSessionCreate}
                title="New session"
              >
                <RefreshCw className="w-4 h-4" />
              </Button>
            )}
            {sessionId && (
              <Button
                variant="ghost"
                size="icon"
                onClick={disconnect}
                title="Disconnect"
              >
                <LogOut className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}
