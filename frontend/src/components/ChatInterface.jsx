import { useState, useRef, useEffect } from 'react'
import { Send, Sparkles, Bot, User, Zap } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

const AGENT_COLORS = {
  system: 'text-slate-400',
  orchestrator: 'text-brand',
  strategy: 'text-purple-400',
  audience: 'text-cyan-400',
  content: 'text-emerald-400',
  images: 'text-orange-400',
  claude: 'text-brand-light',
}

const AGENT_LABELS = {
  system: 'System',
  orchestrator: 'Orchestrator',
  strategy: 'Strategy Agent',
  audience: 'Audience Agent',
  content: 'Content Agent',
  images: 'Image Agent',
  claude: 'Claude',
}

const SUGGESTIONS = [
  'Launch a B2B SaaS productivity app for remote teams',
  'E-commerce campaign for sustainable fashion brand',
  'Local restaurant chain targeting millennials',
  'Fitness app for busy professionals aged 30-45',
]

export default function ChatInterface({ messages, steps, isTyping, isRunning, hasCampaign, onSend }) {
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() || isRunning) return
    onSend(input.trim())
    setInput('')
  }

  const handleSuggestion = (s) => {
    setInput(s)
    inputRef.current?.focus()
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-5 py-4 border-b border-slate-700/50 flex items-center gap-3 flex-shrink-0">
        <div className="w-9 h-9 rounded-xl bg-brand/20 border border-brand/30 flex items-center justify-center">
          <Sparkles className="w-4 h-4 text-brand" />
        </div>
        <div>
          <h2 className="font-semibold text-slate-100 text-sm">Campaign Assistant</h2>
          <p className="text-xs text-slate-500">LangGraph · Claude · RAG · Flux</p>
        </div>
        <div className="ml-auto">
          <div className={`w-2 h-2 rounded-full ${isRunning ? 'bg-brand animate-pulse' : 'bg-success'}`} />
        </div>
      </div>

      {/* Step Progress */}
      <div className="px-4 py-3 border-b border-slate-700/30 flex-shrink-0">
        <div className="flex gap-1.5 overflow-x-auto pb-1">
          {steps.map(step => (
            <div key={step.id} className={`step-indicator flex-shrink-0 ${step.status}`}>
              <span>{step.icon}</span>
              <span className="text-xs">{step.label.split(' ')[0]}</span>
              {step.status === 'active' && (
                <span className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin" />
              )}
              {step.status === 'completed' && <span className="text-xs">✓</span>}
            </div>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3 min-h-0">
        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {isTyping && (
          <div className="flex items-start gap-3">
            <div className="w-7 h-7 rounded-lg bg-surface-card border border-slate-700 flex items-center justify-center flex-shrink-0">
              <Bot className="w-3.5 h-3.5 text-brand" />
            </div>
            <div className="chat-bubble-bot">
              <div className="flex gap-1.5">
                {[0, 1, 2].map(i => (
                  <div key={i} className="typing-dot w-2 h-2 rounded-full bg-slate-400" />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggestions (only when idle) */}
      {!hasCampaign && (
        <div className="px-4 pb-3 flex-shrink-0">
          <p className="text-xs text-slate-500 mb-2">Try an example:</p>
          <div className="flex flex-wrap gap-1.5">
            {SUGGESTIONS.map(s => (
              <button
                key={s}
                onClick={() => handleSuggestion(s)}
                className="text-xs bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 px-2.5 py-1.5 rounded-lg transition-colors"
              >
                {s.slice(0, 35)}{s.length > 35 ? '...' : ''}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="px-4 pb-4 flex-shrink-0">
        <form onSubmit={handleSubmit} className="relative">
          <input
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder={isRunning ? 'Generating campaign...' : hasCampaign ? 'Ask a follow-up question...' : 'Describe your campaign goal...'}
            disabled={isRunning}
            className="w-full bg-surface-card border border-slate-700 focus:border-brand/50 text-slate-100 placeholder-slate-500
                       rounded-xl px-4 py-3 pr-12 text-sm outline-none transition-colors"
          />
          <button
            type="submit"
            disabled={!input.trim() || isRunning}
            className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-brand disabled:bg-slate-700
                       rounded-lg flex items-center justify-center transition-colors"
          >
            {isRunning ? (
              <Zap className="w-3.5 h-3.5 text-brand animate-pulse" />
            ) : (
              <Send className="w-3.5 h-3.5 text-white" />
            )}
          </button>
        </form>
      </div>
    </div>
  )
}

function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  const agentColor = AGENT_COLORS[message.agent] || 'text-slate-400'
  const agentLabel = AGENT_LABELS[message.agent] || message.agent

  if (isUser) {
    return (
      <div className="flex items-start gap-2 justify-end animate-fade-in">
        <div className="chat-bubble-user">
          <p className="text-sm">{message.content}</p>
        </div>
        <div className="w-7 h-7 rounded-lg bg-brand/20 border border-brand/30 flex items-center justify-center flex-shrink-0">
          <User className="w-3.5 h-3.5 text-brand" />
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-start gap-2 animate-fade-in">
      <div className="w-7 h-7 rounded-lg bg-surface-card border border-slate-700 flex items-center justify-center flex-shrink-0">
        <Bot className="w-3.5 h-3.5 text-slate-400" />
      </div>
      <div className="flex-1 min-w-0">
        {message.agent && message.agent !== 'system' && (
          <p className={`text-xs font-medium mb-1 ${agentColor}`}>{agentLabel}</p>
        )}
        <div className="chat-bubble-bot max-w-full">
          <div className="text-sm prose prose-invert prose-sm max-w-none">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  )
}
