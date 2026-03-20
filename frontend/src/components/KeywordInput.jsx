import { useState, useRef } from 'react'

export default function KeywordInput({ onScan, loading }) {
  const [keywords, setKeywords] = useState([])
  const [inputVal, setInputVal]  = useState('')
  const [limit, setLimit] = useState(20)
  const inputRef = useRef()

  function addKeyword(raw) {
    const val = raw.trim().replace(/,/g, '')
    if (val && !keywords.includes(val)) {
      setKeywords(prev => [...prev, val])
    }
    setInputVal('')
  }

  function handleKey(e) {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      addKeyword(inputVal)
    } else if (e.key === 'Backspace' && inputVal === '' && keywords.length) {
      setKeywords(prev => prev.slice(0, -1))
    }
  }

  function removeKeyword(kw) {
    setKeywords(prev => prev.filter(k => k !== kw))
  }

  function handleScan() {
    // If there's still text in the input, add it first
    if (inputVal.trim()) addKeyword(inputVal)
    const kws = inputVal.trim()
      ? [...keywords, inputVal.trim().replace(/,/g, '')].filter(Boolean)
      : keywords
    if (kws.length > 0) onScan(kws, limit)
  }

  return (
    <div className="card fade-in">
      <div className="card-title">
        <span>🔍</span> 1. fāze — TikTok Skautēšana
      </div>
      <div className="card-sub" style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <div>
          Ievadiet atslēgas vārdus un nospiediet <kbd style={{
            background: 'var(--bg-card-hover)',
            border: '1px solid var(--border)',
            borderRadius: '4px',
            padding: '1px 6px',
            fontSize: '11px',
            color: 'var(--text-2)'
          }}>Enter</kbd> katram. Sistēma iegūs top video un izveidos heštagu mākoni.
        </div>
        <div style={{display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', background: 'var(--bg-card-hover)', padding: '6px 12px', borderRadius: '8px'}}>
          <label>Video limits:</label>
          <input 
            type="number" 
            min="5" max="100" 
            value={limit} 
            onChange={e => setLimit(Number(e.target.value))}
            style={{
              background: 'var(--bg-surface)', border: '1px solid var(--border)', 
              color: 'var(--text-1)', width: '50px', borderRadius: '4px', padding: '2px 4px',
              fontFamily: 'inherit'
            }}
          />
        </div>
      </div>

      <div
        className="tag-input-wrap"
        onClick={() => inputRef.current?.focus()}
      >
        {keywords.map(kw => (
          <span key={kw} className="keyword-tag">
            {kw}
            <button onClick={e => { e.stopPropagation(); removeKeyword(kw) }}>×</button>
          </span>
        ))}
        <input
          ref={inputRef}
          className="tag-text-input"
          value={inputVal}
          onChange={e => setInputVal(e.target.value)}
          onKeyDown={handleKey}
          placeholder={keywords.length ? '' : 'Wakuku, fidget toy, slime kit...'}
        />
      </div>
      <div className="input-hint">Nospiediet Enter vai komatu, lai pievienotu atslēgas vārdu</div>

      <button
        className="btn btn-primary btn-full"
        disabled={loading || (keywords.length === 0 && !inputVal.trim())}
        onClick={handleScan}
      >
        {loading
          ? '⏳ Skenē TikTok...'
          : '🚀 Sākt TikTok skenēšanu'}
      </button>
    </div>
  )
}
