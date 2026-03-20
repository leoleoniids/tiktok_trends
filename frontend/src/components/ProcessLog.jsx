export default function ProcessLog({ logs }) {
  return (
    <aside className="process-log-sidebar">
      <div className="process-log-header">
        <span>📜</span> Procesa gaita
      </div>
      <div className="log-list">
        {logs.map(log => (
          <div key={log.id} className={`log-item status-${log.status} fade-in`}>
            <div className="log-dot"></div>
            <div className="log-time">{log.timestamp}</div>
            <div className="log-message">{log.message}</div>
            {log.detail && <div className="log-detail">{log.detail}</div>}
          </div>
        ))}
        {logs.length === 0 && (
          <div style={{ fontSize: '13px', color: 'var(--text-3)', textAlign: 'center', marginTop: '40px' }}>
            Gaida sistēmas darbības...
          </div>
        )}
      </div>
    </aside>
  )
}
