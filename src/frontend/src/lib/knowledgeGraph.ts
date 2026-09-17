export type GraphNodeType =
  | 'standard'
  | 'section'
  | 'clause'
  | 'concept'
  | 'contract_type'
  | 'risk_pattern'
  | 'rule'
  | 'control'
  | 'finding'
  | 'authority'

export type GraphMode = 'live' | 'preview' | 'contract'
export type EdgeReviewStatus = 'approved' | 'candidate'

export type KnowledgeGraphNode = {
  id: string
  type: GraphNodeType
  label: string
  description?: string | null
  clauseId?: string | null
  printedPage?: number | null
}

export type KnowledgeGraphEdge = {
  id: string
  source: string
  target: string
  predicate: string
  evidenceClauseId?: string | null
  printedPage?: number | null
  approvalStatus: EdgeReviewStatus
  scholarReviewer?: string | null
}

export type KnowledgeGraphPath = {
  nodeIds: string[]
  edgeIds: string[]
}

export type KnowledgeGraphResult = {
  seed: KnowledgeGraphNode
  nodes: KnowledgeGraphNode[]
  edges: KnowledgeGraphEdge[]
  paths: KnowledgeGraphPath[]
  truncated: boolean
  mode: GraphMode
  demoOnly: boolean
  queryEngine?: string
}

export type ApiKnowledgeGraphNode = {
  id: string
  type: GraphNodeType
  label: string
  description?: string | null
  clause_id?: string | null
  printed_page?: number | null
}

export type ApiKnowledgeGraph = {
  seed: ApiKnowledgeGraphNode
  nodes: ApiKnowledgeGraphNode[]
  edges: Array<{
    id: string
    source: string
    target: string
    predicate: string
    evidence_clause_id?: string | null
    printed_page?: number | null
    approval_status?: EdgeReviewStatus
    scholar_reviewer?: string | null
  }>
  paths: Array<{ node_ids: string[]; edge_ids: string[] }>
  truncated: boolean
  mode?: GraphMode
  demo_only?: boolean
  query_engine?: string
}

function nodeFromApi(node: ApiKnowledgeGraphNode): KnowledgeGraphNode {
  return {
    id: node.id,
    type: node.type,
    label: node.label,
    description: node.description,
    clauseId: node.clause_id,
    printedPage: node.printed_page,
  }
}

export function normaliseKnowledgeGraph(graph: ApiKnowledgeGraph): KnowledgeGraphResult {
  return {
    mode: graph.mode === 'contract' || graph.mode === 'preview' ? graph.mode : 'live',
    demoOnly: Boolean(graph.demo_only),
    queryEngine: graph.query_engine,
    seed: nodeFromApi(graph.seed),
    nodes: graph.nodes.map(nodeFromApi),
    edges: graph.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      predicate: edge.predicate,
      evidenceClauseId: edge.evidence_clause_id,
      printedPage: edge.printed_page,
      approvalStatus: edge.approval_status === 'approved' ? 'approved' : 'candidate',
      scholarReviewer: edge.scholar_reviewer,
    })),
    paths: graph.paths.map((path) => ({ nodeIds: path.node_ids, edgeIds: path.edge_ids })),
    truncated: graph.truncated,
  }
}

const previewGraph: KnowledgeGraphResult = {
  mode: 'preview',
  demoOnly: true,
  seed: {
    id: 'risk:variable-profit-benchmark',
    type: 'risk_pattern',
    label: 'Variable profit benchmark',
    description: 'A sale price determined by a future floating benchmark.',
  },
  nodes: [
    { id: 'risk:variable-profit-benchmark', type: 'risk_pattern', label: 'Variable profit benchmark', description: 'A sale price determined by a future floating benchmark.' },
    { id: 'rule:fixed-price', type: 'rule', label: 'Fixed price and profit', description: 'The sale price and profit are fixed and known at signature.' },
    { id: 'clause:ss8:4/6', type: 'clause', label: 'SS 8 · 4/6', clauseId: '4/6', printedPage: 211, description: 'Evidence reference for the reviewed mapping.' },
    { id: 'standard:ss8', type: 'standard', label: 'AAOIFI Shari’ah Standard 8', description: 'Murabahah (Revised Standard), English 2015 compilation.' },
    { id: 'control:fixed-sale-price', type: 'control', label: 'Confirm the executed sale price', description: 'Control proposed for human review before contract execution.' },
  ],
  edges: [
    { id: 'edge:variable-profit-conflicts-fixed-price', source: 'risk:variable-profit-benchmark', target: 'rule:fixed-price', predicate: 'CONFLICTS_WITH', evidenceClauseId: '4/6', printedPage: 211, approvalStatus: 'approved', scholarReviewer: 'Required before corpus publication' },
    { id: 'edge:fixed-price-evidenced-by-ss8-4-6', source: 'rule:fixed-price', target: 'clause:ss8:4/6', predicate: 'EVIDENCED_BY', evidenceClauseId: '4/6', printedPage: 211, approvalStatus: 'approved', scholarReviewer: 'Required before corpus publication' },
    { id: 'edge:ss8-4-6-contained-by-ss8', source: 'clause:ss8:4/6', target: 'standard:ss8', predicate: 'CONTAINS', evidenceClauseId: '4/6', printedPage: 211, approvalStatus: 'approved', scholarReviewer: 'Required before corpus publication' },
    { id: 'edge:fixed-price-requires-control', source: 'rule:fixed-price', target: 'control:fixed-sale-price', predicate: 'REQUIRES', evidenceClauseId: '4/6', printedPage: 211, approvalStatus: 'approved', scholarReviewer: 'Required before corpus publication' },
  ],
  paths: [{ nodeIds: ['risk:variable-profit-benchmark', 'rule:fixed-price', 'clause:ss8:4/6'], edgeIds: ['edge:variable-profit-conflicts-fixed-price', 'edge:fixed-price-evidenced-by-ss8-4-6'] }],
  truncated: false,
}

async function jsonPayload<T>(response: Response): Promise<T | null> {
  const body = await response.text()
  if (!body.trim()) return null
  try {
    return JSON.parse(body) as T
  } catch {
    return null
  }
}

async function responseError(response: Response, fallback: string) {
  const payload = await jsonPayload<{ detail?: string }>(response)
  return payload?.detail?.trim() || fallback
}

export async function lookupKnowledgeGraph(seed: string): Promise<KnowledgeGraphResult> {
  try {
    const response = await fetch('/api/v1/standards/graph/lookup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ seed, max_hops: 2, node_limit: 50, edge_limit: 75 }),
    })
    if (!response.ok) return previewGraph
    const payload = await jsonPayload<ApiKnowledgeGraph>(response)
    return payload ? normaliseKnowledgeGraph(payload) : previewGraph
  } catch {
    return previewGraph
  }
}

export async function queryContractKnowledgeGraph(analysisId: string, query: string): Promise<KnowledgeGraphResult> {
  const response = await fetch('/api/v1/contracts/graph/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ analysis_id: analysisId, query }),
  })
  if (!response.ok) throw new Error(await responseError(response, 'The graph query could not be completed.'))
  const payload = await jsonPayload<{ graph: ApiKnowledgeGraph }>(response)
  if (!payload?.graph) throw new Error('The graph query returned no readable result.')
  return normaliseKnowledgeGraph(payload.graph)
}
