import * as React from 'react';
import type { TypingIndicatorProps } from '@/types';

export function TypingIndicator({
  isVisible = true,
  text = 'Agent is typing...',
}: TypingIndicatorProps) {
  if (!isVisible) {
    return null;
  }

  return (
    <div className="flex items-center gap-1 text-sm text-muted-foreground px-4 py-2">
      <span>{text}</span>
      <div className="flex gap-1">
        <span className="animate-bounce" style={{ animationDelay: '0ms' }}>
          ●
        </span>
        <span className="animate-bounce" style={{ animationDelay: '150ms' }}>
          ●
        </span>
        <span className="animate-bounce" style={{ animationDelay: '300ms' }}>
          ●
        </span>
      </div>
    </div>
  );
}
