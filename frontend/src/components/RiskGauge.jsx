/**
 * SVG circular risk gauge — no external deps needed.
 * score: 0–100
 */
export default function RiskGauge({ score = 0, threshold = 70 }) {
  const R = 42
  const cx = 56
  const cy = 56
  const circumference = 2 * Math.PI * R
  const dash = (score / 100) * circumference
  const gap  = circumference - dash

  // Color: green → yellow → red
  const color =
    score < 40 ? '#10b981' :
    score < threshold ? '#f59e0b' :
    '#ef4444'

  return (
    <div className="gauge-wrap">
      <svg width="112" height="112" viewBox="0 0 112 112">
        {/* Track */}
        <circle
          cx={cx} cy={cy} r={R}
          fill="none"
          stroke="rgba(255,255,255,0.07)"
          strokeWidth="10"
        />
        {/* Fill */}
        <circle
          cx={cx} cy={cy} r={R}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={`${dash} ${gap}`}
          strokeDashoffset={circumference * 0.25}
          style={{ transition: 'stroke-dasharray 0.6s ease, stroke 0.4s ease', filter: `drop-shadow(0 0 5px ${color})` }}
        />
        {/* Value text */}
        <text
          x={cx} y={cy + 2}
          textAnchor="middle"
          dominantBaseline="middle"
          fill={color}
          fontSize="18"
          fontWeight="800"
          fontFamily="Inter, sans-serif"
        >
          {score}
        </text>
        {/* /100 label */}
        <text
          x={cx} y={cy + 18}
          textAnchor="middle"
          dominantBaseline="middle"
          fill="rgba(255,255,255,0.3)"
          fontSize="9"
          fontFamily="Inter, sans-serif"
        >
          /100
        </text>
      </svg>
      <span className="gauge-label">Riska score</span>
    </div>
  )
}
