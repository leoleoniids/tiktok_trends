import { useState } from 'react'
import Sidebar from './components/Sidebar'
import KeywordInput from './components/KeywordInput'
import HashtagCloud from './components/HashtagCloud'
import AuditResults from './components/AuditResults'
import CategoryTrends from './components/CategoryTrends'
import ProcessLog from './components/ProcessLog'
import { scanTikTok, auditMarket } from './api'

const PHASE = {
  IDLE:     'idle',
  SCANNING: 'scanning',
  CLOUD:    'cloud',
  AUDITING: 'auditing',
  RESULTS:  'results',
}

export default function App() {
  const [phase, setPhase]       = useState(PHASE.IDLE)
  const [keywords, setKeywords] = useState([])
  const [scanData, setScanData] = useState(null)    // { total_videos, hashtag_cloud }
  const [auditData, setAuditData] = useState(null)  // PipelineResult
  const [selectedTag, setSelectedTag] = useState(null)
  const [error, setError]       = useState(null)
  const [riskThreshold, setRiskThreshold] = useState(70)
  const [discovering, setDiscovering] = useState(false)
  const [logs, setLogs] = useState([])

  function addLog(status, message, detail='') {
    setLogs(prev => [{
      id: Date.now() + Math.random(),
      timestamp: new Date().toLocaleTimeString('lv-LV', { hour12: false }),
      status,
      message,
      detail
    }, ...prev])
  }

  async function handleScan(kws, limit) {
    setError(null)
    setKeywords(kws)
    setScanData(null)
    setAuditData(null)
    setSelectedTag(null)
    setPhase(PHASE.SCANNING)
    
    addLog('info', 'Uzsākta TikTok video meklēšana')
    addLog('in_progress', 'Tiek meklēti TikTok video par norādītajiem atslēgvārdiem...')
    
    // Simulate steps since backend is blocking
    const t1 = setTimeout(() => addLog('in_progress', 'Tiek izgūti caption un hashtagi...'), 2000)
    const t2 = setTimeout(() => addLog('in_progress', 'Notiek biežāko hashtagu apkopošana...'), 5000)
    
    try {
      const data = await scanTikTok(kws, limit)
      clearTimeout(t1)
      clearTimeout(t2)
      setScanData(data)
      setPhase(PHASE.CLOUD)
      addLog('success', 'TikTok analīze pabeigta')
      addLog('info', 'Hashtagi sagatavoti tālākai izvērtēšanai')
    } catch (e) {
      clearTimeout(t1)
      clearTimeout(t2)
      setError(e.message)
      setPhase(PHASE.IDLE)
      addLog('error', 'Kļūda TikTok meklēšanā', e.message)
    }
  }

  async function handleSelectHashtag(tag) {
    setError(null)
    setSelectedTag(tag)
    setAuditData(null)
    setPhase(PHASE.AUDITING)
    
    addLog('info', `Izvēlēts audits heštagam: #${tag}`)
    addLog('in_progress', 'Uzsākta produktu meklēšana Latvijas tirgū...')
    
    const t1 = setTimeout(() => addLog('in_progress', 'Tiek atlasīti e-komercijas veikali un atdalīti portāli...'), 2000)
    const t2 = setTimeout(() => addLog('in_progress', 'Notiek AI risku analīze atrastajos veikalos...'), 5000)
    
    try {
      const data = await auditMarket(tag, keywords)
      clearTimeout(t1)
      clearTimeout(t2)
      setAuditData(data)
      setPhase(PHASE.RESULTS)
      addLog('success', 'Latvijas tirgus audita analīze pabeigta')
      addLog('info', `Atrasti ${data.reports.length} produktu veikali`)
    } catch (e) {
      clearTimeout(t1)
      clearTimeout(t2)
      setError(e.message)
      setPhase(PHASE.CLOUD)
      addLog('error', 'Kļūda Latvijas tirgus auditā', e.message)
    }
  }

  function handleBack() {
    setPhase(PHASE.CLOUD)
    setAuditData(null)
    setSelectedTag(null)
  }

  return (
    <div className="app-shell">
      <Sidebar riskThreshold={riskThreshold} setRiskThreshold={setRiskThreshold} />

      <main className="main-content">
        <header className="page-header">
          <h1 className="page-title">🛡️ PTAC Sentinel</h1>
          <p className="page-subtitle">
            TikTok trendu uzraudzības sistēma — bīstamu preču atklāšana Latvijas tirgū
          </p>
        </header>

        {/* Error banner */}
        {error && (
          <div style={{
            background:'rgba(239,68,68,0.12)',
            border:'1px solid rgba(239,68,68,0.35)',
            borderRadius:'12px',
            padding:'14px 18px',
            marginBottom:'20px',
            color:'#fca5a5',
            fontSize:'14px',
          }}>
            ⚠️ Kļūda: {error}
          </div>
        )}

        {/* Phase 0 & 1: Input — always visible unless in results */}
        {phase !== PHASE.RESULTS && (
          <>
            <CategoryTrends 
              onSelectTrend={(trend) => {
                addLog('info', `Izvēlēts trends: ${trend.product_name}`)
                handleScan(trend.example_keywords, 20)
              }}
              loading={discovering}
              setLoading={setDiscovering}
              addLog={addLog}
            />
            <KeywordInput
              onScan={handleScan}
              loading={phase === PHASE.SCANNING}
            />
          </>
        )}

        {/* Loading: TikTok Scan */}
        {phase === PHASE.SCANNING && (
          <div className="loader-wrap fade-in">
            <div className="loader-orb" />
            <div className="loader-text">Skenē TikTok...</div>
            <div className="loader-sub">
              Iegūst top 20 video katram atslēgas vārdam un analizē heštagus
            </div>
          </div>
        )}

        {/* Phase 2: Hashtag Cloud */}
        {(phase === PHASE.CLOUD || phase === PHASE.AUDITING) && scanData?.hashtag_cloud && (
          <>
            <div style={{height:20}}/>
            <HashtagCloud
              cloud={scanData.hashtag_cloud}
              totalVideos={scanData.total_videos}
              keywords={keywords}
              onSelect={handleSelectHashtag}
            />
          </>
        )}

        {/* Loading: Market Audit */}
        {phase === PHASE.AUDITING && (
          <div className="loader-wrap fade-in">
            <div className="loader-orb" style={{background:'linear-gradient(135deg,#8b5cf6,#ec4899)'}}/>
            <div className="loader-text">Meklē Latvijas tirgū...</div>
            <div className="loader-sub">
              Audita heštags: <strong style={{color:'#a78bfa'}}>#{selectedTag}</strong>
              {' '}— filtrē salīdzinājumu portālus, pārbauda produktu lapas
            </div>
          </div>
        )}

        {/* Phase 3: Audit Results */}
        {phase === PHASE.RESULTS && auditData && (
          <>
            {/* Allow re-scan */}
            <div style={{marginBottom:20}}>
              <KeywordInput
                onScan={handleScan}
                loading={false}
              />
            </div>
            <AuditResults
              result={auditData}
              hashtag={selectedTag}
              riskThreshold={riskThreshold}
              onBack={handleBack}
            />
          </>
        )}

        {/* Empty state — first load */}
        {phase === PHASE.IDLE && (
          <div className="empty-state fade-in">
            <div className="empty-icon">🔎</div>
            <h2>Sāciet ar atslēgas vārdu ievadi</h2>
            <p>Ievadiet produkta nosaukumu, piemēram <em>Wakuku</em> vai <em>fidget toy</em>,<br/>
            un sistēma automatizēti izveidos TikTok heštagu mākoni.</p>
          </div>
        )}
      </main>

      <ProcessLog logs={logs} />
    </div>
  )
}
