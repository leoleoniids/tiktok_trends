import { useState } from 'react'
import { discoverTrends } from '../api'

export default function CategoryTrends({ onSelectTrend, loading, setLoading, addLog }) {
  const [category, setCategory] = useState('')
  const [trends, setTrends] = useState([])
  const [error, setError] = useState(null)

  async function handleDiscover() {
    if (!category.trim()) return
    setError(null)
    setLoading(true)
    setTrends([])
    
    addLog('info', `Izvēlēta kategorija: ${category}`)
    addLog('info', 'Uzsākta aktuālo trendu meklēšana')
    
    const t1 = setTimeout(() => addLog('in_progress', 'Tiek veikta web meklēšana pēc aktuāliem produktiem šajā kategorijā'), 1500)
    const t2 = setTimeout(() => addLog('in_progress', 'Tiek strukturēti atrastie rezultāti'), 4500)
    
    try {
      const data = await discoverTrends(category)
      clearTimeout(t1)
      clearTimeout(t2)
      const results = data.trends || []
      setTrends(results)
      addLog('success', `Atrasti ${results.length} aktuāli trendi`)
      addLog('info', 'Rezultāti sagatavoti izvēlei')
    } catch (e) {
      clearTimeout(t1)
      clearTimeout(t2)
      setError(e.message)
      addLog('error', 'Neizdevās iegūt strukturētus rezultātus no trendu analīzes', e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card fade-in" style={{ marginBottom: '20px' }}>
      <div className="card-title">
        <span>💡</span> 0. fāze — Uzzināt trendus
      </div>
      <div className="card-sub">
        Ievadiet produkta kategoriju (piem. "bērnu rotaļlietas" vai "skaistumkopšana"), 
        un AI automātiski atradīs 5 aktuālākos trendus šajā nišā.
      </div>
      
      {error && (
        <div style={{ color: '#fca5a5', marginBottom: '10px', fontSize: '14px' }}>
          ⚠️ Kļūda: {error}
        </div>
      )}

      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <input
          className="tag-text-input"
          style={{ flex: 1, padding: '10px', background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: '8px', color: 'var(--text-1)' }}
          value={category}
          onChange={e => setCategory(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleDiscover()}
          placeholder="Ievadiet kategoriju, piemēram: bērnu rotaļlietas"
        />
        <button 
          className="btn btn-primary" 
          disabled={loading || !category.trim()}
          onClick={handleDiscover}
        >
          {loading ? 'Meklējam aktuālos trendus...' : 'Uzzināt trendus'}
        </button>
      </div>

      {trends.length > 0 && (
        <div style={{ display: 'grid', gap: '15px' }}>
          {trends.map((t, i) => (
            <div key={i} style={{ 
              background: 'var(--bg-surface)', 
              padding: '15px', 
              borderRadius: '8px',
              border: '1px solid var(--border)'
            }}>
              <h3 style={{ margin: '0 0 5px 0', fontSize: '16px', color: 'var(--accent)' }}>{t.product_name}</h3>
              <p style={{ margin: '0 0 10px 0', fontSize: '13px', color: 'var(--text-2)' }}>{t.short_description}</p>
              
              <div style={{ marginBottom: '10px' }}>
                <strong style={{ fontSize: '12px', color: 'var(--text-3)' }}>Kāpēc tas ir trends:</strong>
                <p style={{ margin: '2px 0 0 0', fontSize: '13px', color: 'var(--text-1)' }}>{t.why_trending}</p>
              </div>

              <div style={{ marginBottom: '15px', display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {t.example_keywords.map(kw => (
                  <span key={kw} style={{ 
                    background: 'rgba(139, 92, 246, 0.1)', 
                    color: 'var(--accent)', 
                    padding: '2px 6px', 
                    borderRadius: '4px', 
                    fontSize: '11px' 
                  }}>
                    {kw}
                  </span>
                ))}
              </div>
              
              <button 
                className="btn btn-primary" 
                style={{ width: '100%', padding: '8px', fontSize: '13px' }}
                onClick={() => onSelectTrend(t)}
              >
                Izvēlēties un skenēt TikTok
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
