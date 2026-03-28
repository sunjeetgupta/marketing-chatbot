import { Target, TrendingUp, Calendar, DollarSign, BarChart2, CheckCircle, AlertTriangle, Zap } from 'lucide-react'

export default function StrategyPanel({ strategy }) {
  if (!strategy) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center px-8">
        <div className="w-16 h-16 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center mb-4">
          <Target className="w-8 h-8 text-slate-600" />
        </div>
        <h3 className="text-slate-400 font-medium mb-1">No Strategy Yet</h3>
        <p className="text-sm text-slate-600">Submit a campaign brief to generate your strategy</p>
      </div>
    )
  }

  return (
    <div className="p-5 space-y-5 overflow-y-auto h-full">
      {/* Campaign Header */}
      <div className="glass-card p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <span className="inline-block text-xs font-medium bg-brand/10 text-brand border border-brand/20 px-2.5 py-0.5 rounded-full mb-2 capitalize">
              {strategy.campaign_type?.replace('_', ' ')}
            </span>
            <h2 className="text-xl font-bold text-white mb-1">{strategy.campaign_name}</h2>
            <p className="text-sm text-slate-400">{strategy.unique_value_proposition}</p>
          </div>
        </div>
      </div>

      {/* Objectives */}
      <Section icon={<Target className="w-4 h-4" />} title="Campaign Objectives" color="brand">
        <ul className="space-y-2">
          {(strategy.objectives || []).map((obj, i) => (
            <li key={i} className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-success mt-0.5 flex-shrink-0" />
              <span className="text-sm text-slate-300">{obj}</span>
            </li>
          ))}
        </ul>
      </Section>

      {/* Key Messages */}
      <Section icon={<Zap className="w-4 h-4" />} title="Key Messages" color="purple">
        <div className="flex flex-wrap gap-2">
          {(strategy.key_messages || []).map((msg, i) => (
            <span key={i} className="text-xs bg-purple-500/10 border border-purple-500/20 text-purple-300 px-3 py-1.5 rounded-full">
              {msg}
            </span>
          ))}
        </div>
      </Section>

      {/* Channels */}
      <Section icon={<BarChart2 className="w-4 h-4" />} title="Channel Strategy" color="cyan">
        <div className="space-y-3">
          {(strategy.channels || []).map((ch, i) => (
            <div key={i} className="flex items-center gap-3">
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-slate-200">{ch.name}</span>
                  <span className="text-xs text-slate-400">{ch.budget_pct}%</span>
                </div>
                <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-brand"
                    style={{ width: `${ch.budget_pct}%` }}
                  />
                </div>
                {ch.rationale && (
                  <p className="text-xs text-slate-500 mt-1">{ch.rationale}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </Section>

      {/* Timeline Phases */}
      {strategy.phases && strategy.phases.length > 0 && (
        <Section icon={<Calendar className="w-4 h-4" />} title={`Timeline (${strategy.timeline_weeks || '?'} weeks)`} color="emerald">
          <div className="space-y-3">
            {strategy.phases.map((phase, i) => (
              <div key={i} className="pl-4 border-l-2 border-emerald-500/30">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span className="text-sm font-semibold text-slate-200">{phase.phase}</span>
                  <span className="text-xs text-slate-500">({phase.duration})</span>
                </div>
                <ul className="space-y-0.5 ml-4">
                  {(phase.activities || []).slice(0, 3).map((act, j) => (
                    <li key={j} className="text-xs text-slate-400">• {act}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* KPIs */}
      <Section icon={<TrendingUp className="w-4 h-4" />} title="KPIs & Targets" color="orange">
        <div className="grid grid-cols-2 gap-2">
          {(strategy.kpis || []).slice(0, 6).map((kpi, i) => (
            <div key={i} className="bg-slate-800/50 rounded-xl p-3 border border-slate-700/50">
              <p className="text-xs text-slate-500 mb-0.5">{kpi.metric}</p>
              <p className="text-sm font-bold text-orange-400">{kpi.target}</p>
              {kpi.measurement && <p className="text-xs text-slate-600 mt-0.5 truncate">{kpi.measurement}</p>}
            </div>
          ))}
        </div>
      </Section>

      {/* Risk Factors */}
      {strategy.risk_factors && strategy.risk_factors.length > 0 && (
        <Section icon={<AlertTriangle className="w-4 h-4" />} title="Risk Factors" color="warning">
          <ul className="space-y-1.5">
            {strategy.risk_factors.map((risk, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-400">
                <span className="text-warning mt-0.5">⚠</span> {risk}
              </li>
            ))}
          </ul>
        </Section>
      )}
    </div>
  )
}

function Section({ icon, title, color, children }) {
  const colorMap = {
    brand: 'text-brand',
    purple: 'text-purple-400',
    cyan: 'text-cyan-400',
    emerald: 'text-emerald-400',
    orange: 'text-orange-400',
    warning: 'text-warning',
  }
  return (
    <div className="glass-card p-4">
      <div className="flex items-center gap-2 mb-3">
        <span className={colorMap[color]}>{icon}</span>
        <h3 className="font-semibold text-slate-200 text-sm">{title}</h3>
      </div>
      {children}
    </div>
  )
}
