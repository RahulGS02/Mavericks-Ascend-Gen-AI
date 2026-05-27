"use client";

import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuthStore } from '@/store/authStore';
import { chatbotAPI, ChatMessage } from '@/lib/api';
import {
  MessageCircle, X, Send, Loader2, Sparkles,
  ChevronDown, RotateCcw, Database, Bot,
} from 'lucide-react';

// ─── Role colours ──────────────────────────────────────────────────────────
const ROLE_THEME: Record<string, { bg: string; light: string; label: string }> = {
  maverick:    { bg: 'from-blue-600 to-indigo-600',    light: 'bg-blue-50',   label: 'Maverick Guide' },
  trainer:     { bg: 'from-green-600 to-teal-600',     light: 'bg-green-50',  label: 'Trainer Guide'  },
  hr:          { bg: 'from-purple-600 to-pink-600',    light: 'bg-purple-50', label: 'HR Guide'       },
  manager:     { bg: 'from-orange-600 to-red-600',     light: 'bg-orange-50', label: 'Manager Guide'  },
  super_admin: { bg: 'from-gray-700 to-gray-900',      light: 'bg-gray-50',   label: 'Admin Guide'    },
};

// ─── Simple markdown renderer ─────────────────────────────────────────────
function renderMarkdown(text: string) {
  const lines = text.split('\n');
  const elements: React.ReactNode[] = [];
  let key = 0;

  for (const line of lines) {
    const k = key++;
    // Numbered list
    const numMatch = line.match(/^(\d+)\.\s+(.+)/);
    if (numMatch) {
      elements.push(
        <div key={k} className="flex gap-2 mt-1">
          <span className="font-semibold text-blue-600 shrink-0">{numMatch[1]}.</span>
          <span>{renderInline(numMatch[2])}</span>
        </div>
      );
      continue;
    }
    // Bullet list
    const bulletMatch = line.match(/^[-•]\s+(.+)/);
    if (bulletMatch) {
      elements.push(
        <div key={k} className="flex gap-2 mt-1">
          <span className="text-blue-500 shrink-0">•</span>
          <span>{renderInline(bulletMatch[1])}</span>
        </div>
      );
      continue;
    }
    // Arrow steps
    const arrowMatch = line.match(/^→\s+(.+)/);
    if (arrowMatch) {
      elements.push(
        <div key={k} className="flex gap-2 mt-1 text-gray-700">
          <span className="text-indigo-500 shrink-0">→</span>
          <span>{renderInline(arrowMatch[1])}</span>
        </div>
      );
      continue;
    }
    // Empty line
    if (line.trim() === '') {
      elements.push(<div key={k} className="h-1" />);
      continue;
    }
    // Normal paragraph
    elements.push(<p key={k} className="mt-1">{renderInline(line)}</p>);
  }
  return <>{elements}</>;
}

function renderInline(text: string): React.ReactNode {
  // Bold: **text**
  const parts = text.split(/\*\*(.+?)\*\*/g);
  return parts.map((p, i) =>
    i % 2 === 1
      ? <strong key={i} className="font-semibold">{p}</strong>
      : <span key={i}>{p}</span>
  );
}

// ─── Mini data table ─────────────────────────────────────────────────────
function DataTable({ data }: { data: Record<string, any>[] }) {
  if (!data || data.length === 0) return null;
  const cols = Object.keys(data[0]).slice(0, 6); // max 6 columns
  const rows = data.slice(0, 8);                  // max 8 rows in chat

  return (
    <div className="mt-2 overflow-x-auto rounded border border-gray-200 text-xs">
      <table className="w-full">
        <thead className="bg-gray-100">
          <tr>
            {cols.map(c => (
              <th key={c} className="px-2 py-1 text-left font-semibold text-gray-600 whitespace-nowrap">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
              {cols.map(c => (
                <td key={c} className="px-2 py-1 text-gray-800 whitespace-nowrap max-w-[120px] truncate">
                  {row[c] !== null && row[c] !== undefined ? String(row[c]) : '—'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {data.length > 8 && (
        <p className="px-2 py-1 text-gray-500 bg-gray-50 border-t">
          … and {data.length - 8} more rows
        </p>
      )}
    </div>
  );
}

// ─── Message bubble ────────────────────────────────────────────────────────
interface BubbleProps {
  msg: ChatMessage & {
    type?: string;
    data?: Record<string, any>[];
    data_count?: number;
  };
  theme: typeof ROLE_THEME[string];
}

function MessageBubble({ msg, theme }: BubbleProps) {
  const isUser = msg.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
      {!isUser && (
        <div className={`w-7 h-7 rounded-full bg-gradient-to-br ${theme.bg} flex items-center justify-center mr-2 mt-1 shrink-0`}>
          <Bot className="w-4 h-4 text-white" />
        </div>
      )}
      <div className={`max-w-[85%] ${isUser ? 'order-1' : ''}`}>
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm
            ${isUser
              ? `bg-gradient-to-br ${theme.bg} text-white rounded-tr-sm`
              : `bg-white border border-gray-100 text-gray-800 rounded-tl-sm`
            }`}
        >
          {isUser
            ? msg.content
            : renderMarkdown(msg.content)
          }
        </div>

        {/* Analytics data table */}
        {!isUser && msg.type === 'analytics' && msg.data && (
          <div className="mt-1">
            <div className="flex items-center gap-1 text-xs text-purple-600 mb-1 px-1">
              <Database className="w-3 h-3" />
              <span>Live data — {msg.data_count ?? msg.data.length} records</span>
            </div>
            <DataTable data={msg.data} />
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Main ChatBot widget ───────────────────────────────────────────────────
export default function ChatBot() {
  const { user } = useAuthStore();
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(true);

  // Extended message type that carries analytics payload
  type ExtendedMessage = ChatMessage & {
    type?: string;
    data?: Record<string, any>[];
    data_count?: number;
  };

  const [messages, setMessages] = useState<ExtendedMessage[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef  = useRef<HTMLInputElement>(null);

  const role  = user?.role ?? 'maverick';
  const theme = ROLE_THEME[role] ?? ROLE_THEME.maverick;

  // Fetch suggestions on mount
  useEffect(() => {
    if (!user) return;
    chatbotAPI.getSuggestions()
      .then(res => setSuggestions(res.data?.suggestions ?? []))
      .catch(() => {});
  }, [user]);

  // Greet user when chat opens for the first time
  useEffect(() => {
    if (open && messages.length === 0) {
      const greeting: ExtendedMessage = {
        role: 'assistant',
        content: `Hi ${user?.name?.split(' ')[0] ?? 'there'}! 👋 I'm your personal ${theme.label}.\n\nI can help you navigate the app, explain features, and${role === 'hr' || role === 'super_admin' ? ' answer analytical questions with live data.' : ' answer any questions about what you can do here.'}\n\nWhat can I help you with?`,
      };
      setMessages([greeting]);
    }
  }, [open]);

  // Auto-scroll on new message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Focus input when opening
  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 100);
  }, [open]);

  const sendMessage = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setInput('');
    setShowSuggestions(false);

    const userMsg: ExtendedMessage = { role: 'user', content: trimmed };
    const history = messages.filter(m => m.role === 'user' || m.role === 'assistant');
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await chatbotAPI.sendMessage(trimmed, history);
      const body = res.data;

      const assistantMsg: ExtendedMessage = {
        role: 'assistant',
        content: body.response,
        type: body.type,
        data: body.data,
        data_count: body.data_count,
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err: any) {
      const errMsg: ExtendedMessage = {
        role: 'assistant',
        content: 'Sorry, I ran into an issue. Please try again in a moment.',
        type: 'general',
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  }, [messages, loading]);

  const clearChat = () => {
    setMessages([]);
    setShowSuggestions(true);
  };

  if (!user) return null;

  return (
    <>
      {/* ── Floating button ─────────────────────────────────────────── */}
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className={`fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-gradient-to-br ${theme.bg}
            shadow-lg hover:shadow-xl transition-all hover:scale-110 flex items-center justify-center
            text-white group`}
          aria-label="Open AI assistant"
        >
          <MessageCircle className="w-6 h-6" />
          <span className={`absolute -top-1 -right-1 w-4 h-4 rounded-full bg-green-400 border-2 border-white`} />
        </button>
      )}

      {/* ── Chat panel ──────────────────────────────────────────────── */}
      {open && (
        <div className="fixed bottom-6 right-6 z-50 flex flex-col w-[380px] max-w-[95vw] h-[600px] max-h-[85vh] rounded-2xl shadow-2xl overflow-hidden bg-white border border-gray-200">

          {/* Header */}
          <div className={`bg-gradient-to-r ${theme.bg} px-4 py-3 flex items-center justify-between shrink-0`}>
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-sm font-bold text-white">{theme.label}</p>
                <p className="text-xs text-white/70">AI-powered · Always here to help</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={clearChat}
                className="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white transition-colors"
                title="Clear chat"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
              <button
                onClick={() => setOpen(false)}
                className="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white transition-colors"
                title="Close"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Messages area */}
          <div className="flex-1 overflow-y-auto px-4 py-3 bg-gray-50">
            {messages.map((msg, i) => (
              <MessageBubble key={i} msg={msg} theme={theme} />
            ))}

            {/* Typing indicator */}
            {loading && (
              <div className="flex items-center gap-2 mb-3">
                <div className={`w-7 h-7 rounded-full bg-gradient-to-br ${theme.bg} flex items-center justify-center shrink-0`}>
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="bg-white rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm border border-gray-100">
                  <div className="flex gap-1 items-center h-4">
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Suggestions */}
          {showSuggestions && suggestions.length > 0 && messages.length <= 1 && (
            <div className={`${theme.light} px-3 py-2 border-t border-gray-100 shrink-0`}>
              <p className="text-xs text-gray-500 mb-1.5 font-medium">Try asking:</p>
              <div className="flex flex-col gap-1">
                {suggestions.slice(0, 3).map((s, i) => (
                  <button
                    key={i}
                    onClick={() => sendMessage(s)}
                    className="text-left text-xs px-3 py-1.5 rounded-lg bg-white border border-gray-200 hover:border-blue-300 hover:bg-blue-50 text-gray-700 transition-colors truncate"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input bar */}
          <div className="px-3 py-3 bg-white border-t border-gray-100 shrink-0">
            <div className="flex items-center gap-2 bg-gray-100 rounded-xl px-3 py-2">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage(input);
                  }
                }}
                placeholder="Ask me anything…"
                disabled={loading}
                className="flex-1 bg-transparent text-sm text-gray-800 placeholder-gray-400 outline-none disabled:opacity-50"
              />
              <button
                onClick={() => sendMessage(input)}
                disabled={loading || !input.trim()}
                className={`w-8 h-8 rounded-lg bg-gradient-to-br ${theme.bg} flex items-center justify-center text-white disabled:opacity-40 transition-opacity shrink-0`}
              >
                {loading
                  ? <Loader2 className="w-4 h-4 animate-spin" />
                  : <Send className="w-4 h-4" />
                }
              </button>
            </div>
            <p className="text-center text-xs text-gray-400 mt-1">
              Powered by Azure AI · gpt-4.1-mini
            </p>
          </div>
        </div>
      )}
    </>
  );
}
