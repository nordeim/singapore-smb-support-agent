import * as React from 'react';
import { Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';
import type { ChatInputProps } from '@/types';

export function ChatInput({
  onSendMessage,
  disabled = false,
  isLoading = false,
  maxLength = 5000,
  placeholder = 'Type your message here...',
}: ChatInputProps) {
  const [message, setMessage] = React.useState('');
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmed = message.trim();

    if (trimmed.length > 0 && !disabled && !isLoading) {
      onSendMessage(trimmed);
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;

    if (newValue.length <= maxLength) {
      setMessage(newValue);

      // Auto-resize textarea
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
        textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
      }
    }
  };

  React.useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  }, [message]);

  const remainingChars = maxLength - message.length;
  const isNearLimit = remainingChars < 100;
  const isAtLimit = remainingChars <= 0;

  return (
    <div className="border-t bg-background p-4">
      <div className="space-y-2">
        <Label htmlFor="chat-input" className="sr-only">
          Message input
        </Label>
        <div className="flex gap-2">
          <Textarea
            ref={textareaRef}
            id="chat-input"
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled || isLoading}
            className="min-h-[60px] max-h-[200px] resize-none"
            aria-label="Message input"
          />
          <Button
            onClick={handleSend}
            disabled={disabled || isLoading || message.trim().length === 0}
            size="icon"
            className="h-[60px] w-[60px] flex-shrink-0"
            aria-label="Send message"
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>
        <div
          className={cn(
            'text-xs flex justify-between',
            isNearLimit && !isAtLimit && 'text-amber-500',
            isAtLimit && 'text-red-500',
          )}
        >
          <span className="text-muted-foreground">
            {isLoading ? 'Sending...' : 'Press Enter to send, Shift+Enter for new line'}
          </span>
          <span>
            {message.length} / {maxLength}
          </span>
        </div>
      </div>
    </div>
  );
}
