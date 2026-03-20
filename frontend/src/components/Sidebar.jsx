import { useEffect, useState } from 'react'
import { getHealth } from '../api'

export default function Sidebar({ riskThreshold, setRiskThreshold }) {
  const [health, setHealth] = useState(null)

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealth(null))
  }, [])

  const apis = health?.apis ?? {}

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <img
          src="https://ptac.gov.lv/themes/custom/vpg/logo.svg"
          alt="PTAC"
          onError={e => { e.target.style.display = 'none' }}
        />
      </div>

      <div>
        <div className="sidebar-section-title">API Statuss</div>
        <ApiRow label="Apify (TikTok)" ok={apis.apify} />
        <ApiRow label="Tavily (Tirgus)" ok={apis.tavily} />
        <ApiRow label="Gemini (AI)" ok={apis.gemini} />
      </div>

      <hr className="sidebar-divider" />

      <div>
        <div className="sidebar-section-title">Riska slieksnis</div>
        <div className="slider-label">
          <span>Kritiskais risks</span>
          <strong>{riskThreshold}/100</strong>
        </div>
        <input
          type="range"
          min={1} max={100}
          value={riskThreshold}
          onChange={e => setRiskThreshold(Number(e.target.value))}
        />
      </div>

      <hr className="sidebar-divider" />

      <div className="sidebar-footer">
        PTAC Sentinel v3.0<br />
        TikTok → Tirgus → AI Audits
      </div>
    </aside>
  )
}

function ApiRow({ label, ok }) {
  return (
    <div className="api-indicator">
      <span className={`api-dot ${ok ? 'ok' : 'missing'}`} />
      {label}
    </div>
  )
}
