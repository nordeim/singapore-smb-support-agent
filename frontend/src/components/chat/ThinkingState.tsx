'use client';

import * as React from 'react';
import { Loader2 } from 'lucide-react';

interface ThinkingStateProps {
  isThinking: boolean;
}

const THOUGHT_STEPS = [
  { text: "Scanning Knowledge Base...", icon: Loader2 },
  { text: "Cross-referencing Policies...", icon: Loader2 },
  { text: "Formatting Response...", icon: Loader2 },
];

export function ThinkingState({ isThinking }: ThinkingStateProps) {
  const [currentStep, setCurrentStep] = React.useState(0);

  React.useEffect(() => {
    if (isThinking) {
      const interval = setInterval(() => {
        setCurrentStep((prev) => (prev + 1) % THOUGHT_STEPS.length);
      }, 2000); // 2s per step
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
