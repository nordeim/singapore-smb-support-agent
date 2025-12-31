'use client';

import * as React from 'react';
import { Trash2 } from 'lucide-react';

interface SessionPulseProps {
  expiresAt: Date;
  onExtend?: () => void;
  onWipe?: () => void;
}

export function SessionPulse({ expiresAt, onExtend, onWipe }: SessionPulseProps) {
  const [timeLeft, setTimeLeft] = React.useState(0);

  React.useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      const diff = expiresAt.getTime() - now.getTime();
      const minutes = Math.max(0, Math.floor(diff / 60000));
      setTimeLeft(minutes);
    }, 1000);

    return () => clearInterval(interval);
  }, [expiresAt]);

  const getPhase = () => {
    if (timeLeft > 15) return { color: 'bg-green-500', pulse: 'animate-pulse' };
    if (timeLeft > 5) return { color: 'bg-amber-500', pulse: 'animate-pulse' };
    return { color: 'bg-red-500', pulse: 'animate-ping' };
  };

  const phase = getPhase();

  return (
    <div className="relative">
      <div
        className={`w-3 h-3 rounded-full ${phase.color} ${phase.pulse}`}
        title={`${timeLeft} minutes remaining`}
      />
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-[10px] font-bold text-white">
          {timeLeft}m
        </span>
      </div>
    </div>
  );
}
