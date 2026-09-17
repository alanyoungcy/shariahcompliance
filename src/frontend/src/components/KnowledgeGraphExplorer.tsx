import { useMemo, useRef, useState, type PointerEvent as ReactPointerEvent } from 'react'
import { ArrowRight, CheckCircle2, Code2, Network, RotateCcw, Search, X } from 'lucide-react'
import { queryContractKnowledgeGraph, type KnowledgeGraphEdge, type KnowledgeGraphNode, type KnowledgeGraphResult } from '../lib/knowledgeGraph'

type PositionedNode = KnowledgeGraphNode & { x: number; y: number }

type Props = {
  analysisId?: string
  graph: KnowledgeGraphResult
  isLoading: boolean
  onClose: () => void
}

const NODE_COLOURS: Record<KnowledgeGraphNode['type'], string> = {
  standard: '#111113',
  section: '#4d8768',
  clause: '#cf2028',
  concept: '#71716d',
  contract_type: '#71716d',
  risk_pattern: '#d58b1f',
  rule: '#4d8768',
  control: '#526f9a',
  finding: '#cf2028',
  authority: '#111113',
}

const NODE_LABELS: Record<KnowledgeGraphNode['type'], string> = {
  standard: 'Standard',
  section: 'Section',
  clause: 'Clause',
  concept: 'Concept',
  contract_type: 'Contract type',
  risk_pattern: 'Risk pattern',
  rule: 'Rule',
  control: 'Control',
  finding: 'Finding',
  authority: 'Authority',
}

const CANVAS = { width: 900, height: 560 }
const EXAMPLE_QUERY = 'MATCH (f:finding)-[r:EVIDENCED_BY]->(c:clause) RETURN f,r,c'
const NODE_RADIUS = 23

function resolveNodeId(value: string | { id: string }) {
  return typeof value === 'string' ? value : value.id
}

function shortLabel(label: string) {
  const words = label.replace(/\s+/g, ' ').trim().split(' ')
  const lines: string[] = []
  let line = ''
  for (const word of words) {
    const next = line ? `${line} ${word}` : word
    if (next.length > 22 && line) {
      lines.push(line)
      line = word
      if (lines.length === 2) break
    } else {
      line = next
    }
  }
  if (lines.length < 2 && line) lines.push(line)
  if (lines.length === 2 && words.join(' ').length > lines.join(' ').length) lines[1] = `${lines[1].slice(0, 19)}…`
  return lines
}

function connectedComponents(nodes: KnowledgeGraphNode[], edges: KnowledgeGraphEdge[]) {
  const adjacency = new Map(nodes.map((node) => [node.id, new Set<string>()]))
  for (const edge of edges) {
    const source = resolveNodeId(edge.source)
    const target = resolveNodeId(edge.target)
    adjacency.get(source)?.add(target)
    adjacency.get(target)?.add(source)
  }
  const visited = new Set<string>()
  const components: KnowledgeGraphNode[][] = []
  for (const node of nodes) {
    if (visited.has(node.id)) continue
    const queue = [node.id]
    const component: KnowledgeGraphNode[] = []
    visited.add(node.id)
    while (queue.length) {
      const id = queue.shift()!
      const current = nodes.find((candidate) => candidate.id === id)
      if (current) component.push(current)
      for (const neighbour of adjacency.get(id) ?? []) {
        if (!visited.has(neighbour)) {
          visited.add(neighbour)
          queue.push(neighbour)
        }
      }
    }
    components.push(component)
  }
  return { components: components.sort((left, right) => right.length - left.length), adjacency }
}

function componentLayout(graph: KnowledgeGraphResult): PositionedNode[] {
  const { components, adjacency } = connectedComponents(graph.nodes, graph.edges)
  const columns = components.length > 1 ? 2 : 1
  const rows = Math.ceil(components.length / columns)
  const cellWidth = CANVAS.width / columns
  const cellHeight = CANVAS.height / rows
  const positioned: PositionedNode[] = []

  components.forEach((component, index) => {
    const col = index % columns
    const row = Math.floor(index / columns)
    const centerX = cellWidth * (col + 0.5)
    const centerY = cellHeight * (row + 0.5)
    const ordered = [...component].sort((left, right) => {
      const leftPriority = left.id === graph.seed.id ? 1000 : (adjacency.get(left.id)?.size ?? 0)
      const rightPriority = right.id === graph.seed.id ? 1000 : (adjacency.get(right.id)?.size ?? 0)
      return rightPriority - leftPriority || left.label.localeCompare(right.label)
    })
    const focal = ordered[0]
    if (!focal) return
    positioned.push({ ...focal, x: centerX, y: centerY })
    const surrounding = ordered.slice(1)
    const radius = Math.max(68, Math.min(cellWidth, cellHeight) * (surrounding.length > 5 ? 0.31 : 0.26))
    surrounding.forEach((node, nodeIndex) => {
      const angle = -Math.PI / 2 + (2 * Math.PI * nodeIndex) / surrounding.length
      positioned.push({
        ...node,
        x: Math.max(68, Math.min(CANVAS.width - 68, centerX + Math.cos(angle) * radius)),
        y: Math.max(72, Math.min(CANVAS.height - 72, centerY + Math.sin(angle) * radius)),
      })
    })
  })
  return positioned
}

function GraphCanvas({ graph, activeNodeId, onSelectNode }: {
  graph: KnowledgeGraphResult
  activeNodeId: string
  onSelectNode: (id: string) => void
}) {
  const layout = useMemo<PositionedNode[]>(() => componentLayout(graph), [graph])
  const initialPositions = useMemo(
    () => Object.fromEntries(layout.map((node) => [node.id, { x: node.x, y: node.y }])),
    [layout],
  )
  const [positions, setPositions] = useState(initialPositions)
  const canvasRef = useRef<SVGSVGElement>(null)
  const dragRef = useRef<{ id: string; startX: number; startY: number; moved: boolean } | null>(null)
  const suppressClickRef = useRef(false)

  const pointInCanvas = (event: ReactPointerEvent<SVGGElement>) => {
    const bounds = canvasRef.current?.getBoundingClientRect()
    if (!bounds) return { x: 0, y: 0 }
    return {
      x: ((event.clientX - bounds.left) / bounds.width) * CANVAS.width,
      y: ((event.clientY - bounds.top) / bounds.height) * CANVAS.height,
    }
  }

  const beginDrag = (event: ReactPointerEvent<SVGGElement>, node: PositionedNode) => {
    const point = pointInCanvas(event)
    dragRef.current = { id: node.id, startX: point.x, startY: point.y, moved: false }
    event.currentTarget.setPointerCapture(event.pointerId)
  }

  const moveDrag = (event: ReactPointerEvent<SVGGElement>) => {
    const drag = dragRef.current
    if (!drag) return
    const point = pointInCanvas(event)
    if (Math.hypot(point.x - drag.startX, point.y - drag.startY) > 3) drag.moved = true
    setPositions((current) => ({
      ...current,
      [drag.id]: {
        x: Math.max(48, Math.min(CANVAS.width - 48, point.x)),
        y: Math.max(48, Math.min(CANVAS.height - 58, point.y)),
      },
    }))
  }

  const endDrag = (event: ReactPointerEvent<SVGGElement>) => {
    const drag = dragRef.current
    if (!drag) return
    if (event.currentTarget.hasPointerCapture(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId)
    if (drag.moved) {
      suppressClickRef.current = true
      window.setTimeout(() => { suppressClickRef.current = false }, 0)
    }
    dragRef.current = null
  }

  const positioned = new Map(layout.map((node) => [node.id, { ...node, ...positions[node.id] }]))
  if (!layout.length) return <div className="graph-empty"><Search size={22} /><strong>No relationships matched this query.</strong><span>Use the example query or reset the graph.</span></div>

  return <div className="graph-canvas-wrap">
    <div className="graph-canvas-hint">Drag nodes to arrange the map. Select a node to inspect its evidence.</div>
    <svg ref={canvasRef} className="graph-canvas" viewBox={`0 0 ${CANVAS.width} ${CANVAS.height}`} role="img" aria-label="Draggable knowledge graph relationship map">
      <defs>
        <marker id="graph-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,6 L6,3 z" fill="#777772" />
        </marker>
      </defs>
      {graph.edges.map((edge) => {
        const source = positioned.get(resolveNodeId(edge.source))
        const target = positioned.get(resolveNodeId(edge.target))
        if (!source || !target) return null
        return <g className="graph-edge" key={edge.id}>
          <line x1={source.x} y1={source.y} x2={target.x} y2={target.y} markerEnd="url(#graph-arrow)" />
          <title>{edge.predicate.replaceAll('_', ' ')}</title>
        </g>
      })}
      {layout.map((node) => {
        const position = positioned.get(node.id)!
        const isActive = node.id === activeNodeId
        return <g className={isActive ? 'graph-node graph-node--active' : 'graph-node'} key={node.id} onPointerDown={(event) => beginDrag(event, position)} onPointerMove={moveDrag} onPointerUp={endDrag} onPointerCancel={endDrag} onClick={() => { if (!suppressClickRef.current) onSelectNode(node.id) }} tabIndex={0} role="button" aria-label={`Inspect or drag ${node.label}`} onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') onSelectNode(node.id) }}>
          <title>{node.label}</title>
          <circle cx={position.x} cy={position.y} r={isActive ? NODE_RADIUS + 4 : NODE_RADIUS} fill={NODE_COLOURS[node.type]} />
          <text className="graph-node-type" x={position.x} y={position.y + 4}>{NODE_LABELS[node.type].slice(0, 3).toUpperCase()}</text>
          <text className="graph-node-label" x={position.x} y={position.y + 42}>{shortLabel(node.label).map((line, index) => <tspan key={line} x={position.x} dy={index ? 12 : 0}>{line}</tspan>)}</text>
        </g>
      })}
    </svg>
  </div>
}

function EvidenceDetails({ node, edges, nodesById, onSelectNode, contractGraph }: {
  node?: KnowledgeGraphNode
  edges: KnowledgeGraphEdge[]
  nodesById: Map<string, KnowledgeGraphNode>
  onSelectNode: (id: string) => void
  contractGraph: boolean
}) {
  if (!node) return <aside className="graph-inspector graph-inspector--empty"><Network size={24} /><h3>Inspect a relationship</h3><p>Run a query or select a node in the relationship map to read its source-grounded context.</p></aside>
  const connectedEdges = edges.filter((edge) => edge.source === node.id || edge.target === node.id)
  return <aside className="graph-inspector" aria-live="polite">
    <div className="graph-inspector__type"><span className="graph-key" style={{ background: NODE_COLOURS[node.type] }} />{NODE_LABELS[node.type]}</div>
    <h3>{node.label}</h3>
    <p>{node.description ?? (contractGraph ? 'Semantic graph node proposed for reviewer inspection.' : 'No description is available for this graph node.')}</p>
    {(node.clauseId || node.printedPage) && <div className="graph-citation"><span>{contractGraph ? 'Uploaded contract evidence' : 'Evidence clause'}</span><strong>{node.clauseId ? (contractGraph ? node.clauseId : `AAOIFI SS 8 · ${node.clauseId}`) : 'Page reference'}</strong>{node.printedPage && <small>Page {node.printedPage}</small>}</div>}
    <div className="graph-inspector__relationships">
      <span>Connected relationships</span>
      {connectedEdges.map((edge) => {
        const otherId = edge.source === node.id ? edge.target : edge.source
        const otherNode = nodesById.get(otherId)
        return <button key={edge.id} onClick={() => onSelectNode(otherId)}>
          <span>{edge.predicate.replaceAll('_', ' ').toLowerCase()}</span>
          <strong>{otherNode?.label ?? 'Linked record'}</strong>
          <ArrowRight size={14} />
        </button>
      })}
      {!connectedEdges.length && <small className="graph-no-connections">No retained relationships for this query.</small>}
    </div>
  </aside>
}

export function KnowledgeGraphExplorer({ analysisId, graph, isLoading, onClose }: Props) {
  const [displayGraph, setDisplayGraph] = useState(graph)
  const [activeNodeId, setActiveNodeId] = useState(graph.seed.id)
  const [query, setQuery] = useState(EXAMPLE_QUERY)
  const [queryError, setQueryError] = useState<string | null>(null)
  const [isQuerying, setIsQuerying] = useState(false)
  const [layoutRevision, setLayoutRevision] = useState(0)
  const isContractGraph = displayGraph.mode === 'contract'
  const nodesById = useMemo(() => new Map(displayGraph.nodes.map((node) => [node.id, node])), [displayGraph.nodes])
  const activeNode = nodesById.get(activeNodeId) ?? displayGraph.nodes[0]

  const runQuery = async () => {
    if (!analysisId || !query.trim() || isQuerying) return
    setIsQuerying(true)
    setQueryError(null)
    try {
      const result = await queryContractKnowledgeGraph(analysisId, query)
      setDisplayGraph(result)
      setActiveNodeId(result.seed.id)
      setLayoutRevision((revision) => revision + 1)
    } catch (error) {
      setQueryError(error instanceof Error ? error.message : 'The graph query could not be completed.')
    } finally {
      setIsQuerying(false)
    }
  }

  const resetGraph = () => {
    setDisplayGraph(graph)
    setActiveNodeId(graph.seed.id)
    setQueryError(null)
    setLayoutRevision((revision) => revision + 1)
  }

  return <div className="graph-overlay" role="presentation">
    <section className="graph-drawer" role="dialog" aria-modal="true" aria-labelledby="relationship-map-title">
      <header className="graph-drawer__header">
        <div><div className="eyebrow"><Network size={13} /> Knowledge graph lookup</div><h2 id="relationship-map-title">Relationship map</h2></div>
        <button className="graph-close" onClick={onClose} aria-label="Close relationship map"><X size={20} /></button>
      </header>
      <div className="graph-drawer__context">
        <div><span>Seed</span><strong>{displayGraph.seed.label}</strong></div>
        <div><span>Traversal</span><strong>{isContractGraph ? 'Source-grounded candidate relationships' : '2 hops · approved edges only'}</strong></div>
        <div><span>Display</span><strong>{displayGraph.nodes.length} nodes · {displayGraph.edges.length} relationships</strong></div>
      </div>
      {displayGraph.demoOnly && <div className="graph-preview-note"><CheckCircle2 size={16} /><span>Demo-only mapping illustrates the graph contract. The AAOIFI corpus remains unavailable until source rights and scholar approval are recorded.</span></div>}
      {isContractGraph && <div className="graph-contract-note"><CheckCircle2 size={16} /><span>Relationships are semantic, source-grounded candidates from this uploaded contract. Scholar review remains pending.</span></div>}
      {isContractGraph && <form className="graph-query" onSubmit={(event) => { event.preventDefault(); void runQuery() }}>
        <div><label htmlFor="graph-query"><Code2 size={14} /> Bounded Cypher-compatible query</label><input id="graph-query" value={query} onChange={(event) => setQuery(event.target.value)} spellCheck={false} aria-describedby="graph-query-help" /></div>
        <button className="secondary-action graph-query__run" type="submit" disabled={isQuerying}>{isQuerying ? 'Running…' : 'Run query'}</button>
        <button className="graph-reset" type="button" onClick={resetGraph}><RotateCcw size={14} /> Reset</button>
        <small id="graph-query-help">Example: MATCH (f:finding)-[r:EVIDENCED_BY]-&gt;(c:clause) RETURN f,r,c</small>
        {queryError && <p className="graph-query__error">{queryError}</p>}
      </form>}
      <div className="graph-workspace">
        {isLoading ? <div className="graph-loading">Loading source-grounded relationships…</div> : <GraphCanvas key={`${layoutRevision}:${displayGraph.nodes.map((node) => node.id).join('|')}`} graph={displayGraph} activeNodeId={activeNodeId} onSelectNode={setActiveNodeId} />}
        <EvidenceDetails node={activeNode} edges={displayGraph.edges} nodesById={nodesById} onSelectNode={setActiveNodeId} contractGraph={isContractGraph} />
      </div>
      <footer className="graph-drawer__footer"><span>{displayGraph.truncated ? 'Showing a bounded graph view. Refine the query to inspect another path.' : isContractGraph ? 'Every retained relationship links to uploaded-contract evidence.' : 'Every shown relationship has a clause reference or review annotation.'}</span><span>AI assists analysis. Qualified scholars retain final authority.</span></footer>
    </section>
  </div>
}
