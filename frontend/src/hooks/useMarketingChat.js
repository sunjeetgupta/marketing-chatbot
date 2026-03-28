import { useState, useRef, useCallback } from 'react'
import axios from 'axios'

// In production (Vercel), set VITE_API_URL to your Railway backend URL.
// In local dev, the Vite proxy forwards /api → http://localhost:8000/api.
const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : '/api'

export function useMarketingChat() {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: "Hi! I'm **CampaignAI**, your AI marketing strategist powered by **Groq + LLaMA**. Tell me about your product or campaign goal, and I'll create a complete campaign strategy, target audience, email & website templates, and campaign imagery for you.\n\n*Try: \"Launch a new productivity SaaS app targeting remote teams\"*",
      timestamp: new Date(),
      agent: 'system',
    }
  ])
  const [campaignData, setCampaignData] = useState({
    strategy: null,
    audience: null,
    emailHtml: null,
    websiteHtml: null,
    images: [],
    imageUrls: [],
    status: 'idle', // idle | running | complete | error
    currentStep: null,
  })
  const [steps, setSteps] = useState([
    { id: 'strategy', label: 'Campaign Strategy', icon: '🎯', status: 'pending', llm: 'LLaMA 70B' },
    { id: 'audience', label: 'Target Audience', icon: '👥', status: 'pending', llm: 'LLaMA 8B' },
    { id: 'content', label: 'Email & Website', icon: '✉️', status: 'pending', llm: 'LLaMA 70B' },
    { id: 'images', label: 'Campaign Imagery', icon: '🖼️', status: 'pending', llm: 'picsum.photos' },
  ])
  const [isTyping, setIsTyping] = useState(false)
  const [activeTab, setActiveTab] = useState('strategy')
  const eventSourceRef = useRef(null)
  const campaignIdRef = useRef(null)

  const addMessage = useCallback((msg) => {
    setMessages(prev => [...prev, { id: Date.now().toString(), timestamp: new Date(), ...msg }])
  }, [])

  const updateStepStatus = useCallback((stepId, status, extra = {}) => {
    setSteps(prev => prev.map(s => s.id === stepId ? { ...s, status, ...extra } : s))
  }, [])

  const sendCampaignBrief = useCallback(async (userInput) => {
    if (!userInput.trim()) return

    // Add user message
    addMessage({ role: 'user', content: userInput })
    setIsTyping(true)
    setCampaignData(prev => ({ ...prev, status: 'running', strategy: null, audience: null, emailHtml: null, websiteHtml: null, images: [], imageUrls: [] }))
    setSteps(prev => prev.map(s => ({ ...s, status: 'pending' })))

    addMessage({
      role: 'assistant',
      content: '**Starting campaign generation...** I\'m orchestrating 4 specialized AI agents to build your complete campaign. Watch the progress below.',
      agent: 'orchestrator',
    })

    try {
      // Start campaign
      const { data } = await axios.post(`${API_BASE}/campaign/start`, { user_input: userInput })
      const campaignId = data.campaign_id
      campaignIdRef.current = campaignId

      // Connect to SSE stream
      const es = new EventSource(`${API_BASE}/campaign/${campaignId}/stream`)
      eventSourceRef.current = es

      es.onmessage = (event) => {
        const evt = JSON.parse(event.data)
        handleStreamEvent(evt)
      }

      es.onerror = () => {
        es.close()
        setIsTyping(false)
        setCampaignData(prev => ({ ...prev, status: 'error' }))
        addMessage({ role: 'assistant', content: '⚠️ Connection lost. Please try again.', agent: 'system' })
      }
    } catch (err) {
      setIsTyping(false)
      setCampaignData(prev => ({ ...prev, status: 'error' }))
      addMessage({ role: 'assistant', content: `❌ Failed to start: ${err.message}`, agent: 'system' })
    }

    function handleStreamEvent(evt) {
      const { type, step, message, data } = evt

      if (type === 'ping' || type === 'connected') return

      if (type === 'step_start') {
        updateStepStatus(step, 'active')
        addMessage({
          role: 'assistant',
          content: `**${getStepEmoji(step)} ${getStepLabel(step)}**: ${message}`,
          agent: step,
        })
        setActiveTab(step === 'content' ? 'email' : step)
      }

      if (type === 'step_progress') {
        addMessage({ role: 'assistant', content: `  ↳ ${message}`, agent: step })
      }

      if (type === 'step_complete') {
        updateStepStatus(step, 'completed')
        if (step === 'strategy' && data) {
          setCampaignData(prev => ({ ...prev, strategy: data }))
          setActiveTab('strategy')
          addMessage({
            role: 'assistant',
            content: `✅ **Strategy created**: *${data.campaign_name}* — ${data.campaign_type} campaign across ${data.channels?.length || 0} channels.`,
            agent: 'strategy',
          })
        }
        if (step === 'audience' && data) {
          setCampaignData(prev => ({ ...prev, audience: data }))
          setActiveTab('audience')
          addMessage({
            role: 'assistant',
            content: `✅ **Audience defined**: Primary segment "${data.primary_segment?.name}" (${data.primary_segment?.age_range}). LLM: ${data._llm_used || 'Ollama'}.`,
            agent: 'audience',
          })
        }
        if (step === 'content') {
          addMessage({
            role: 'assistant',
            content: `✅ **Content generated**: Email template and website landing page HTML are ready for preview.`,
            agent: 'content',
          })
          setActiveTab('email')
        }
        if (step === 'images' && data) {
          setCampaignData(prev => ({ ...prev, images: data.images || [], imageUrls: data.image_urls || [] }))
          setActiveTab('images')
          addMessage({
            role: 'assistant',
            content: `✅ **Images generated**: ${data.images?.length || 4} campaign visuals created (keywords by Qwen2.5, photos from loremflickr).`,
            agent: 'images',
          })
        }
      }

      if (type === 'campaign_complete' && data) {
        setCampaignData(prev => ({
          ...prev,
          strategy: data.strategy || prev.strategy,
          audience: data.audience || prev.audience,
          emailHtml: data.email_html,
          websiteHtml: data.website_html,
          images: data.images || prev.images,
          imageUrls: data.image_urls || prev.imageUrls,
          status: 'complete',
        }))
        setIsTyping(false)
        addMessage({
          role: 'assistant',
          content: `🎉 **Campaign complete!** All assets generated:\n- 📋 Campaign strategy\n- 👥 Audience segments\n- ✉️ Email HTML template\n- 🌐 Website landing page\n- 🖼️ ${data.images?.length || 4} campaign images\n\nYou can preview everything in the panels on the right. Ask me any follow-up questions!`,
          agent: 'orchestrator',
        })
        eventSourceRef.current?.close()
      }

      if (type === 'stream_end') {
        setIsTyping(false)
        eventSourceRef.current?.close()
      }

      if (type === 'step_error' || type === 'fatal_error') {
        updateStepStatus(step, 'error')
        setIsTyping(false)
        addMessage({
          role: 'assistant',
          content: `❌ **Error in ${step}**: ${message}`,
          agent: 'system',
        })
      }
    }
  }, [addMessage, updateStepStatus])

  const sendFollowUp = useCallback(async (message) => {
    if (!campaignIdRef.current) return
    addMessage({ role: 'user', content: message })
    setIsTyping(true)
    try {
      const { data } = await axios.post(`${API_BASE}/campaign/${campaignIdRef.current}/chat`, {
        campaign_id: campaignIdRef.current,
        message,
      })
      addMessage({ role: 'assistant', content: data.response, agent: 'claude' })
    } catch {
      addMessage({ role: 'assistant', content: 'Sorry, I could not process that.', agent: 'system' })
    } finally {
      setIsTyping(false)
    }
  }, [addMessage])

  return {
    messages,
    campaignData,
    steps,
    isTyping,
    activeTab,
    setActiveTab,
    sendCampaignBrief,
    sendFollowUp,
    hasCampaign: campaignData.status !== 'idle',
    isRunning: campaignData.status === 'running',
  }
}

function getStepEmoji(step) {
  const map = { strategy: '🎯', audience: '👥', content: '✉️', images: '🖼️' }
  return map[step] || '⚙️'
}
function getStepLabel(step) {
  const map = { strategy: 'Strategy Agent (Qwen2.5)', audience: 'Audience Agent (Qwen2.5)', content: 'Content Agent (Qwen2.5)', images: 'Image Agent (Flux)' }
  return map[step] || step
}
