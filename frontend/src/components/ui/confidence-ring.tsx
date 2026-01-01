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
    if (confidence >= 0.85) return 'ring-trust-green';
    if (confidence >= 0.70) return 'ring-trust-amber';
    return 'ring-trust-red';
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
