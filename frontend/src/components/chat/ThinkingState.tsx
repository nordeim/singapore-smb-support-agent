'use client';

import * as React from 'react';
import { Loader2 } from 'lucide-react';

interface ThinkingStateProps {
  isThinking: boolean;
}

const THOUGHT_STEPS = [
  { text: "Scanning Knowledge Base..." },
  { text: "Cross-referencing Policies..." },
  { text: "Formatting Response..." },
];

function ThinkingDots() {
  return (
    <div className="flex gap-1">
      <div className="w-1.5 h-1.5 rounded-full bg-foreground/40 animate-bounce" style={{ animationDelay: '0ms' }} />
      <div className="w-1.5 h-1.5 rounded-full bg-foreground/40 animate-bounce" style={{ animationDelay: '150ms' }} />
      <div className="w-1.5 h-1.5 rounded-full bg-foreground/40 animate-bounce" style={{ animationDelay: '300ms' }} />
    </div>
  );
}

export function ThinkingState({ isThinking }: ThinkingStateProps) {
  const [currentStep, setCurrentStep] = React.useState(0);

  React.useEffect(() => {
    if (isThinking) {
      const interval = setInterval(() => {
        setCurrentStep((prev) => (prev + 1) % THOUGHT_STEPS.length);
      }, 2000);
      return () => clearInterval(interval);
    } else {
      setCurrentStep(0);
    }
  }, [isThinking]);

  if (!isThinking) return null;

  return (
    <div className="flex items-center gap-2 text-xs text-muted-foreground">
      <div className="flex gap-1">
        <ThinkingDots />
      </div>
      <span>{THOUGHT_STEPS[currentStep].text}</span>
    </div>
  );
}
