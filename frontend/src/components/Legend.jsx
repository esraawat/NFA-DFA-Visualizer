export default function Legend() {
  const items = [
    { cls: 'border-2 border-dashed border-active bg-canvas', label: 'Start state' },
    { cls: 'border-2 border-accept bg-canvas ring-2 ring-accept/25', label: 'Accept state' },
    { cls: 'border-2 border-accent bg-accent/80', label: 'Active (current)' },
    { cls: 'border-2 border-gray-700 bg-canvas text-gray-600', label: 'Dead / trap state' },
  ]
  return (
    <div className="flex flex-wrap items-center gap-3 px-4 py-2 border-t border-border bg-surface/50">
      {items.map((item) => (
        <div key={item.label} className="flex items-center gap-2">
          <div className={`w-5 h-5 rounded-full ${item.cls}`} />
          <span className="text-xs text-muted">{item.label}</span>
        </div>
      ))}
    </div>
  )
}
