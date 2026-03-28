import { useState, useRef } from 'react'
import { Code, Eye, Download, ExternalLink, Mail, Globe } from 'lucide-react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

export default function PreviewPanel({ emailHtml, websiteHtml, type }) {
  const [viewMode, setViewMode] = useState('preview') // preview | source
  const html = type === 'email' ? emailHtml : websiteHtml
  const iframeRef = useRef(null)

  const isEmpty = !html

  const handleDownload = () => {
    if (!html) return
    const blob = new Blob([html], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = type === 'email' ? 'campaign-email.html' : 'campaign-landing-page.html'
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleOpenNew = () => {
    if (!html) return
    const blob = new Blob([html], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank')
  }

  if (isEmpty) {
    const Icon = type === 'email' ? Mail : Globe
    return (
      <div className="flex flex-col items-center justify-center h-full text-center px-8">
        <div className="w-16 h-16 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center mb-4">
          <Icon className="w-8 h-8 text-slate-600" />
        </div>
        <h3 className="text-slate-400 font-medium mb-1">
          {type === 'email' ? 'Email Template' : 'Website Landing Page'} Not Generated Yet
        </h3>
        <p className="text-sm text-slate-600">HTML will appear here after campaign generation</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-700/50 flex-shrink-0">
        <div className="flex items-center gap-1 bg-slate-800 rounded-xl p-1">
          <button
            onClick={() => setViewMode('preview')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              viewMode === 'preview' ? 'bg-brand text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Eye className="w-3 h-3" /> Preview
          </button>
          <button
            onClick={() => setViewMode('source')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              viewMode === 'source' ? 'bg-brand text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Code className="w-3 h-3" /> Source
          </button>
        </div>

        <div className="ml-auto flex items-center gap-1.5">
          <button onClick={handleOpenNew} className="btn-ghost flex items-center gap-1.5">
            <ExternalLink className="w-3.5 h-3.5" /> Open
          </button>
          <button onClick={handleDownload} className="btn-ghost flex items-center gap-1.5">
            <Download className="w-3.5 h-3.5" /> Download
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {viewMode === 'preview' ? (
          <div className="h-full bg-white">
            {type === 'email' ? (
              // Email preview in a centered container
              <div className="h-full overflow-auto bg-gray-100 p-4">
                <div className="max-w-[600px] mx-auto shadow-xl">
                  <iframe
                    ref={iframeRef}
                    srcDoc={html}
                    className="preview-frame"
                    style={{ minHeight: '600px', height: '100%' }}
                    title="Email Preview"
                  />
                </div>
              </div>
            ) : (
              // Website preview full-width
              <iframe
                ref={iframeRef}
                srcDoc={html}
                className="preview-frame w-full h-full"
                title="Website Preview"
              />
            )}
          </div>
        ) : (
          <div className="h-full overflow-auto">
            <SyntaxHighlighter
              language="html"
              style={vscDarkPlus}
              showLineNumbers
              wrapLines
              customStyle={{
                margin: 0,
                borderRadius: 0,
                fontSize: '12px',
                height: '100%',
                background: '#0d1117',
              }}
            >
              {html}
            </SyntaxHighlighter>
          </div>
        )}
      </div>
    </div>
  )
}
