import { useMemo } from 'react'
import ReactFlow, {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  MarkerType,
  useNodesState,
  useEdgesState,
} from 'reactflow'
import 'reactflow/dist/style.css'
import AutomataNode from './AutomataNode'

const NODE_TYPES = { automata: AutomataNode }

function circularLayout(nodes, cx = 300, cy = 220, baseR = 160) {
  const n = nodes.length
  if (n === 0) return []
  const r = Math.max(baseR, n * 28)
  return nodes.map((node, i) => {
    const angle = (2 * Math.PI * i) / n - Math.PI / 2
    return {
      ...node,
      position: {
        x: cx + r * Math.cos(angle) - 28,
        y: cy + r * Math.sin(angle) - 28,
      },
    }
  })
}

function buildRFNodes(graphData, activeSet) {
  const raw = graphData.nodes.map((n) => ({
    id: n.id,
    type: 'automata',
    data: {
      label:    n.label,
      isStart:  n.is_start,
      isAccept: n.is_accept,
      isDead:   n.is_dead,
      isActive: activeSet.has(n.id),
    },
    style: { background: 'transparent', border: 'none', padding: 0 },
  }))
  return circularLayout(raw)
}

function buildRFEdges(graphData) {
  return graphData.edges.map((e) => {
    const isSelf = e.source === e.target
    return {
      id:     e.id,
      source: e.source,
      target: e.target,
      label:  e.label,
      type:   isSelf ? 'smoothstep' : 'bezier',
      markerEnd: { type: MarkerType.ArrowClosed, color: '#7c3aed', width: 18, height: 18 },
      style:      { stroke: '#7c3aed', strokeWidth: 1.8 },
      labelStyle: { fill: '#c9d1d9', fontSize: 11, fontFamily: "'JetBrains Mono', monospace" },
      labelBgStyle:   { fill: '#161b22', fillOpacity: 0.95, rx: 4 },
      labelBgPadding: [4, 6],
    }
  })
}

export default function AutomataGraph({ graphData, activeStates = [], title }) {
  const activeSet = useMemo(() => new Set(activeStates), [activeStates])
  const rfNodes   = useMemo(() => buildRFNodes(graphData, activeSet), [graphData, activeSet])
  const rfEdges   = useMemo(() => buildRFEdges(graphData), [graphData])

  const [nodes, , onNodesChange] = useNodesState(rfNodes)
  const [edges, , onEdgesChange] = useEdgesState(rfEdges)

  const liveNodes = useMemo(
    () => nodes.map((n) => ({ ...n, data: { ...n.data, isActive: activeSet.has(n.id) } })),
    [nodes, activeSet]
  )

  return (
    <div className="flex flex-col h-full">
      {title && (
        <div className="flex items-center gap-2 px-3 py-2 border-b border-border">
          <span className="text-xs font-mono font-semibold text-muted uppercase tracking-widest">
            {title}
          </span>
          <span className="text-xs text-muted">
            {graphData.nodes.length} states · {graphData.edges.length} transitions
          </span>
        </div>
      )}
      <div className="flex-1 min-h-0">
        <ReactFlow
          nodes={liveNodes}
          edges={rfEdges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={NODE_TYPES}
          fitView
          fitViewOptions={{ padding: 0.35 }}
          minZoom={0.3}
          maxZoom={3}
          proOptions={{ hideAttribution: true }}
        >
          <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#21262d" />
          <Controls showInteractive={false} />
          <MiniMap
            nodeColor={(n) =>
              n.data?.isActive ? '#7c3aed' : n.data?.isAccept ? '#16a34a' : '#21262d'
            }
            maskColor="rgba(13,17,23,0.7)"
          />
        </ReactFlow>
      </div>
    </div>
  )
}
