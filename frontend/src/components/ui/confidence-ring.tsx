'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

export interface ConfidenceRingProps {
  confidence: number;
  size?: 'sm' | 'md' | 'lg';
}

export function ConfidenceRing({ confidence, size = 'md' }: ConfidenceRingProps) {
  const getRingColor = () => {
    if (confidence >= 0.85) return 'ring-green-500';
    if (confidence >= 0.70) return 'ring-amber-500';
    return 'ring-red-500 ring-opacity-0 ring-offset-0';
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
