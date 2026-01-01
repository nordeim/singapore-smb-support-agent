# backend/app/memory/long_term.py
```py
"""Long-term memory using PostgreSQL with SQLAlchemy async."""

from datetime import datetime
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import (
    Base,
    User,
    Conversation,
    Message,
    ConversationSummary,
    SupportTicket,
)


class LongTermMemory:
    """Long-term memory using PostgreSQL for persistent storage."""

    def __init__(self, db: AsyncSession):
        """Initialize long-term memory with database session."""
        self.db = db

    async def create_user(
        self,
        email: str,
        hashed_password: str,
        consent_given_at: datetime,
        consent_version: str = "v1.0",
        data_retention_days: int = 30,
    ) -> User:
        """Create a new user."""
        user = User(
            email=email,
            hashed_password=hashed_password,
            consent_given_at=consent_given_at,
            consent_version=consent_version,
            data_retention_days=data_retention_days,
            is_active=True,
            is_deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User)
            .where(User.email == email)
            .where(User.is_active == True)
            .where(User.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def create_conversation(
        self,
        user_id: int,
        session_id: str,
        language: str = "en",
    ) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            user_id=user_id,
            session_id=session_id,
            language=language,
            is_active=True,
            summary_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def get_conversation_by_session_id(self, session_id: str) -> Optional[Conversation]:
        """Get conversation by session ID."""
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.session_id == session_id)
            .where(Conversation.is_active == True)
        )
        return result.scalar_one_or_none()

    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        confidence: Optional[float] = None,
        sources: Optional[str] = None,
    ) -> Message:
        """Add a message to conversation."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            confidence=confidence,
            sources=sources,
            created_at=datetime.utcnow(),
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_conversation_messages(
        self,
        conversation_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Message]:
        """Get messages for a conversation with pagination."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def save_conversation_summary(
        self,
        conversation_id: int,
        summary: str,
        message_range_start: int,
        message_range_end: int,
        embedding_vector: Optional[str] = None,
        metadata: Optional[str] = None,
    ) -> ConversationSummary:
        """Save conversation summary."""
        conv_summary = ConversationSummary(
            conversation_id=conversation_id,
            summary=summary,
            message_range_start=message_range_start,
            message_range_end=message_range_end,
            embedding_vector=embedding_vector,
            metadata=metadata,
            created_at=datetime.utcnow(),
        )
        self.db.add(conv_summary)

        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            conversation.summary_count += 1
            conversation.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(conv_summary)
        return conv_summary

    async def get_conversation_summaries(
        self,
        conversation_id: int,
    ) -> list[ConversationSummary]:
        """Get all summaries for a conversation."""
        result = await self.db.execute(
            select(ConversationSummary)
            .where(ConversationSummary.conversation_id == conversation_id)
            .order_by(ConversationSummary.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_support_ticket(
        self,
        conversation_id: int,
        reason: str,
        status: str = "open",
    ) -> SupportTicket:
        """Create a support ticket for human escalation."""
        ticket = SupportTicket(
            conversation_id=conversation_id,
            reason=reason,
            status=status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def update_ticket_status(
        self,
        ticket_id: int,
        status: str,
        assigned_to: Optional[str] = None,
    ) -> Optional[SupportTicket]:
        """Update ticket status."""
        result = await self.db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
        ticket = result.scalar_one_or_none()
        if ticket:
            ticket.status = status
            ticket.assigned_to = assigned_to
            ticket.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(ticket)
        return ticket

    async def expire_user_data(self, user_id: int) -> None:
        """Mark user data for PDPA-compliant expiry (soft delete)."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.is_active = False
            user.updated_at = datetime.utcnow()
        await self.db.commit()

    async def get_conversation_count(self, user_id: int) -> int:
        """Get total conversation count for a user."""
        result = await self.db.execute(
            select(func.count(Conversation.id))
            .where(Conversation.user_id == user_id)
            .where(Conversation.is_active == True)
        )
        count = result.scalar()
        return count if count is not None else 0

```

# frontend/src/app/globals.css
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* Typography - Singapore Professional */
    --font-manrope: 'Manrope', sans-serif;
    --font-inter: 'Inter', sans-serif;

    /* Trust Colors - Singapore Professional */
    --semantic-green: 120 45% 69%;    /* Medium Green - Trust */
    --semantic-amber: 40 75% 65%;     /* Amber - Warning */
    --semantic-red: 0 70% 50%;         /* Red - Error */

    /* Enhanced Radius - Sharp, Professional */
    --radius: 0.125rem;  /* 2px instead of 8px */

    /* Color System - Base */
    --background: 0 0% 100%;
    --foreground: 0 0% 100%;
    --card: 0 0% 100%;
    --card-foreground: 0 0% 100%;
    --popover: 0 0% 100%;
    --popover-foreground: 0 0% 100%;
    --primary: 0 0% 9%;
    --primary-foreground: 0 0% 98%;
    --secondary: 0 0% 96.1%;
    --secondary-foreground: 0 0% 9%;
    --muted: 0 0% 96.1%;
    --muted-foreground: 0 0% 45.1%;
    --accent: 0 0% 96.1%;
    --accent-foreground: 0 0% 9%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 0 0% 98%;
    --border: 0 0% 89.8%;
    --input: 0 0% 89.8%;
    --ring: 0 0% 3.9%;
  }

  .dark {
    --background: 0 0% 3.9%;
    --foreground: 0 0% 98%;
    --card: 0 0% 3.9%;
    --card-foreground: 0 0% 98%;
    --popover: 0 0% 3.9%;
    --popover-foreground: 0 0% 98%;
    --primary: 0 0% 98%;
    --primary-foreground: 0 0% 9%;
    --secondary: 0 0% 14.9%;
    --secondary-foreground: 0 0% 98%;
    --muted: 0 0% 14.9%;
    --muted-foreground: 0 0% 63.9%;
    --accent: 0 0% 14.9%;
    --accent-foreground: 0 0% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 0 0% 98%;
    --border: 0 0% 14.9%;
    --input: 0 0% 14.9%;
    --ring: 0 0% 83.1%;
  }
}

* {
  @apply border-border;
}

body {
  @apply bg-background text-foreground;
}

```

# frontend/src/components/chat/ChatMessage.tsx
```tsx
'use client';

import * as React from 'react';
import { Bot, User } from 'lucide-react';
import { format } from 'date-fns';
import { Separator } from '@/components/ui/separator';
import { ConfidenceRing } from '@/components/ui/confidence-ring';
import { ThinkingState } from './ThinkingState';
import type { ChatMessageProps } from '@/types';
import { useChatStore } from '@/stores/chatStore';

export function ChatMessage({ message, showSources = false }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';
  const { isThinking } = useChatStore();

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
        <div className="flex-shrink-0">
          <ConfidenceRing confidence={message.confidence || 0}>
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
              <Bot className="w-5 h-5 text-primary-foreground" />
            </div>
          </ConfidenceRing>
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

```

# frontend/src/components/chat/ChatMessages.tsx
```tsx
import * as React from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ChatMessage } from './ChatMessage';
import { ThinkingState } from './ThinkingState';
import { TypingIndicator } from './TypingIndicator';
import { useChatStore } from '@/stores/chatStore';

export function ChatMessages() {
  const { messages, isTyping, isThinking } = useChatStore();
  const scrollAreaRef = React.useRef<HTMLDivElement>(null);
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  if (messages.length === 0 && !isTyping) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        <p className="text-center">
          Welcome to Singapore SMB Support Agent.
          <br />
          Ask me anything about our products, services, or policies.
        </p>
      </div>
    );
  }

  return (
    <ScrollArea className="flex-1" ref={scrollAreaRef}>
      <div className="p-4 space-y-4">
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
            showSources
          />
        ))}

        {isThinking && <ThinkingState isThinking={true} />}

        {isTyping && <TypingIndicator />}

        <div ref={messagesEndRef} />
      </div>
    </ScrollArea>
  );
}

```

# frontend/src/components/ui/confidence-ring.tsx
```tsx
'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

export interface ConfidenceRingProps {
  children?: React.ReactNode;
  confidence: number;
  size?: 'sm' | 'md' | 'lg';
}

export function ConfidenceRing({ children, confidence, size = 'md' }: ConfidenceRingProps) {
  const getRingColor = () => {
    if (confidence >= 0.85) return 'ring-trust-error';
    if (confidence >= 0.70) return 'ring-trust-amber';
    return 'ring-trust-green ring-opacity-0 ring-offset-0';
  };

  const ringColor = getRingColor();
  const sizeClasses = {
    sm: 'ring-2',
    md: 'ring-4',
    lg: 'ring-6',
  };

  return (
    <div
      className={cn(
        'rounded-full transition-all duration-500',
        ringColor,
        sizeClasses[size]
      )}
    >
      {children}
    </div>
  );
}

```

# frontend/tailwind.config.ts
```ts
import type { Config } from "tailwindcss"
import tailwindcssAnimate from "tailwindcss-animate"

const config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: {
          DEFAULT: "hsl(var(--ring))",
        },
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        trust: {
          green: "hsl(var(--semantic-green))",
          amber: "hsl(var(--semantic-amber))",
          red: "hsl(var(--semantic-red))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        bounce: {
          "0%, 100%": {
            transform: "translateY(-25%)",
            animationTimingFunction: "cubic-bezier(0.8,0,1,1)",
          },
          "50%": {
            transform: "none",
            animationTimingFunction: "cubic-bezier(0,0,0.2,1)",
          },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "bounce": "bounce 1s infinite",
      },
    },
  },
  plugins: [tailwindcssAnimate],
} satisfies Config

export default config

```

