import { Sparkles, Target, Users, Mail, Globe, Image as ImageIcon, Cpu } from 'lucide-react'
import { useMarketingChat } from './hooks/useMarketingChat'
import ChatInterface from './components/ChatInterface'
import StrategyPanel from './components/StrategyPanel'
import AudiencePanel from './components/AudiencePanel'
import PreviewPanel from './components/PreviewPanel'
import ImageGallery from './components/ImageGallery'

const TABS = [
  { id: 'strategy', label: 'Strategy', icon: Target, shortLabel: '🎯' },
  { id: 'audience', label: 'Audience', icon: Users, shortLabel: '👥' },
  { id: 'email', label: 'Email', icon: Mail, shortLabel: '✉️' },
  { id: 'website', label: 'Website', icon: Globe, shortLabel: '🌐' },
  { id: 'images', label: 'Images', icon: ImageIcon, shortLabel: '🖼️' },
]

export default function App() {
  const chat = useMarketingChat()

  const handleSend = (input) => {
    if (chat.campaignData.status === 'complete' || chat.campaignData.status === 'error') {
      chat.sendFollowUp(input)
    } else {
      chat.sendCampaignBrief(input)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-surface overflow-hidden">
      {/* Top Nav */}
      <header className="flex-shrink-0 border-b border-slate-700/50 bg-surface-card/50 backdrop-blur-sm">
        <div className="flex items-center gap-4 px-6 py-3">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-brand to-purple-600 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-slate-100 text-sm leading-tight">CampaignAI</h1>
              <p className="text-xs text-slate-500 leading-tight">Marketing Campaign Generator</p>
            </div>
          </div>

          {/* Tech stack badges */}
          <div className="flex items-center gap-2 ml-4">
            <TechBadge label="LangGraph" color="brand" />
            <TechBadge label="Ollama" color="purple" />
            <TechBadge label="Qwen2.5:7b" color="cyan" />
            <TechBadge label="ChromaDB RAG" color="emerald" />
            <TechBadge label="loremflickr Photos" color="orange" />
          </div>

          {/* Status */}
          <div className="ml-auto flex items-center gap-2">
            {chat.isRunning && (
              <div className="flex items-center gap-2 text-xs text-brand">
                <Cpu className="w-3.5 h-3.5 animate-pulse" />
                <span>Generating campaign...</span>
              </div>
            )}
            {chat.campaignData.status === 'complete' && (
              <span className="text-xs text-success flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-success inline-block" />
                Campaign ready
              </span>
            )}
          </div>
        </div>
      </header>

      {/* Main Layout */}
      <div className="flex flex-1 min-h-0">
        {/* Left: Chat Panel */}
        <div className="w-[380px] flex-shrink-0 border-r border-slate-700/50 flex flex-col min-h-0">
          <ChatInterface
            messages={chat.messages}
            steps={chat.steps}
            isTyping={chat.isTyping}
            isRunning={chat.isRunning}
            hasCampaign={chat.hasCampaign}
            onSend={handleSend}
          />
        </div>

        {/* Right: Results Panel */}
        <div className="flex-1 flex flex-col min-h-0 min-w-0">
          {/* Tab Bar */}
          <div className="flex-shrink-0 border-b border-slate-700/50 bg-surface-card/30 px-4 py-2">
            <div className="flex gap-1 overflow-x-auto">
              {TABS.map(tab => {
                const Icon = tab.icon
                const hasData = hasTabData(tab.id, chat.campaignData)
                return (
                  <button
                    key={tab.id}
                    onClick={() => chat.setActiveTab(tab.id)}
                    className={`tab-btn flex items-center gap-2 ${chat.activeTab === tab.id ? 'active' : ''}`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span>{tab.label}</span>
                    {hasData && chat.activeTab !== tab.id && (
                      <span className="w-1.5 h-1.5 rounded-full bg-success" />
                    )}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Tab Content */}
          <div className="flex-1 min-h-0 overflow-hidden">
            {chat.activeTab === 'strategy' && (
              <StrategyPanel strategy={chat.campaignData.strategy} />
            )}
            {chat.activeTab === 'audience' && (
              <AudiencePanel audience={chat.campaignData.audience} />
            )}
            {chat.activeTab === 'email' && (
              <PreviewPanel emailHtml={chat.campaignData.emailHtml} websiteHtml={chat.campaignData.websiteHtml} type="email" />
            )}
            {chat.activeTab === 'website' && (
              <PreviewPanel emailHtml={chat.campaignData.emailHtml} websiteHtml={chat.campaignData.websiteHtml} type="website" />
            )}
            {chat.activeTab === 'images' && (
              <ImageGallery images={chat.campaignData.images} />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function TechBadge({ label, color }) {
  const colorMap = {
    brand: 'bg-brand/10 text-brand border-brand/20',
    purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    cyan: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    orange: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
  }
  return (
    <span className={`text-xs border px-2 py-0.5 rounded-full font-medium ${colorMap[color]}`}>
      {label}
    </span>
  )
}

function hasTabData(tabId, data) {
  switch (tabId) {
    case 'strategy': return !!data.strategy
    case 'audience': return !!data.audience
    case 'email': return !!data.emailHtml
    case 'website': return !!data.websiteHtml
    case 'images': return data.images?.length > 0
    default: return false
  }
}
