'use client';

import { useEffect, useState } from 'react';
import { Loader2, Sparkles } from 'lucide-react';

const maverickQuotes = [
  "Every expert was once a beginner. Your journey starts here.",
  "Innovation distinguishes between a leader and a follower.",
  "The future belongs to those who believe in their dreams.",
  "Your potential is limitless. We're here to unlock it.",
  "Great things never come from comfort zones.",
  "Be the Maverick the world needs.",
  "Success is the sum of small efforts repeated day in and day out.",
  "The only way to do great work is to love what you do.",
  "Dream big, start small, act now.",
  "Your attitude determines your direction.",
];

interface LoadingScreenProps {
  message?: string;
}

export default function LoadingScreen({ message = 'Loading...' }: LoadingScreenProps) {
  const [currentQuote, setCurrentQuote] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentQuote((prev) => (prev + 1) % maverickQuotes.length);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed inset-0 bg-gray-50 flex items-center justify-center z-50">
      {/* Content */}
      <div className="relative z-10 text-center space-y-8 px-4">
        {/* Logo */}
        <div className="mb-4">
          <h1 className="text-4xl font-black text-blue-900 uppercase tracking-tight">
            MAVERICKS ASCEND
          </h1>
        </div>

        {/* Spinner */}
        <div className="flex justify-center">
          <div className="relative">
            <Loader2 className="w-16 h-16 text-blue-900 animate-spin" />
            <Sparkles className="w-6 h-6 text-blue-700 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 animate-pulse" />
          </div>
        </div>

        {/* Message */}
        <div className="space-y-4">
          <p className="text-gray-700 text-lg font-semibold">{message}</p>

          {/* Motivational Quote */}
          <div className="max-w-md mx-auto">
            <p className="text-gray-600 italic text-sm transition-all duration-500">
              "{maverickQuotes[currentQuote]}"
            </p>
          </div>
        </div>

        {/* Loading dots */}
        <div className="flex justify-center gap-2">
          <div className="w-2.5 h-2.5 bg-blue-900 rounded-full animate-bounce"></div>
          <div className="w-2.5 h-2.5 bg-blue-700 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2.5 h-2.5 bg-blue-900 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
      </div>
    </div>
  );
}
