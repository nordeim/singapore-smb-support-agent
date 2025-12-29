import * as React from 'react';
import { Clock, Globe } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useChatStore } from '@/stores/chatStore';
import type { BusinessHours } from '@/types';

export function ChatHeader() {
  const { connectionStatus } = useChatStore();

  const getBusinessHours = (): BusinessHours => {
    const now = new Date();
    const hour = now.getHours();
    const isBusinessHours = hour >= 9 && hour < 18;
    const day = now.toLocaleDateString('en-SG', { weekday: 'long' });
    const time = now.toLocaleTimeString('en-SG', {
      hour: '2-digit',
      minute: '2-digit',
    });

    return {
      is_open: isBusinessHours,
      business_hours: '9:00 AM - 6:00 PM (SGT)',
      current_time: time,
      timezone: 'Asia/Singapore',
    };
  };

  const hours = getBusinessHours();
  const isConnected = connectionStatus === 'connected';
  const isOnline = hours.is_open && isConnected;

  const statusColor = isOnline ? 'bg-green-500' : 'bg-amber-500';

  return (
    <CardHeader className="px-6 py-4 border-b">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${statusColor}`} />
            <span className="font-semibold">
              Singapore SMB Support Agent
            </span>
          </div>

          <Badge
            variant={isOnline ? 'default' : 'outline'}
            className={isOnline ? 'bg-primary' : 'bg-secondary'}
          >
            {isOnline ? 'Online' : 'Offline'}
          </Badge>
        </div>

        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <Clock className="w-4 h-4" />
            <span>{hours.business_hours}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Globe className="w-4 h-4" />
            <span>{hours.timezone}</span>
          </div>
          <div className="text-xs">
            {hours.current_time}
          </div>
        </div>
      </div>
    </CardHeader>
  );
}
