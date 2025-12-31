import * as React from 'react';
import { Bot, User } from 'lucide-react';
import { format } from 'date-fns';
import { Separator } from '@/components/ui/separator';
import type { ChatMessageProps } from '@/types';

export function ChatMessage({ message, showSources = false }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  if (isSystem) {
    return (
      <div className="flex justify-center my-4">
        <div className="bg-muted text-muted-foreground text-sm px-4 py-2 rounded-lg">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className={`flex gap-3 mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
          <Bot className="w-5 h-5 text-primary-foreground" />
        </div>
      )}

      <div className={`max-w-[80%] space-y-2 ${isUser ? 'text-right' : 'text-left'}`}>
        <div
          className={`rounded-lg px-4 py-3 ${
            isUser
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-muted-foreground'
          }`}
        >
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        </div>

        {showSources && message.sources && message.sources.length > 0 && (
          <details className="text-xs text-muted-foreground space-y-1">
            <summary className="cursor-pointer hover:text-foreground">
              {message.sources.length} source(s)
            </summary>
            <div className="mt-2 space-y-2 pl-4">
              {message.sources.map((source, idx) => (
                <div key={idx} className="border-l-2 border-muted pl-3">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">
                      Confidence: {(source.score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="line-clamp-3 mt-1">
                    {source.content}
                  </p>
                </div>
              ))}
            </div>
          </details>
        )}

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          {message.confidence !== undefined && !isUser && (
            <span>
              Confidence: {(message.confidence * 100).toFixed(0)}%
            </span>
          )}
          <Separator orientation="vertical" className="h-3" />
          <span>{format(new Date(message.timestamp), 'h:mm a')}</span>
        </div>
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
          <User className="w-5 h-5 text-secondary-foreground" />
        </div>
      )}
    </div>
  );
}
