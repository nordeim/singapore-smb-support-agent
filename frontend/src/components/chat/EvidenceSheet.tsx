'use client';

import * as React from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { Copy, Check } from 'lucide-react';
import type { Source } from '@/types';

export interface EvidenceSheetProps {
  source: Source;
  isOpen: boolean;
  onClose: () => void;
}

export function EvidenceSheet({ source, isOpen, onClose }: EvidenceSheetProps) {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(source.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  return (
    <Sheet open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <SheetContent className="max-w-2xl">
        <SheetHeader>
          <SheetTitle>Source Evidence</SheetTitle>
        </SheetHeader>
        <div className="p-6 space-y-4">
          <div className="space-y-2">
            <div className="text-sm text-muted-foreground">
              File: {source.metadata?.file_name || 'Unknown'}
            </div>
            <div className="text-sm text-muted-foreground">
              Confidence: {(source.score * 100).toFixed(1)}%
            </div>
          </div>

          <div className="bg-muted rounded-lg p-4 font-mono text-sm">
            {source.content}
          </div>

          <button
            onClick={handleCopy}
            className="w-full flex items-center justify-center gap-2 rounded-md border border-input bg-background px-4 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors"
            type="button"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4 text-green-500" />
                <span>Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span>Copy Source Text</span>
              </>
            )}
          </button>
        </div>
      </SheetContent>
    </Sheet>
  );
}
