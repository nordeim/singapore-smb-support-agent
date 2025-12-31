'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { X } from 'lucide-react';
import type { ReactNode } from 'react';

const Sheet = React.forwardRef<
  HTMLDivElement,
  {
    open?: boolean;
    onOpenChange?: (open: boolean) => void;
    children?: ReactNode;
  }
>(({ className, open, onOpenChange, children, ...props }, ref) => {
  return (
    <div
      ref={ref}
      {...props}
      className={cn(className)}
      style={{
        display: open ? 'block' : 'none',
      }}
    >
      {children}
    </div>
  );
});
Sheet.displayName = 'Sheet';

const SheetTrigger = React.forwardRef<HTMLButtonElement, React.ButtonHTMLAttributes<HTMLButtonElement>>(
  ({ className, ...props }, ref) => (
    <button
      ref={ref}
      className={cn(className)}
      {...props}
    >
      {props.children}
    </button>
  )
);
SheetTrigger.displayName = 'SheetTrigger';

const SheetContent = React.forwardRef<
  HTMLDivElement,
  {
    children?: ReactNode;
    onClose?: () => void;
  }
>(({ className, children, onClose, ...props }, ref) => (
    <div
      ref={ref}
      {...props}
      className={cn(
        'fixed inset-0 z-50 flex',
        'bg-background/95 backdrop-blur-sm',
        'p-6',
        className
      )}
    >
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">Evidence</h2>
        <button
          onClick={onClose}
          className="text-muted-foreground hover:text-foreground transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
      <div className="max-h-[70vh] overflow-y-auto">
        {children}
      </div>
    </div>
  );
});
SheetContent.displayName = 'SheetContent';

const SheetHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      {...props}
      className={cn(className)}
    >
      {props.children}
    </div>
  );
});
SheetHeader.displayName = 'SheetHeader';

const SheetTitle = React.forwardRef<HTMLHeadingElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3
      ref={ref}
      {...props}
      className={cn('text-lg font-semibold', className)}
    >
      {props.children}
    </h3>
  );
});
SheetTitle.displayName = 'SheetTitle';

export { Sheet, SheetTrigger, SheetContent, SheetHeader, SheetTitle };
