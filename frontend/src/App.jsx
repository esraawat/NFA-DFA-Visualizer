/**
 * App.jsx
 * Root layout: sidebar form | main graph canvas (NFA + DFA side-by-side or toggled)
 */

import { useState, useCallback } from 'react'
import { useConverter } from './hooks/useConverter'
import NFAForm from './components/NFAForm'
import AutomataGraph from './components/AutomataGraph'
import SimulationControls from './components/SimulationControls'
import Legend from './components/Legend'
import { GitMerge, AlertCircle } from 'lucide-react'

const VIEW_MODES = [
  { id: 'side',   label: 'Side by Side' },
  { id: 'nfa',    label: 'NFA only' },
  { id: 'dfa',    label: 'DFA only' },
]

export default function App() {
  const converter           = useConverter()
  const [stepIndex, setStepIndex] = useState(0)
  const [viewMode, setViewMode]   = useState('side')

  const result    = converter.data
  const error     = converter.error
  const loading   = converter.isPending

  const handleSubmit = useCallback(
    (payload) => {
      setStepIndex(0)
      converter.mutate(payload)
    },
    [converter]
  )

  const activeStates = result?.simulation?.steps[stepIndex]?.active_states ?? []
  const showSim      = !!result?.simulation

  const showNFA = viewMode === 'side' || viewMode === 'nfa'
  const showDFA = viewMode === 'side' || viewMode === 'dfa'

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-canvas">
      <header className="flex items-center gap-3 px-5 py-3 border-b border-border bg-surface shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-accent/20 border border-accent/40 flex items-center justify-center">
            <GitMerge size={16} className="text-accent" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-white tracking-tight leading-none">
              NFA → DFA Visualizer
            </h1>
            <p className="text-xs text-muted leading-none mt-0.5">
              Subset Construction · Step-by-step
            </p>
          </div>
        </div>
        {result && (
          <div className="ml-auto flex items-center gap-1 bg-canvas border border-border rounded-lg p-0.5">
            {VIEW_MODES.map((m) => (
              <button
                key={m.id}
                onClick={() => setViewMode(m.id)}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                  viewMode === m.id ? 'bg-accent text-white' : 'text-muted hover:text-white'
                }`}
              >
                {m.label}
              </button>
            ))}
          </div>
        )}
      </header>
      <div className="flex flex-1 overflow-hidden">
        <aside className="w-72 border-r border-border bg-surface flex flex-col overflow-y-auto shrink-0">
          <div className="p-4 flex-1">
            <NFAForm onSubmit={handleSubmit} loading={loading} />
          </div>
          {error && (
            <div className="mx-4 mb-4 bg-reject/10 border border-reject/40 rounded-lg px-3 py-2 flex gap-2">
              <AlertCircle size={14} className="text-red-400 shrink-0 mt-0.5" />
              <p className="text-xs text-red-400 font-mono break-all">
                {error.response?.data?.detail ?? error.message}
              </p>
            </div>
          )}
        </aside>
        <main className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 flex overflow-hidden min-h-0">
            {!result && !loading && (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center space-y-3">
                  <div className="w-16 h-16 rounded-full bg-surface border border-border flex items-center justify-center mx-auto">
                    <GitMerge size={28} className="text-muted" />
                  </div>
                  <p className="text-muted text-sm">Define an NFA and click <strong className="text-white">Convert &amp; Simulate</strong></p>
                  <p className="text-muted text-xs">Or pick an example from the sidebar →</p>
                </div>
              </div>
            )}
            {loading && (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center space-y-3">
                  <div className="w-10 h-10 border-2 border-accent border-t-transparent rounded-full animate-spin mx-auto" />
                  <p className="text-muted text-sm">Converting NFA to DFA…</p>
                </div>
              </div>
            )}
            {result && !loading && (
              <>
                {showNFA && (
                  <div className={`flex flex-col border-r border-border ${viewMode === 'side' ? 'w-1/2' : 'flex-1'}`}>
                    <AutomataGraph graphData={result.nfa} activeStates={showSim ? activeStates : []} title="NFA (original)" />
                  </div>
                )}
                {showDFA && (
                  <div className={`flex flex-col ${viewMode === 'side' ? 'w-1/2' : 'flex-1'}`}>
                    <AutomataGraph graphData={result.dfa} activeStates={[]} title="DFA (subset construction)" />
                  </div>
                )}
              </>
            )}
          </div>
          {result && <Legend />}
          {result?.simulation && (
            <SimulationControls
              steps={result.simulation.steps}
              stepIndex={stepIndex}
              onStepChange={setStepIndex}
              accepted={result.simulation.accepted}
            />
          )}
        </main>
      </div>
    </div>
  )
}
