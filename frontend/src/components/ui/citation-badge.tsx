'use client';

import * as React from 'react';

export interface CitationBadgeProps {
  number: number;
  onClick: () => void;
}

export function CitationBadge({ number, onClick }: CitationBadgeProps) {
  return (
    <button
      onClick={onClick}
      className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-primary text-primary-foreground text-xs font-bold hover:bg-primary/80 transition-colors"
      title="View source"
      type="button"
    >
      [{number}]
    </button>
  );
}
