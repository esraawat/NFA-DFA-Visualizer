import { useState, useCallback } from 'react'
import { Plus, Trash2, Play, Zap, ChevronDown, ChevronUp } from 'lucide-react'
import { PRESETS } from '../presets'

const DEFAULT_NFA = {
  states: ['q0', 'q1', 'q2'],
  alphabet: ['a', 'b'],
  transitions: [
    { from: 'q0', symbol: 'a', to: 'q0,q1' },
    { from: 'q0', symbol: 'b', to: 'q0' },
    { from: 'q1', symbol: 'b', to: 'q2' },
  ],
  start_state: 'q0',
  accept_states: ['q2'],
  input_string: 'aab',
}

function Chip({ label, onRemove, color = 'bg-surface border-border text-muted' }) {
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-mono border ${color}`}>
      {label}
      {onRemove && (
        <button onClick={onRemove} className="hover:text-reject transition-colors ml-0.5">×</button>
      )}
    </span>
  )
}

function TagInput({ label, values, onChange, placeholder }) {
  const [input, setInput] = useState('')
  const add = () => {
    const v = input.trim()
    if (v && !values.includes(v)) onChange([...values, v])
    setInput('')
  }
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-semibold text-muted uppercase tracking-wider">{label}</label>
      <div className="flex gap-1.5">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), add())}
          placeholder={placeholder}
          className="flex-1 bg-canvas border border-border rounded px-2.5 py-1.5 text-xs font-mono focus:outline-none focus:border-accent text-white placeholder-muted"
        />
        <button onClick={add} className="px-2.5 py-1.5 bg-surface border border-border rounded hover:border-accent text-muted hover:text-white transition-colors">
          <Plus size={13} />
        </button>
      </div>
      <div className="flex flex-wrap gap-1">
        {values.map((v) => (
          <Chip key={v} label={v} onRemove={() => onChange(values.filter((x) => x !== v))} />
        ))}
      </div>
    </div>
  )
}

export default function NFAForm({ onSubmit, loading }) {
  const [states, setStates]           = useState(DEFAULT_NFA.states)
  const [alphabet, setAlphabet]       = useState(DEFAULT_NFA.alphabet)
  const [transitions, setTransitions] = useState(DEFAULT_NFA.transitions)
  const [startState, setStartState]   = useState(DEFAULT_NFA.start_state)
  const [acceptStates, setAcceptStates] = useState(DEFAULT_NFA.accept_states)
  const [inputString, setInputString] = useState(DEFAULT_NFA.input_string)
  const [showPresets, setShowPresets] = useState(false)
  const [errors, setErrors]           = useState([])

  const addTransition = () =>
    setTransitions((t) => [...t, { from: states[0] || '', symbol: alphabet[0] || '', to: '' }])

  const updateTrans = (i, field, val) =>
    setTransitions((t) => t.map((r, idx) => (idx === i ? { ...r, [field]: val } : r)))

  const removeTrans = (i) =>
    setTransitions((t) => t.filter((_, idx) => idx !== i))

  const loadPreset = useCallback((preset) => {
    const nfa = preset.nfa
    setStates(nfa.states)
    setAlphabet(nfa.alphabet)
    setStartState(nfa.start_state)
    setAcceptStates(nfa.accept_states)
    setInputString(preset.testStrings[0] ?? '')
    const rows = []
    for (const [from, symMap] of Object.entries(nfa.transitions)) {
      for (const [sym, targets] of Object.entries(symMap)) {
        rows.push({ from, symbol: sym, to: Array.isArray(targets) ? targets.join(',') : targets })
      }
    }
    setTransitions(rows)
    setShowPresets(false)
    setErrors([])
  }, [])

  const handleSubmit = () => {
    const errs = []
    if (!startState || !states.includes(startState))
      errs.push(`Start state '${startState}' must be in the states list.`)
    for (const acc of acceptStates)
      if (!states.includes(acc)) errs.push(`Accept state '${acc}' not in states.`)
    if (errs.length) { setErrors(errs); return }
    setErrors([])

    const transDict = {}
    for (const row of transitions) {
      if (!row.from || !row.symbol || !row.to) continue
      const targets = row.to.split(',').map((s) => s.trim()).filter(Boolean)
      if (!transDict[row.from]) transDict[row.from] = {}
      transDict[row.from][row.symbol] = targets
    }

    onSubmit({
      states,
      alphabet,
      transitions: transDict,
      start_state: startState,
      accept_states: acceptStates,
      input_string: inputString || null,
    })
  }

  const symbolOptions = ['epsilon', ...alphabet]

  return (
    <div className="space-y-5 text-sm">
      <div className="flex items-center justify-between">
        <h2 className="text-xs font-semibold text-muted uppercase tracking-widest">Define NFA</h2>
        <button
          onClick={() => setShowPresets((x) => !x)}
          className="flex items-center gap-1 text-xs text-accent hover:text-violet-300 transition-colors font-medium"
        >
          <Zap size={12} />
          Examples
          {showPresets ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </button>
      </div>

      {showPresets && (
        <div className="bg-canvas border border-border rounded-lg overflow-hidden">
          {PRESETS.map((p) => (
            <button
              key={p.name}
              onClick={() => loadPreset(p)}
              className="w-full text-left px-3 py-2.5 hover:bg-surface border-b border-border last:border-0 transition-colors"
            >
              <div className="text-xs font-mono font-semibold text-white">{p.name}</div>
              <div className="text-xs text-muted mt-0.5">{p.description}</div>
            </button>
          ))}
        </div>
      )}

      <TagInput label="States" values={states} onChange={setStates} placeholder="Add state, e.g. q3" />
      <TagInput label="Alphabet (Σ)" values={alphabet} onChange={setAlphabet} placeholder="Add symbol, e.g. a" />

      <div className="space-y-1.5">
        <label className="text-xs font-semibold text-muted uppercase tracking-wider">Start State</label>
        <select
          value={startState}
          onChange={(e) => setStartState(e.target.value)}
          className="w-full bg-canvas border border-border rounded px-2.5 py-1.5 text-xs font-mono focus:outline-none focus:border-accent text-white"
        >
          {states.map((s) => <option key={s}>{s}</option>)}
        </select>
      </div>

      <div className="space-y-1.5">
        <label className="text-xs font-semibold text-muted uppercase tracking-wider">Accept States</label>
        <div className="flex flex-wrap gap-1">
          {states.map((s) => (
            <button
              key={s}
              onClick={() =>
                setAcceptStates((acc) =>
                  acc.includes(s) ? acc.filter((x) => x !== s) : [...acc, s]
                )
              }
              className={`px-2.5 py-1 rounded text-xs font-mono border transition-colors ${
                acceptStates.includes(s)
                  ? 'bg-accept/20 border-accept text-green-300'
                  : 'bg-canvas border-border text-muted hover:border-muted'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold text-muted uppercase tracking-wider">Transitions (δ)</label>
          <button onClick={addTransition} className="flex items-center gap-1 text-xs text-accent hover:text-violet-300 transition-colors">
            <Plus size={12} /> Add row
          </button>
        </div>
        <div className="space-y-1.5 max-h-52 overflow-y-auto pr-0.5">
          {transitions.length === 0 && (
            <p className="text-xs text-muted italic py-2 text-center">No transitions yet</p>
          )}
          {transitions.map((row, i) => (
            <div key={i} className="flex items-center gap-1">
              <select
                value={row.from}
                onChange={(e) => updateTrans(i, 'from', e.target.value)}
                className="w-16 bg-canvas border border-border rounded px-1.5 py-1 text-xs font-mono text-white focus:outline-none focus:border-accent"
              >
                {states.map((s) => <option key={s}>{s}</option>)}
              </select>
              <span className="text-muted text-xs">─</span>
              <select
                value={row.symbol}
                onChange={(e) => updateTrans(i, 'symbol', e.target.value)}
                className="w-20 bg-canvas border border-border rounded px-1.5 py-1 text-xs font-mono text-white focus:outline-none focus:border-accent"
              >
                {symbolOptions.map((s) => (
                  <option key={s} value={s}>{s === 'epsilon' ? 'ε' : s}</option>
                ))}
              </select>
              <span className="text-muted text-xs">→</span>
              <input
                value={row.to}
                onChange={(e) => updateTrans(i, 'to', e.target.value)}
                placeholder="q1,q2"
                className="flex-1 bg-canvas border border-border rounded px-1.5 py-1 text-xs font-mono text-white focus:outline-none focus:border-accent placeholder-muted"
              />
              <button onClick={() => removeTrans(i)} className="text-muted hover:text-reject transition-colors flex-shrink-0">
                <Trash2 size={12} />
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-1.5">
        <label className="text-xs font-semibold text-muted uppercase tracking-wider">
          Test String <span className="text-muted font-normal normal-case">(optional)</span>
        </label>
        <input
          value={inputString}
          onChange={(e) => setInputString(e.target.value)}
          placeholder="e.g. aab"
          className="w-full bg-canvas border border-border rounded px-2.5 py-1.5 text-xs font-mono text-white focus:outline-none focus:border-accent placeholder-muted"
        />
      </div>

      {errors.length > 0 && (
        <div className="bg-reject/10 border border-reject/40 rounded-lg px-3 py-2 space-y-1">
          {errors.map((e, i) => (
            <p key={i} className="text-xs text-red-400 font-mono">{e}</p>
          ))}
        </div>
      )}

      <button
        onClick={handleSubmit}
        disabled={loading}
        className="w-full flex items-center justify-center gap-2 bg-accent hover:bg-violet-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm py-2.5 rounded-lg transition-colors"
      >
        <Play size={14} />
        {loading ? 'Converting…' : 'Convert & Simulate'}
      </button>
    </div>
  )
}
