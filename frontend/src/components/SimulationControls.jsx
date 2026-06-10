import { useEffect, useRef, useState } from 'react'
import { SkipBack, SkipForward, ChevronLeft, ChevronRight, CheckCircle, XCircle } from 'lucide-react'

export default function SimulationControls({ steps, stepIndex, onStepChange, accepted }) {
  const [isPlaying, setIsPlaying] = useState(false)
  const intervalRef = useRef(null)

  const total   = steps.length
  const current = steps[stepIndex]
  const atEnd   = stepIndex === total - 1
  const atStart = stepIndex === 0

  useEffect(() => {
    if (isPlaying) {
      intervalRef.current = setInterval(() => {
        onStepChange((prev) => {
          if (prev >= total - 1) { setIsPlaying(false); return prev }
          return prev + 1
        })
      }, 900)
    }
    return () => clearInterval(intervalRef.current)
  }, [isPlaying, total, onStepChange])

  useEffect(() => { if (atEnd) setIsPlaying(false) }, [atEnd])

  const inputChars = steps
    .filter((s) => s.symbol_read !== null)
    .map((s) => s.symbol_read)

  return (
    <div className="border-t border-border bg-surface px-4 py-3 space-y-3">
      <div className="flex items-center gap-2">
        <span className="text-xs text-muted font-mono uppercase tracking-wider shrink-0">Input:</span>
        <div className="flex items-center gap-0.5 flex-wrap">
          {inputChars.length === 0 ? (
            <span className="text-xs text-muted font-mono italic">ε (empty string)</span>
          ) : (
            inputChars.map((ch, i) => {
              const charStep  = i + 1
              const isRead    = charStep < stepIndex
              const isCurrent = charStep === stepIndex
              return (
                <span
                  key={i}
                  className={`
                    inline-flex w-7 h-7 items-center justify-center rounded font-mono text-sm font-bold transition-all duration-200
                    ${isCurrent ? 'bg-active text-black scale-110 shadow-md shadow-amber-500/30' : ''}
                    ${isRead    ? 'text-muted bg-canvas' : ''}
                    ${!isRead && !isCurrent ? 'text-white bg-canvas border border-border' : ''}
                  `}
                >
                  {ch}
                </span>
              )
            })
          )}
        </div>
        {atEnd && (
          <span className={`ml-auto flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${
            accepted
              ? 'bg-accept/20 text-green-300 border border-accept/40'
              : 'bg-reject/20 text-red-300 border border-reject/40'
          }`}>
            {accepted ? <CheckCircle size={13} /> : <XCircle size={13} />}
            {accepted ? 'Accepted' : 'Rejected'}
          </span>
        )}
      </div>

      <div className="bg-canvas border border-border rounded-lg px-3 py-2 min-h-[36px]">
        <p className="text-xs font-mono text-white leading-relaxed">
          <span className="text-muted mr-2">Step {stepIndex}/{total - 1}</span>
          {current?.description}
        </p>
      </div>

      {current?.active_states?.length > 0 && (
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-xs text-muted">Active:</span>
          {current.active_states.map((s) => (
            <span key={s} className="px-2 py-0.5 rounded-full bg-accent/20 border border-accent/50 text-xs font-mono text-violet-300">
              {s}
            </span>
          ))}
        </div>
      )}
      {current?.active_states?.length === 0 && stepIndex > 0 && (
        <p className="text-xs font-mono text-reject">∅ — Dead configuration</p>
      )}

      <div className="flex items-center justify-center gap-2">
        <button onClick={() => { setIsPlaying(false); onStepChange(0) }} disabled={atStart}
          className="p-2 rounded-lg border border-border hover:border-muted disabled:opacity-30 disabled:cursor-not-allowed text-muted hover:text-white transition-colors">
          <SkipBack size={14} />
        </button>
        <button onClick={() => onStepChange((i) => Math.max(0, i - 1))} disabled={atStart}
          className="p-2 rounded-lg border border-border hover:border-muted disabled:opacity-30 disabled:cursor-not-allowed text-muted hover:text-white transition-colors">
          <ChevronLeft size={14} />
        </button>
        <button
          onClick={() => setIsPlaying((p) => !p)}
          disabled={atEnd && !isPlaying}
          className={`px-4 py-2 rounded-lg text-xs font-semibold transition-colors border ${
            isPlaying
              ? 'bg-active/20 border-active/50 text-amber-300 hover:bg-active/30'
              : 'bg-accent/20 border-accent/50 text-violet-300 hover:bg-accent/30'
          } disabled:opacity-30 disabled:cursor-not-allowed`}
        >
          {isPlaying ? '⏸ Pause' : '▶ Play'}
        </button>
        <button onClick={() => onStepChange((i) => Math.min(total - 1, i + 1))} disabled={atEnd}
          className="p-2 rounded-lg border border-border hover:border-muted disabled:opacity-30 disabled:cursor-not-allowed text-muted hover:text-white transition-colors">
          <ChevronRight size={14} />
        </button>
        <button onClick={() => { setIsPlaying(false); onStepChange(total - 1) }} disabled={atEnd}
          className="p-2 rounded-lg border border-border hover:border-muted disabled:opacity-30 disabled:cursor-not-allowed text-muted hover:text-white transition-colors">
          <SkipForward size={14} />
        </button>
      </div>

      <div className="h-1 bg-canvas rounded-full overflow-hidden">
        <div
          className="h-full bg-accent rounded-full transition-all duration-300"
          style={{ width: `${(stepIndex / Math.max(1, total - 1)) * 100}%` }}
        />
      </div>
    </div>
  )
}
