import * as React from 'react';
import { cn } from '@/lib/utils';
import { ScrollAreaProps as RadixScrollAreaProps } from '@radix-ui/react-scroll-area';
import { ScrollArea as RadixScrollArea } from '@radix-ui/react-scroll-area';

const ScrollArea = React.forwardRef<
  HTMLDivElement,
  RadixScrollAreaProps
>(({ className, children, ...props }, ref) => (
  <RadixScrollArea
    ref={ref}
    className={cn('relative overflow-hidden', className)}
    {...props}
  >
    <RadixScrollArea.Viewport className="h-full w-full rounded-[inherit]">
      {children}
    </RadixScrollArea.Viewport>
    <RadixScrollArea.Scrollbar
      className="flex touch-none select-none transition-colors"
      orientation="vertical"
    >
      <RadixScrollArea.Thumb className="relative flex-1 w-2.5 rounded-full bg-border" />
    </RadixScrollArea.Scrollbar>
    <RadixScrollArea.Scrollbar
      className="flex touch-none select-none transition-colors"
      orientation="horizontal"
    >
      <RadixScrollArea.Thumb className="relative flex-1 h-2.5 rounded-full bg-border" />
    </RadixScrollArea.Scrollbar>
  </RadixScrollArea>
));
ScrollArea.displayName = 'ScrollArea';

export { ScrollArea };
