"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import DashboardLayout from '@/components/DashboardLayout';
import {
  DollarSign, Activity, TrendingUp, AlertCircle,
  Zap, BarChart3, Loader2, Database, Clock, Cpu,
  RefreshCw, CheckCircle2, XCircle, Brain,
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';

// ─── Types ────────────────────────────────────────────────────────────────────
interface FeatureStat {
  count: number;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  cost_usd: number;
}

interface AIStats {
  is_enabled: boolean;

  // Session (in-memory, resets on restart)
  requests_today: number;
  total_requests: number;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  total_cost_usd: number;
  avg_tokens_per_request: number;
  error_count: number;
  retry_count: number;
  error_rate_percentage: number;
  cost_per_request_usd: number;
  cost_breakdown: { input_cost_usd: number; output_cost_usd: number };
  requests_by_feature: Record<string, FeatureStat>;
  daily_limit: number;
  rate_limit_per_minute: number;
  last_reset: string;

  // Lifetime DB-backed
  lifetime_requests: number;
  lifetime_input_tokens: number;
  lifetime_output_tokens: number;
  lifetime_total_tokens: number;
  lifetime_cost_usd: number;
  lifetime_by_feature: Record<string, FeatureStat>;
  daily_usage: Record<string, number>;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
const fmt   = (n: number | undefined | null) => (n ?? 0).toLocaleString();
const fmtUSD = (n: number | undefined | null, decimals = 4) =>
  `$${(n ?? 0).toFixed(decimals)}`;
const fmtK  = (n: number) => n >= 1000 ? `${(n / 1000).toFixed(1)}K` : String(n);

const FEATURE_LABELS: Record<string, string> = {
  resume_parsing:      'Resume Parsing',
  skill_extraction:    'Skill Extraction',
  performance_insights:'Performance Insights',
  chatbot:             'AI Chatbot',
  nl_query:            'NL Query',
  talent_search:       'Talent Search',
  general:             'General',
};

const FEATURE_COLORS: Record<string, string> = {
  resume_parsing:      'bg-blue-500',
  skill_extraction:    'bg-teal-500',
  performance_insights:'bg-purple-500',
  chatbot:             'bg-indigo-500',
  nl_query:            'bg-orange-500',
  talent_search:       'bg-pink-500',
  general:             'bg-gray-400',
};

// ─── Mini bar-chart for daily usage ──────────────────────────────────────────
function DailyUsageChart({ data }: { data: Record<string, number> }) {
  const entries = Object.entries(data).sort(([a], [b]) => a.localeCompare(b));
  if (entries.length === 0) {
    return (
      <div className="flex items-center justify-center h-32 text-gray-400 text-sm">
        No usage data yet — make some AI calls first
      </div>
    );
  }
  const maxVal = Math.max(...entries.map(([, v]) => v), 1);
  return (
    <div className="flex items-end gap-1 h-32 overflow-x-auto">
      {entries.map(([day, count]) => {
        const pct = (count / maxVal) * 100;
        const label = day.slice(5); // MM-DD
        return (
          <div key={day} className="flex flex-col items-center gap-0.5 flex-1 min-w-[20px]" title={`${day}: ${count} requests`}>
            <span className="text-xs text-gray-500">{count > 0 ? count : ''}</span>
            <div
              className="w-full bg-indigo-500 rounded-t transition-all"
              style={{ height: `${Math.max(pct, 2)}%` }}
            />
            <span className="text-xs text-gray-400 rotate-45 origin-left whitespace-nowrap" style={{ fontSize: 9 }}>
              {label}
            </span>
          </div>
        );
      })}
    </div>
  );
}

// ─── Stat card ────────────────────────────────────────────────────────────────
function StatCard({
  label, value, sub, icon: Icon, color, border,
}: {
  label: string; value: string; sub?: string;
  icon: React.ElementType; color: string; border: string;
}) {
  return (
    <div className={`bg-white rounded-xl shadow p-5 border-l-4 ${border}`}>
      <div className="flex items-center justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">{label}</p>
          <p className="text-2xl font-bold text-gray-900 truncate">{value}</p>
          {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
        </div>
        <Icon className={`w-10 h-10 ${color} opacity-20 shrink-0 ml-3`} />
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────
export default function AIAnalyticsPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const [loading, setLoading]     = useState(true);
  const [stats, setStats]         = useState<AIStats | null>(null);
  const [error, setError]         = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) { router.push('/login'); return; }
    if (user?.role !== 'super_admin') { router.push('/dashboard'); return; }
    load();
  }, [isAuthenticated, user]);

  const load = async (showRefresh = false) => {
    try {
      showRefresh ? setRefreshing(true) : setLoading(true);
      setError(null);
      const res = await apiClient.get('/ai/stats/detailed');
      setStats(res.data as AIStats);
    } catch (err: any) {
      const msg = err?.response?.data?.detail ?? err?.message ?? 'Failed to load AI analytics';
      setError(msg);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <Loader2 className="animate-spin h-12 w-12 text-indigo-600 mx-auto" />
            <p className="mt-4 text-gray-600">Loading AI analytics…</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  // ── Derived values — safe even when stats is null ─────────────────────────
  const s = stats;
  const lifetimeFeatures = Object.entries(s?.lifetime_by_feature ?? {}).sort(
    ([, a], [, b]) => b.cost_usd - a.cost_usd
  );
  const sessionFeatures = Object.entries(s?.requests_by_feature ?? {}).sort(
    ([, a], [, b]) => b.count - a.count
  );
  const totalLifetimeCost = s?.lifetime_cost_usd ?? 0;
  const dailyBars  = s?.daily_usage ?? {};
  const dailyCount = Object.keys(dailyBars).length;

  return (
    <DashboardLayout>
      <div className="space-y-6 p-6 bg-gray-50 min-h-screen">

        {/* ── Header ─────────────────────────────────────────────────────── */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Cost Analytics</h1>
            <p className="text-sm text-gray-500 mt-0.5">
              Model: <strong>gpt-4.1-mini</strong> via Azure AI Foundry ·
              $0.40/1M input · $1.60/1M output
            </p>
          </div>
          <div className="flex items-center gap-3">
            {s?.is_enabled ? (
              <span className="px-3 py-1.5 bg-green-100 text-green-800 rounded-lg flex items-center gap-1.5 text-sm font-medium">
                <CheckCircle2 className="w-4 h-4" /> AI Enabled
              </span>
            ) : (
              <span className="px-3 py-1.5 bg-red-100 text-red-800 rounded-lg flex items-center gap-1.5 text-sm font-medium">
                <XCircle className="w-4 h-4" /> AI Disabled
              </span>
            )}
            <button
              onClick={() => load(true)}
              disabled={refreshing}
              className="px-3 py-1.5 bg-white border border-gray-300 rounded-lg flex items-center gap-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {/* ── LIFETIME STATS (from DB) ────────────────────────────────────── */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Database className="w-4 h-4 text-indigo-600" />
            <h2 className="text-sm font-bold text-gray-700 uppercase tracking-wide">
              Lifetime Totals (Database)
            </h2>
            <span className="text-xs text-gray-400">— persists across server restarts</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              label="Lifetime Cost"
              value={fmtUSD(totalLifetimeCost, 4)}
              sub="All-time AI spend"
              icon={DollarSign}
              color="text-emerald-500"
              border="border-emerald-500"
            />
            <StatCard
              label="Lifetime Requests"
              value={fmt(s?.lifetime_requests)}
              sub="Total API calls made"
              icon={Activity}
              color="text-blue-500"
              border="border-blue-500"
            />
            <StatCard
              label="Total Tokens"
              value={fmtK(s?.lifetime_total_tokens ?? 0)}
              sub={`In: ${fmtK(s?.lifetime_input_tokens ?? 0)} · Out: ${fmtK(s?.lifetime_output_tokens ?? 0)}`}
              icon={Cpu}
              color="text-purple-500"
              border="border-purple-500"
            />
            <StatCard
              label="Avg Cost / Request"
              value={s?.lifetime_requests
                ? fmtUSD(totalLifetimeCost / s.lifetime_requests, 6)
                : '$0.000000'}
              sub="All-time average"
              icon={TrendingUp}
              color="text-orange-500"
              border="border-orange-500"
            />
          </div>
        </div>

        {/* ── SESSION STATS (in-memory) ───────────────────────────────────── */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Clock className="w-4 h-4 text-gray-500" />
            <h2 className="text-sm font-bold text-gray-700 uppercase tracking-wide">
              Current Session
            </h2>
            <span className="text-xs text-gray-400">— resets when server restarts</span>
            {s?.last_reset && (
              <span className="text-xs text-gray-400">
                (last reset: {new Date(s.last_reset).toLocaleString()})
              </span>
            )}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              label="Session Cost"
              value={fmtUSD(s?.total_cost_usd, 4)}
              sub="Since last restart"
              icon={DollarSign}
              color="text-green-500"
              border="border-green-500"
            />
            <StatCard
              label="Requests (Session)"
              value={fmt(s?.requests_today)}
              sub={`Limit: ${fmt(s?.daily_limit)}/day`}
              icon={Activity}
              color="text-blue-500"
              border="border-blue-500"
            />
            <StatCard
              label="Error Rate"
              value={`${(s?.error_rate_percentage ?? 0).toFixed(1)}%`}
              sub={`${s?.error_count ?? 0} errors · ${s?.retry_count ?? 0} retries`}
              icon={AlertCircle}
              color="text-red-500"
              border="border-red-500"
            />
            <StatCard
              label="Avg Tokens/Req"
              value={fmt(Math.round(s?.avg_tokens_per_request ?? 0))}
              sub={`Rate limit: ${s?.rate_limit_per_minute ?? 0}/min`}
              icon={Zap}
              color="text-yellow-500"
              border="border-yellow-500"
            />
          </div>
        </div>

        {/* ── Two-column: feature table + daily chart ─────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* Feature breakdown (DB lifetime) */}
          <div className="bg-white rounded-xl shadow border border-gray-100 overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-2">
              <Brain className="w-4 h-4 text-indigo-600" />
              <h3 className="font-semibold text-gray-900 text-sm">Cost by Feature (Lifetime)</h3>
            </div>
            {lifetimeFeatures.length === 0 ? (
              <div className="p-6 text-center text-gray-400 text-sm">
                No DB data yet — start using AI features and refresh
              </div>
            ) : (
              <div className="divide-y divide-gray-50">
                {lifetimeFeatures.map(([feat, d]) => {
                  const pct = totalLifetimeCost > 0
                    ? (d.cost_usd / totalLifetimeCost) * 100
                    : 0;
                  const barColor = FEATURE_COLORS[feat] ?? 'bg-gray-400';
                  return (
                    <div key={feat} className="px-5 py-3">
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          <span className={`w-2 h-2 rounded-full ${barColor}`} />
                          <span className="text-sm font-medium text-gray-800">
                            {FEATURE_LABELS[feat] ?? feat}
                          </span>
                          <span className="text-xs text-gray-400">{fmt(d.count)} calls</span>
                        </div>
                        <span className="text-sm font-bold text-gray-900">
                          {fmtUSD(d.cost_usd, 4)}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${barColor} rounded-full`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-400 w-10 text-right">{pct.toFixed(1)}%</span>
                      </div>
                      <div className="flex gap-3 mt-1 text-xs text-gray-400">
                        <span>In: {fmtK(d.input_tokens)}</span>
                        <span>Out: {fmtK(d.output_tokens)}</span>
                        <span>Total: {fmtK(d.total_tokens)} tok</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Daily usage chart */}
          <div className="bg-white rounded-xl shadow border border-gray-100 overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-indigo-600" />
                <h3 className="font-semibold text-gray-900 text-sm">
                  Daily Requests ({dailyCount} days)
                </h3>
              </div>
              <span className="text-xs text-gray-400">last 30 days</span>
            </div>
            <div className="px-5 py-4">
              <DailyUsageChart data={dailyBars} />
            </div>
            {/* Token cost summary */}
            <div className="grid grid-cols-2 divide-x divide-gray-100 border-t border-gray-100">
              <div className="px-5 py-3">
                <p className="text-xs text-gray-500">Input tokens (lifetime)</p>
                <p className="font-bold text-gray-900">{fmtK(s?.lifetime_input_tokens ?? 0)}</p>
                <p className="text-xs text-green-600 font-medium">
                  {fmtUSD((s?.lifetime_input_tokens ?? 0) / 1_000_000 * 0.40, 4)}
                </p>
              </div>
              <div className="px-5 py-3">
                <p className="text-xs text-gray-500">Output tokens (lifetime)</p>
                <p className="font-bold text-gray-900">{fmtK(s?.lifetime_output_tokens ?? 0)}</p>
                <p className="text-xs text-green-600 font-medium">
                  {fmtUSD((s?.lifetime_output_tokens ?? 0) / 1_000_000 * 1.60, 4)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* ── Session feature breakdown ────────────────────────────────────── */}
        {sessionFeatures.length > 0 && (
          <div className="bg-white rounded-xl shadow border border-gray-100 overflow-hidden">
            <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-2">
              <Clock className="w-4 h-4 text-gray-500" />
              <h3 className="font-semibold text-gray-900 text-sm">Session Feature Breakdown</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    <th className="text-left px-5 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Feature</th>
                    <th className="text-right px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Calls</th>
                    <th className="text-right px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Input Tok</th>
                    <th className="text-right px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Output Tok</th>
                    <th className="text-right px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Total Tok</th>
                    <th className="text-right px-5 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">Cost (USD)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {sessionFeatures.map(([feat, d]) => (
                    <tr key={feat} className="hover:bg-gray-50 transition-colors">
                      <td className="px-5 py-3 font-medium text-gray-900">
                        <div className="flex items-center gap-2">
                          <span className={`w-2 h-2 rounded-full ${FEATURE_COLORS[feat] ?? 'bg-gray-400'}`} />
                          {FEATURE_LABELS[feat] ?? feat}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-right text-gray-700">{fmt(d.count)}</td>
                      <td className="px-4 py-3 text-right text-gray-700">{fmtK(d.input_tokens)}</td>
                      <td className="px-4 py-3 text-right text-gray-700">{fmtK(d.output_tokens)}</td>
                      <td className="px-4 py-3 text-right text-gray-700">{fmtK(d.total_tokens)}</td>
                      <td className="px-5 py-3 text-right font-semibold text-emerald-700">
                        {fmtUSD(d.cost_usd, 6)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ── Pricing reference ────────────────────────────────────────────── */}
        <div className="bg-gradient-to-r from-indigo-50 to-blue-50 border border-indigo-100 rounded-xl p-5">
          <div className="flex items-start gap-3">
            <Brain className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
            <div>
              <h3 className="font-bold text-indigo-900 mb-2">Azure AI Foundry Pricing — gpt-4.1-mini</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                <div className="bg-white rounded-lg p-3 border border-indigo-100">
                  <p className="text-indigo-600 font-semibold">Input tokens</p>
                  <p className="text-xl font-bold text-gray-900">$0.40</p>
                  <p className="text-xs text-gray-500">per 1M tokens</p>
                </div>
                <div className="bg-white rounded-lg p-3 border border-indigo-100">
                  <p className="text-indigo-600 font-semibold">Output tokens</p>
                  <p className="text-xl font-bold text-gray-900">$1.60</p>
                  <p className="text-xs text-gray-500">per 1M tokens</p>
                </div>
                <div className="bg-white rounded-lg p-3 border border-indigo-100">
                  <p className="text-indigo-600 font-semibold">1000 resumes</p>
                  <p className="text-xl font-bold text-gray-900">~$1.60</p>
                  <p className="text-xs text-gray-500">estimated</p>
                </div>
                <div className="bg-white rounded-lg p-3 border border-indigo-100">
                  <p className="text-indigo-600 font-semibold">1000 chatbot msgs</p>
                  <p className="text-xl font-bold text-gray-900">~$0.40</p>
                  <p className="text-xs text-gray-500">estimated</p>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </DashboardLayout>
  );
}
