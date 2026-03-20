import RiskGauge from './RiskGauge'

export default function AuditResults({ result, hashtag, riskThreshold, onBack }) {
  if (!result) return null

  const { reports = [], top_risk_score = 0 } = result
  const critical = reports.filter(r => r.risk_score >= riskThreshold)
  const sorted   = [...reports].sort((a, b) => b.risk_score - a.risk_score)

  return (
    <div className="fade-in">
      {/* Stats bar */}
      <div className="stats-bar">
        <div className="stat-item">
          <div className="stat-value">{reports.length}</div>
          <div className="stat-label">Produktu lapas</div>
        </div>
        <div className="stat-divider" />
        <div className="stat-item">
          <div className={`stat-value ${critical.length > 0 ? 'danger' : ''}`}>{critical.length}</div>
          <div className="stat-label">Kritiskie riski</div>
        </div>
        <div className="stat-divider" />
        <div className="stat-item">
          <div className={`stat-value ${top_risk_score >= riskThreshold ? 'danger' : ''}`}>{top_risk_score}</div>
          <div className="stat-label">Augstākais score</div>
        </div>
      </div>

      {/* Results header */}
      <div className="results-header">
        <span className="results-title">
          🛡️ Audita rezultāti
        </span>
        <span className="hashtag-chip">#{hashtag}</span>
      </div>

      {sorted.length === 0 ? (
        <div className="no-results">
          <div style={{fontSize:48, marginBottom:12}}>🔍</div>
          <p>Netika atrasti produktu veikali pēc šī heštaga.</p>
          <p style={{marginTop:6}}>Mēģiniet izvēlēties citu heštagu no mākoņa.</p>
          <button className="btn btn-ghost" style={{marginTop:20}} onClick={onBack}>
            ← Atpakaļ uz heštagu mākoni
          </button>
        </div>
      ) : (
        <>
          {sorted.map(rep => (
            <StoreCard key={rep.url} rep={rep} riskThreshold={riskThreshold} />
          ))}

          {top_risk_score >= riskThreshold && (
            <div className="high-risk-alert">
              <h3>⚠️ SISTĒMAS BRĪDINĀJUMS — Kritisks apdraudējums konstatēts</h3>
              <p>
                AI daudzlīmeņu audits atklāja aizdomīgus produktus ar heštagu <strong>#{hashtag}</strong>.
                Ieteicama tūlītēja inspektora pārbaude augstu riska vērtību domēniem.
              </p>
            </div>
          )}

          <div style={{marginTop: 28}}>
            <button className="btn btn-ghost" onClick={onBack}>
              ← Atpakaļ uz heštagu mākoni
            </button>
          </div>
        </>
      )}
    </div>
  )
}

function StoreCard({ rep, riskThreshold }) {
  const isHigh   = rep.risk_score >= riskThreshold
  const domain   = (() => { try { return new URL(rep.url).hostname.replace('www.', '') } catch { return rep.url } })()
  const displayTitle = rep.title || domain

  return (
    <div className={`store-card ${isHigh ? 'high-risk' : ''}`}>
      <div className="store-card-top">
        <div style={{flex:1, minWidth:0}}>
          <div className="store-domain">{displayTitle}</div>
          <div className="store-url">
            <a href={rep.url} target="_blank" rel="noreferrer">{rep.url}</a>
          </div>

          <div className="badge-row" style={{marginTop:10}}>
            <Badge ok={rep.audit.ce_mark}           label="CE Marķējums" />
            <Badge ok={rep.audit.manufacturer_info} label="Ražotāja info" />
            <Badge ok={rep.audit.lv_language}       label="LV valoda" />
            <Badge ok={rep.audit.age_restriction}   label="Vecuma ierobežojums" />
          </div>

          <div className="ai-summary-box">
            {rep.audit.risk_summary || 'Nav AI kopsavilkuma.'}
          </div>

          {isHigh && (
            <div style={{
              marginTop:10, fontSize:12, fontWeight:700,
              color:'#fca5a5', display:'flex', alignItems:'center', gap:5
            }}>
              ⚠️ AUGSTS RISKS — ieteicama inspektora pārbaude
            </div>
          )}
        </div>

        <RiskGauge score={rep.risk_score} threshold={riskThreshold} />
      </div>
    </div>
  )
}

function Badge({ ok, label }) {
  return (
    <span className={`badge ${ok ? 'badge-ok' : 'badge-fail'}`}>
      {ok ? '✅' : '❌'} {label}
    </span>
  )
}
