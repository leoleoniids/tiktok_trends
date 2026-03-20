/**
 * Interactive hashtag cloud.
 * cloud: { hashtags: {tag: count}, top_hashtags: [str], ai_summary: str }
 */
export default function HashtagCloud({ cloud, onSelect, totalVideos, keywords }) {
  if (!cloud) return null

  const { hashtags = {}, top_hashtags = [], ai_summary = '' } = cloud
  const recommended = new Set(top_hashtags)

  // Others sorted by frequency, excluding recommended
  const others = Object.entries(hashtags)
    .filter(([tag]) => !recommended.has(tag))
    .sort((a, b) => b[1] - a[1])
    .slice(0, 40)

  // Font size for word cloud feel
  const maxCount = Math.max(...Object.values(hashtags), 1)
  function tagSize(count) {
    const ratio = count / maxCount
    return Math.round(11 + ratio * 10)
  }

  return (
    <div className="card fade-in">
      <div className="card-title"><span>☁️</span> 2. fāze — TikTok Heštagu Mākonis</div>
      <div className="card-sub">
        Atrasti <strong style={{color:'#93c5fd'}}>{totalVideos}</strong> video pēc:{' '}
        {keywords.map(k => <span key={k} className="hashtag-chip" style={{marginRight:4}}>🔑 {k}</span>)}
      </div>

      {ai_summary && (
        <div className="cloud-ai-summary">
          <strong>🤖 AI analīze:</strong> {ai_summary}
        </div>
      )}

      {top_hashtags.length > 0 && (
        <>
          <div className="cloud-section-label">⭐ AI ieteiktie — augstā prioritāte</div>
          <div className="hashtag-cloud" style={{marginBottom: 20}}>
            {top_hashtags.map(tag => (
              <button
                key={tag}
                className="ht-tag ht-recommended btn"
                onClick={() => onSelect(tag)}
                title={`Biežums: ${hashtags[tag] || '?'} video`}
              >
                #{tag} ⭐
              </button>
            ))}
          </div>
        </>
      )}

      {others.length > 0 && (
        <>
          <div className="cloud-section-label">📊 Visi heštagi — klikšķini lai sāktu auditu</div>
          <div className="hashtag-cloud">
            {others.map(([tag, count]) => (
              <button
                key={tag}
                className="ht-tag ht-normal btn"
                style={{ fontSize: tagSize(count) + 'px', padding: `${5 + count/maxCount*3}px ${10 + count/maxCount*4}px` }}
                onClick={() => onSelect(tag)}
                title={`${count} video`}
              >
                #{tag}
                <span style={{fontSize:'10px', opacity:0.5, marginLeft:3}}>({count})</span>
              </button>
            ))}
          </div>
        </>
      )}

      {top_hashtags.length === 0 && others.length === 0 && (
        <div className="no-results">
          <p>Netika atrasti heštagi. Mēģiniet citus atslēgas vārdus.</p>
        </div>
      )}
    </div>
  )
}
