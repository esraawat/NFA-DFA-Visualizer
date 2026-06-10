import { Handle, Position } from 'reactflow'

export default function AutomataNode({ data }) {
  const { label, isStart, isAccept, isDead, isActive } = data

  let cls = 'rf-node'
  if (isDead)   cls += ' is-dead'
  if (isStart)  cls += ' is-start'
  if (isAccept) cls += ' is-accept'
  if (isActive) cls += ' is-active'

  return (
    <>
      <Handle type="target" position={Position.Left}  style={{ opacity: 0 }} />
      <div className={cls} title={label}>
        {label}
      </div>
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
    </>
  )
}
