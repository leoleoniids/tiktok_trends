const BASE = '/api'

async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Nezināma kļūda' }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export async function getHealth() {
  const res = await fetch(`${BASE}/health`)
  return res.ok ? res.json() : null
}

/**
 * Phase 0: Discover trends by category via OpenAI
 * @param {string} category
 */
export async function discoverTrends(category) {
  return post('/trends/discover', { category })
}

/**
 * Phase 1: Search TikTok by keywords → returns hashtag cloud
 * @param {string[]} keywords
 * @param {number} limit
 */
export async function scanTikTok(keywords, limit = 20) {
  return post('/scan', { keywords, limit })
}

/**
 * Phase 2: Audit Latvian market for a chosen hashtag
 * @param {string} hashtag
 * @param {string[]} keywords
 */
export async function auditMarket(hashtag, keywords) {
  return post('/audit', { hashtag, keywords })
}
