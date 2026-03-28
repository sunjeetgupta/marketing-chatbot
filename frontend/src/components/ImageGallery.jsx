import { useState } from 'react'
import { Image as ImageIcon, Download, ZoomIn, X, Copy, Check } from 'lucide-react'

const FORMAT_LABELS = {
  email: { label: 'Email Hero', badge: 'bg-blue-500/10 text-blue-400 border-blue-500/20' },
  website: { label: 'Website Hero', badge: 'bg-purple-500/10 text-purple-400 border-purple-500/20' },
  social: { label: 'Social Square', badge: 'bg-pink-500/10 text-pink-400 border-pink-500/20' },
  story: { label: 'Story/Reel', badge: 'bg-orange-500/10 text-orange-400 border-orange-500/20' },
}

export default function ImageGallery({ images }) {
  const [lightbox, setLightbox] = useState(null)
  const [copiedIdx, setCopiedIdx] = useState(null)

  if (!images || images.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center px-8">
        <div className="w-16 h-16 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center mb-4">
          <ImageIcon className="w-8 h-8 text-slate-600" />
        </div>
        <h3 className="text-slate-400 font-medium mb-1">No Images Yet</h3>
        <p className="text-sm text-slate-600">Campaign images will appear here after generation</p>
        <p className="text-xs text-slate-700 mt-2">Powered by picsum.photos (Fastly CDN, always loads)</p>
      </div>
    )
  }

  const handleDownload = async (img) => {
    try {
      const response = await fetch(img.url)
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `campaign-${img.format}-${Date.now()}.jpg`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      window.open(img.url, '_blank')
    }
  }

  const handleCopyPrompt = (prompt, idx) => {
    navigator.clipboard.writeText(prompt)
    setCopiedIdx(idx)
    setTimeout(() => setCopiedIdx(null), 2000)
  }

  return (
    <div className="p-5 h-full overflow-y-auto">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-slate-200">{images.length} Campaign Images Generated</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Powered by <span className="text-orange-400">picsum.photos</span> · keywords by Qwen2.5 · Fastly CDN, always loads
          </p>
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-2 gap-4">
        {images.map((img, i) => {
          const fmt = FORMAT_LABELS[img.format] || { label: img.name, badge: 'bg-slate-700 text-slate-400 border-slate-600' }
          const isWide = img.format === 'email' || img.format === 'website'
          return (
            <div
              key={i}
              className={`glass-card overflow-hidden group ${isWide ? 'col-span-2' : 'col-span-1'}`}
            >
              {/* Image */}
              <div
                className="relative overflow-hidden cursor-pointer"
                style={{ paddingBottom: img.format === 'story' ? '177%' : img.format === 'social' ? '100%' : img.format === 'email' ? '33%' : '56%' }}
                onClick={() => setLightbox(img)}
              >
                <img
                  src={img.url}
                  alt={img.name}
                  loading="lazy"
                  className="absolute inset-0 w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                  onError={(e) => {
                    // Show placeholder on error
                    e.target.style.display = 'none'
                    e.target.parentElement.style.background = 'linear-gradient(135deg, #1e293b, #334155)'
                  }}
                />
                {/* Overlay on hover */}
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors flex items-center justify-center">
                  <ZoomIn className="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>

              {/* Info */}
              <div className="p-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`text-xs border px-2 py-0.5 rounded-full font-medium ${fmt.badge}`}>
                    {fmt.label}
                  </span>
                  <span className="text-xs text-slate-500">{img.width}×{img.height}px</span>
                  <div className="ml-auto flex gap-1">
                    <button
                      onClick={() => handleCopyPrompt(img.prompt, i)}
                      title="Copy prompt"
                      className="p-1.5 hover:bg-slate-700 rounded-lg text-slate-400 hover:text-slate-200 transition-colors"
                    >
                      {copiedIdx === i ? <Check className="w-3.5 h-3.5 text-success" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                    <button
                      onClick={() => handleDownload(img)}
                      title="Download"
                      className="p-1.5 hover:bg-slate-700 rounded-lg text-slate-400 hover:text-slate-200 transition-colors"
                    >
                      <Download className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
                <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">{img.prompt}</p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Lightbox */}
      {lightbox && (
        <div
          className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-6"
          onClick={() => setLightbox(null)}
        >
          <button className="absolute top-4 right-4 text-white hover:text-slate-300 p-2" onClick={() => setLightbox(null)}>
            <X className="w-6 h-6" />
          </button>
          <div className="max-w-4xl max-h-full flex flex-col gap-3" onClick={e => e.stopPropagation()}>
            <img
              src={lightbox.url}
              alt={lightbox.name}
              className="max-w-full max-h-[70vh] object-contain rounded-xl"
            />
            <div className="glass-card p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-sm font-medium text-slate-200">{lightbox.name}</span>
                <span className="text-xs text-slate-500">{lightbox.width}×{lightbox.height}px</span>
              </div>
              <p className="text-xs text-slate-400">{lightbox.prompt}</p>
              <div className="flex gap-2 mt-3">
                <button onClick={() => handleDownload(lightbox)} className="btn-primary text-xs px-3 py-1.5 flex items-center gap-1.5">
                  <Download className="w-3 h-3" /> Download
                </button>
                <button onClick={() => handleCopyPrompt(lightbox.prompt, -1)} className="btn-ghost text-xs">
                  {copiedIdx === -1 ? '✓ Copied' : 'Copy Prompt'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
