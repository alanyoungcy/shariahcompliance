import { useMemo, useRef, useState, type ChangeEvent, type RefObject } from 'react'
import { AaoifiReferenceList, StandardsDialog } from './components/AaoifiReferences'
import type { AaoifiReference } from './lib/aaoifiReferences'
import { KnowledgeGraphExplorer } from './components/KnowledgeGraphExplorer'
import { PdfHighlightPreview } from './components/PdfHighlightPreview'
import { normaliseKnowledgeGraph, type ApiKnowledgeGraph, type KnowledgeGraphResult } from './lib/knowledgeGraph'
import {
  AlertTriangle,
  ArrowDownToLine,
  ArrowRight,
  BookOpen,
  Check,
  ChevronDown,
  ChevronRight,
  CircleHelp,
  Clock3,
  FileSearch,
  FileText,
  Layers3,
  Menu,
  Network,
  Search,
  ShieldCheck,
  Sparkles,
  Upload,
  X,
} from 'lucide-react'
import './App.css'

type Tab = 'findings' | 'clauses' | 'guidance'
type Surface = 'workspace' | 'library' | 'insights'
type Severity = 'critical' | 'high' | 'medium'

type Finding = {
  id: string
  type: string
  severity: Severity
  title: string
  clause: string
  excerpt: string
  page: number
  citation: string
  recommendation: string
  match_basis: string
}

type Clause = {
  type: string
  text: string
  page: number
  state: string
}

type Guidance = {
  title: string
  source: string
  text: string
  finding_id: string
}

type Analysis = {
  analysis_id: string
  contract: {
    filename: string
    pages: number
    characters_extracted: number
    analysed_at: string
  }
  summary: {
    tier: string
    determination: string
    determination_detail: string
    riba_count: number
    gharar_count: number
    finding_count: number
    clause_count: number
  }
  findings: Finding[]
  clauses: Clause[]
  guidance: Guidance[]
  graph: ApiKnowledgeGraph
  analysis_method: {
    mode: string
    model: string
    grounding: string
  }
  warnings: string[]
}

type CopilotExplanation = {
  explanation: string
  model: string
  status: string
  disclaimer: string
}

const MAX_FILE_BYTES = 20 * 1024 * 1024

async function responsePayload<T>(response: Response): Promise<T | null> {
  const body = await response.text()
  if (!body.trim()) return null
  try {
    return JSON.parse(body) as T
  } catch {
    return null
  }
}

function responseMessage(payload: unknown, fallback: string) {
  if (typeof payload === 'object' && payload !== null && 'detail' in payload) {
    const detail = (payload as { detail?: unknown }).detail
    if (typeof detail === 'string' && detail.trim()) return detail
  }
  return fallback
}

function CapcoMark() {
  return <div className="capco-mark" aria-label="Capco"><span>CAPCO</span><i aria-hidden="true" /></div>
}

function SeverityMarker({ severity }: { severity: Severity }) {
  const names = { critical: 'Critical', high: 'High', medium: 'Medium' }
  return <span className={`severity severity--${severity}`}>{names[severity]}</span>
}

function formatTime(value: string) {
  const date = new Date(value)
  return Number.isNaN(date.valueOf()) ? 'just now' : date.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
}

function downloadFile(filename: string, contents: string, mimeType: string) {
  const url = URL.createObjectURL(new Blob([contents], { type: mimeType }))
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  URL.revokeObjectURL(url)
}

function reportFor(analysis: Analysis, reviewedFindingIds: Set<string>, reviewRequested: boolean) {
  const findings = analysis.findings.map((finding) => `
<article>
  <h2>${finding.id} · ${finding.title}</h2>
  <p><strong>Classification:</strong> ${finding.type} / ${finding.severity}</p>
  <p><strong>Source:</strong> ${finding.clause}, page ${finding.page}</p>
  <blockquote>${finding.excerpt}</blockquote>
  <p><strong>Candidate reference:</strong> ${finding.citation}</p>
  <p><strong>Recommended next step:</strong> ${finding.recommendation}</p>
  <p><strong>Review state:</strong> ${reviewedFindingIds.has(finding.id) ? 'Reviewed' : 'Pending review'}</p>
</article>`).join('\\n')
  return `<!doctype html><html><head><meta charset="utf-8"><title>Contract review report</title><style>body{font-family:Arial,sans-serif;color:#171717;line-height:1.5;max-width:860px;margin:48px auto;padding:0 24px}h1{font-size:30px}h2{font-size:19px;margin-top:32px;border-top:1px solid #ddd;padding-top:22px}blockquote{margin:18px 0;padding:14px 18px;border-left:3px solid #cf2028;background:#f7f7f4}small{color:#666}</style></head><body><h1>Shariah Compliance Copilot review report</h1><p><strong>Contract:</strong> ${analysis.contract.filename}</p><p><strong>Analysed:</strong> ${formatTime(analysis.contract.analysed_at)}</p><p><strong>Preliminary determination:</strong> ${analysis.summary.determination} · ${analysis.summary.tier}</p><p>${analysis.summary.determination_detail}</p><p><strong>Scholar review:</strong> ${reviewRequested ? 'Requested' : 'Not yet requested'}</p><small>${analysis.warnings.join(' ')}</small>${findings}</body></html>`
}

function App() {
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [activeSurface, setActiveSurface] = useState<Surface>('workspace')
  const [activeTab, setActiveTab] = useState<Tab>('findings')
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [isNavOpen, setIsNavOpen] = useState(false)
  const [reviewRequested, setReviewRequested] = useState(false)
  const [reviewedFindingIds, setReviewedFindingIds] = useState<Set<string>>(() => new Set())
  const [searchTerm, setSearchTerm] = useState('')
  const [guidanceTerm, setGuidanceTerm] = useState('')
  const [graph, setGraph] = useState<KnowledgeGraphResult | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [sourceFinding, setSourceFinding] = useState<Finding | null>(null)
  const [standardsReference, setStandardsReference] = useState<AaoifiReference | null>(null)
  const [showHelp, setShowHelp] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const [explanations, setExplanations] = useState<Record<string, CopilotExplanation>>({})
  const [copilotError, setCopilotError] = useState<string | null>(null)
  const [copilotLoadingId, setCopilotLoadingId] = useState<string | null>(null)
  const uploadInputRef = useRef<HTMLInputElement>(null)
  const findingsSearchRef = useRef<HTMLInputElement>(null)

  const findings = useMemo(() => analysis?.findings ?? [], [analysis])
  const selectedFinding = useMemo(
    () => findings.find((item) => item.id === selectedId) ?? findings[0] ?? null,
    [findings, selectedId],
  )
  const visibleFindings = useMemo(() => {
    const term = searchTerm.trim().toLowerCase()
    return term ? findings.filter((item) => `${item.title} ${item.type} ${item.clause} ${item.excerpt}`.toLowerCase().includes(term)) : findings
  }, [findings, searchTerm])
  const visibleGuidance = useMemo(() => {
    const guidance = analysis?.guidance ?? []
    const term = guidanceTerm.trim().toLowerCase()
    return term ? guidance.filter((item) => `${item.title} ${item.source} ${item.text}`.toLowerCase().includes(term)) : guidance
  }, [analysis?.guidance, guidanceTerm])

  const updateTab = (tab: Tab) => {
    setActiveTab(tab)
    setActiveSurface('workspace')
    setIsNavOpen(false)
  }

  const handleFile = async (file?: File) => {
    if (!file) return
    setUploadError(null)
    if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') {
      setUploadError('Select a PDF contract to begin the review.')
      return
    }
    if (file.size > MAX_FILE_BYTES) {
      setUploadError('This demo accepts PDFs up to 20 MB.')
      return
    }

    setIsUploading(true)
    try {
      const body = new FormData()
      body.append('file', file)
      const response = await fetch('/api/v1/contracts/analyze', { method: 'POST', body })
      const payload = await responsePayload<Analysis | { detail?: string }>(response)
      if (!response.ok || !payload || !('analysis_id' in payload)) {
        throw new Error(responseMessage(payload, 'The contract could not be analysed.'))
      }
      const result = payload
      setAnalysis(result)
      setSelectedId(result.findings[0]?.id ?? null)
      setReviewedFindingIds(new Set())
      setReviewRequested(false)
      setSearchTerm('')
      setGuidanceTerm('')
      setExplanations({})
      setCopilotError(null)
      setActiveSurface('workspace')
      setActiveTab(result.findings.length > 0 ? 'findings' : 'clauses')
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : 'The contract could not be analysed.')
    } finally {
      setIsUploading(false)
      if (uploadInputRef.current) uploadInputRef.current.value = ''
    }
  }

  const handleInput = (event: ChangeEvent<HTMLInputElement>) => void handleFile(event.target.files?.[0])
  const requestReview = () => setReviewRequested(true)
  const toggleReviewed = (findingId: string) => {
    setReviewedFindingIds((current) => {
      const next = new Set(current)
      if (next.has(findingId)) next.delete(findingId)
      else next.add(findingId)
      return next
    })
  }
  const openRelationshipMap = () => {
    if (!analysis?.graph?.nodes?.length) return
    setGraph(normaliseKnowledgeGraph(analysis.graph))
  }
  const askCopilot = async () => {
    if (!selectedFinding || copilotLoadingId) return
    setCopilotError(null)
    setCopilotLoadingId(selectedFinding.id)
    try {
      const response = await fetch('/api/v1/contracts/explain-finding', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: selectedFinding.title,
          finding_type: selectedFinding.type,
          severity: selectedFinding.severity,
          excerpt: selectedFinding.excerpt,
          citation: selectedFinding.citation,
          recommendation: selectedFinding.recommendation,
        }),
      })
      const payload = await responsePayload<CopilotExplanation | { detail?: string }>(response)
      if (!response.ok || !payload || !('explanation' in payload)) {
        throw new Error(responseMessage(payload, 'The copilot could not prepare an explanation.'))
      }
      setExplanations((current) => ({ ...current, [selectedFinding.id]: payload }))
    } catch (error) {
      setCopilotError(error instanceof Error ? error.message : 'The copilot could not prepare an explanation.')
    } finally {
      setCopilotLoadingId(null)
    }
  }
  const exportReport = () => {
    if (!analysis) return
    const baseName = analysis.contract.filename.replace(/\\.pdf$/i, '')
    downloadFile(`${baseName}-review-report.html`, reportFor(analysis, reviewedFindingIds, reviewRequested), 'text/html')
  }
  const downloadClauses = () => {
    if (!analysis) return
    downloadFile(`${analysis.contract.filename.replace(/\\.pdf$/i, '')}-clauses.json`, JSON.stringify(analysis.clauses, null, 2), 'application/json')
  }
  const focusFindingSearch = () => {
    if (!analysis) return
    setActiveSurface('workspace')
    setActiveTab('findings')
    window.setTimeout(() => findingsSearchRef.current?.focus(), 0)
  }

  return <div className="app-shell">
    <header className="topbar">
      <div className="brand-wrap"><CapcoMark /><span className="brand-divider" /><span className="product-name">Shariah Compliance Copilot</span></div>
      <nav className={isNavOpen ? 'topnav topnav--open' : 'topnav'} aria-label="Primary navigation">
        <button className={activeSurface === 'workspace' ? 'nav-link nav-link--active' : 'nav-link'} onClick={() => { setActiveSurface('workspace'); setIsNavOpen(false) }}>Review workspace</button>
        <button className={activeSurface === 'library' ? 'nav-link nav-link--active' : 'nav-link'} onClick={() => { setActiveSurface('library'); setIsNavOpen(false) }}>Guidance library</button>
        <button className={activeSurface === 'insights' ? 'nav-link nav-link--active' : 'nav-link'} onClick={() => { setActiveSurface('insights'); setIsNavOpen(false) }}>Review insights</button>
      </nav>
      <div className="topbar-actions"><button className="icon-button" aria-label="Search contract findings" onClick={focusFindingSearch}><Search size={18} /></button><button className="help-button" onClick={() => setShowHelp(true)}><CircleHelp size={17} /><span>Help</span></button><button className="avatar" aria-label="Open analyst profile" onClick={() => setShowHelp(true)}>FA</button><button className="menu-button" aria-label="Toggle navigation" onClick={() => setIsNavOpen((open) => !open)}>{isNavOpen ? <X /> : <Menu />}</button></div>
    </header>

    {!analysis ? activeSurface === 'workspace' ? <UploadWorkspace
      inputRef={uploadInputRef}
      isUploading={isUploading}
      error={uploadError}
      isDragging={isDragging}
      onChange={handleInput}
      onBrowse={() => uploadInputRef.current?.click()}
      onDragState={setIsDragging}
      onDrop={(file) => void handleFile(file)}
    /> : <PreUploadSurface surface={activeSurface} onUpload={() => setActiveSurface('workspace')} /> : <main>
      <section className="case-header">
        <div className="breadcrumb"><span>Contract review</span><ChevronRight size={15} /><span>{analysis.contract.filename}</span></div>
        <div className="case-heading"><div><div className="contract-label"><FileText size={16} /> {analysis.contract.filename}</div><h1>Decision workspace</h1><p>Analysed {formatTime(analysis.contract.analysed_at)} · {analysis.contract.pages} page{analysis.contract.pages === 1 ? '' : 's'} · AAOIFI review framework</p></div><div className="case-actions"><button className="text-action" onClick={exportReport}><ArrowDownToLine size={17} /> Export report</button><button className={reviewRequested ? 'primary-action primary-action--done' : 'primary-action'} onClick={requestReview}>{reviewRequested ? <Check size={17} /> : <ShieldCheck size={17} />}{reviewRequested ? 'Review requested' : 'Request scholar review'}</button></div></div>
        {reviewRequested && <div className="notice"><Check size={17} /> Scholar review requested. The request and current evidence are included in this review session.</div>}
      </section>

      <section className="assessment-band" aria-label="Analysis summary">
        <div className="decision-block"><div className="eyebrow">Preliminary determination</div><div className="decision-line"><span className={analysis.summary.finding_count > 0 ? 'decision-indicator' : 'decision-indicator decision-indicator--clear'}>{analysis.summary.finding_count > 0 ? <AlertTriangle size={18} /> : <Check size={18} />}</span><strong>{analysis.summary.determination}</strong></div><p>{analysis.summary.determination_detail}</p></div>
        <div className="summary-grid"><div className="summary-item"><strong>{analysis.summary.riba_count}</strong><span>potential riba findings</span></div><div className="summary-item"><strong>{analysis.summary.gharar_count}</strong><span>potential gharar risks</span></div><div className="summary-item"><strong>{analysis.summary.clause_count}</strong><span>provisions extracted</span></div><div className="summary-item"><strong>{analysis.contract.pages}</strong><span>pages analysed</span></div></div>
        <div className="tier-block"><span>Decision tier</span><strong>{analysis.summary.tier}</strong><small>Qualified human decision required</small></div>
      </section>

      <div className="analysis-warnings">{analysis.warnings.map((warning) => <div className="analysis-warning" key={warning}><AlertTriangle size={15} />{warning}</div>)}</div>

      {activeSurface === 'workspace' && <section className="workspace">
        <aside className="analysis-sidebar"><div className="sidebar-heading"><span>Analysis</span><span className="analysis-count">{analysis.summary.finding_count}</span></div><button className={activeTab === 'findings' ? 'sidebar-link sidebar-link--active' : 'sidebar-link'} onClick={() => updateTab('findings')}><AlertTriangle size={18} /> Findings <span>{analysis.summary.finding_count}</span></button><button className={activeTab === 'clauses' ? 'sidebar-link sidebar-link--active' : 'sidebar-link'} onClick={() => updateTab('clauses')}><Layers3 size={18} /> Extracted clauses <span>{analysis.summary.clause_count}</span></button><button className={activeTab === 'guidance' ? 'sidebar-link sidebar-link--active' : 'sidebar-link'} onClick={() => updateTab('guidance')}><BookOpen size={18} /> Related guidance <span>{analysis.guidance.length}</span></button><div className="audit-card"><Clock3 size={18} /><div><strong>Review session active</strong><p>{reviewRequested ? 'Scholar review has been requested.' : `${reviewedFindingIds.size} finding${reviewedFindingIds.size === 1 ? '' : 's'} marked reviewed.`}</p></div></div></aside>
        <div className="content-area">
          {activeTab === 'findings' && <FindingsView
            findings={visibleFindings}
            selectedFinding={selectedFinding}
            selectedId={selectedId}
            searchTerm={searchTerm}
            searchRef={findingsSearchRef}
            reviewedFindingIds={reviewedFindingIds}
            onSearch={setSearchTerm}
            onSelect={setSelectedId}
            onSource={setSourceFinding}
            onOpenReference={setStandardsReference}
            onToggleReviewed={toggleReviewed}
            onGraph={() => void openRelationshipMap()}
            explanation={selectedFinding ? explanations[selectedFinding.id] : undefined}
            copilotError={copilotError}
            isCopilotLoading={copilotLoadingId === selectedFinding?.id}
            onAskCopilot={() => void askCopilot()}
          />}
          {activeTab === 'clauses' && <ClausesView clauses={analysis.clauses} onDownload={downloadClauses} />}
          {activeTab === 'guidance' && <GuidanceView guidance={analysis.guidance} onSelectFinding={(id) => { setSelectedId(id); setActiveTab('findings') }} />}
        </div>
      </section>}

      {activeSurface === 'library' && <LibraryView guidance={visibleGuidance} searchTerm={guidanceTerm} onSearch={setGuidanceTerm} onOpen={(id) => { setSelectedId(id); setActiveSurface('workspace'); setActiveTab('guidance') }} />}
      {activeSurface === 'insights' && <InsightsView analysis={analysis} reviewedFindingIds={reviewedFindingIds} reviewRequested={reviewRequested} onReturn={() => setActiveSurface('workspace')} />}
    </main>}

    <footer className="app-footer"><span>Shariah Compliance Copilot · Capco demonstration</span><span>AI assists analysis. Qualified scholars retain final authority.</span></footer>
    {sourceFinding && analysis && <SourceDialog
      finding={sourceFinding}
      analysisId={analysis.analysis_id}
      explanation={explanations[sourceFinding.id]}
      onClose={() => setSourceFinding(null)}
      onOpenReference={setStandardsReference}
    />}
    {standardsReference && <StandardsDialog reference={standardsReference} onClose={() => setStandardsReference(null)} />}
    {showHelp && <HelpDialog onClose={() => setShowHelp(false)} />}
    {graph && <KnowledgeGraphExplorer analysisId={analysis?.analysis_id} graph={graph} isLoading={false} onClose={() => setGraph(null)} />}
  </div>
}

function UploadWorkspace({ inputRef, isUploading, error, isDragging, onChange, onBrowse, onDragState, onDrop }: {
  inputRef: RefObject<HTMLInputElement | null>
  isUploading: boolean
  error: string | null
  isDragging: boolean
  onChange: (event: ChangeEvent<HTMLInputElement>) => void
  onBrowse: () => void
  onDragState: (value: boolean) => void
  onDrop: (file?: File) => void
}) {
  return <main className="upload-page"><section className="upload-intro"><div className="eyebrow">Contract review</div><h1>Review a contract with traceable evidence.</h1><p>Upload a text-based PDF. The semantic copilot extracts provisions, identifies source-grounded review candidates, and prepares a qualified-review workspace.</p><div className="upload-steps"><span><b>1</b> Upload contract</span><span><b>2</b> Review evidence</span><span><b>3</b> Request scholar review</span></div></section><section className="upload-card"><FileSearch size={28} /><h2>Upload a contract PDF</h2><p>PDF only · up to 20 MB · text-based documents</p><input ref={inputRef} className="visually-hidden" type="file" accept="application/pdf,.pdf" onChange={onChange} />
    <div className={isDragging ? 'drop-zone drop-zone--active' : 'drop-zone'} onDragOver={(event) => { event.preventDefault(); onDragState(true) }} onDragLeave={() => onDragState(false)} onDrop={(event) => { event.preventDefault(); onDragState(false); onDrop(event.dataTransfer.files[0]) }}><Upload size={22} /><strong>{isUploading ? 'Reading contract…' : 'Drop a PDF here'}</strong><span>{isUploading ? 'Extracting text and preparing review evidence.' : 'or choose a file from your computer'}</span><button className="primary-action" type="button" onClick={onBrowse} disabled={isUploading}>{isUploading ? 'Analysing contract' : 'Choose PDF'}</button></div>
    {error && <div className="upload-error"><AlertTriangle size={17} />{error}</div>}<div className="upload-boundary"><ShieldCheck size={17} /><span>Semantic inferences are preliminary. The demo does not issue a Shari’ah ruling or publish AAOIFI source text.</span></div></section></main>
}

function PreUploadSurface({ surface, onUpload }: { surface: Exclude<Surface, 'workspace'>; onUpload: () => void }) {
  const isLibrary = surface === 'library'
  return <main className="pre-upload-page"><section><span className="eyebrow">{isLibrary ? 'Candidate guidance' : 'Review session'}</span><h1>{isLibrary ? 'Guidance library' : 'Review insights'}</h1><p>{isLibrary ? 'Candidate guidance is assembled from the language detected in the contract you upload.' : 'The insight view will track evidence review and scholar handoff for the uploaded contract.'}</p><button className="primary-action" onClick={onUpload}>Upload a contract <ArrowRight size={17} /></button></section><aside><BookOpen size={25} /><strong>{isLibrary ? 'No contract in review' : 'No review session yet'}</strong><span>Upload a PDF to populate this area with live information from the current review.</span></aside></main>
}

function FindingsView({ findings, selectedFinding, selectedId, searchTerm, searchRef, reviewedFindingIds, onSearch, onSelect, onSource, onOpenReference, onToggleReviewed, onGraph, explanation, copilotError, isCopilotLoading, onAskCopilot }: {
  findings: Finding[]
  selectedFinding: Finding | null
  selectedId: string | null
  searchTerm: string
  searchRef: RefObject<HTMLInputElement | null>
  reviewedFindingIds: Set<string>
  onSearch: (value: string) => void
  onSelect: (id: string) => void
  onSource: (finding: Finding) => void
  onOpenReference: (reference: AaoifiReference) => void
  onToggleReviewed: (id: string) => void
  onGraph: () => void
  explanation?: CopilotExplanation
  copilotError: string | null
  isCopilotLoading: boolean
  onAskCopilot: () => void
}) {
  return <section className="findings-view"><div className="view-heading"><div><span className="eyebrow">Flagged for review</span><h2>Findings and evidence</h2></div><label className="search-field"><Search size={17} /><input ref={searchRef} value={searchTerm} onChange={(event) => onSearch(event.target.value)} placeholder="Search findings" /></label></div><div className="review-layout"><div className="finding-list" aria-label="Finding list">{findings.map((finding) => <button key={finding.id} className={selectedId === finding.id ? 'finding-row finding-row--selected' : 'finding-row'} onClick={() => onSelect(finding.id)}><span className={`finding-symbol finding-symbol--${finding.severity}`}>{finding.type === 'Riba' ? 'R' : 'G'}</span><span className="finding-copy"><span className="finding-topline"><SeverityMarker severity={finding.severity} /><span>{finding.id}{reviewedFindingIds.has(finding.id) ? ' · Reviewed' : ''}</span></span><strong>{finding.title}</strong><small>{finding.clause}</small></span><ChevronRight size={17} /></button>)}{findings.length === 0 && <div className="empty-state"><Check size={22} /><strong>No potential issues inferred</strong><span>{searchTerm ? `No findings match “${searchTerm}”.` : 'Review the extracted provisions or upload another contract.'}</span></div>}</div>{selectedFinding ? <article className="evidence-panel"><div className="evidence-meta"><SeverityMarker severity={selectedFinding.severity} /><span>{selectedFinding.id}</span><span className="confidence">Semantic inference · source grounded</span></div><h3>{selectedFinding.title}</h3><div className="source-ref"><FileText size={16} /> {selectedFinding.clause} · Page {selectedFinding.page}</div><blockquote>{selectedFinding.excerpt}</blockquote><div className="evidence-section"><span>Candidate AAOIFI mapping</span><AaoifiReferenceList citation={selectedFinding.citation} onOpen={onOpenReference} /></div><div className="evidence-section"><span>Inference basis</span><p>{selectedFinding.match_basis}</p></div><div className="evidence-section evidence-section--recommendation"><span>Recommended next step</span><p>{selectedFinding.recommendation}</p></div><div className="copilot-section"><div className="copilot-section__heading"><div><span className="eyebrow"><Sparkles size={13} /> Copilot explanation</span><p>Explain this source-grounded semantic inference using the selected contract evidence.</p></div><button className="secondary-action copilot-action" onClick={onAskCopilot} disabled={isCopilotLoading}>{isCopilotLoading ? 'Preparing…' : explanation ? 'Refresh explanation' : 'Ask copilot'}</button></div>{explanation && <div className="copilot-answer"><p>{explanation.explanation}</p><small>{explanation.model} · {explanation.disclaimer}</small></div>}{copilotError && <div className="copilot-error"><AlertTriangle size={15} />{copilotError}</div>}</div><div className="evidence-footer"><button className="secondary-action" onClick={() => onSource(selectedFinding)}>View source clause</button><button className="graph-action" onClick={onGraph}><Network size={16} /> Explore relationship map</button><button className={reviewedFindingIds.has(selectedFinding.id) ? 'link-action link-action--done' : 'link-action'} onClick={() => onToggleReviewed(selectedFinding.id)}>{reviewedFindingIds.has(selectedFinding.id) ? <Check size={16} /> : null}{reviewedFindingIds.has(selectedFinding.id) ? 'Reviewed' : 'Mark reviewed'} <ChevronDown size={16} /></button></div></article> : <article className="evidence-panel evidence-panel--empty"><FileText size={28} /><h3>Select an extracted provision</h3><p>The evidence panel will show source wording and the appropriate review next step.</p></article>}</div></section>
}

function ClausesView({ clauses, onDownload }: { clauses: Clause[]; onDownload: () => void }) {
  return <section className="table-view"><div className="view-heading"><div><span className="eyebrow">Structured extraction</span><h2>Contract clauses</h2></div><button className="text-action" onClick={onDownload}><ArrowDownToLine size={17} /> Download JSON</button></div><div className="clause-table"><div className="table-row table-row--header"><span>Clause type</span><span>Extracted provision</span><span>Source</span><span>Review state</span></div>{clauses.map((clause, index) => <div className="table-row" key={`${clause.page}-${index}`}><strong>{clause.type}</strong><span>{clause.text}</span><span>Page {clause.page}</span><span className={clause.state === 'Potential issue' ? 'state state--risk' : 'state'}>{clause.state}</span></div>)}{clauses.length === 0 && <div className="empty-state"><FileText size={22} /><strong>No provisions extracted</strong><span>The uploaded document did not provide readable sentence-level text.</span></div>}</div></section>
}

function GuidanceView({ guidance, onSelectFinding }: { guidance: Guidance[]; onSelectFinding: (id: string) => void }) {
  return <section className="fatwa-view"><div className="view-heading"><div><span className="eyebrow">Contextual research</span><h2>Related guidance</h2></div></div><p className="fatwa-intro">Candidate mappings are assembled from the detected language. A qualified scholar confirms their applicability and any authoritative source text.</p><GuidanceCards guidance={guidance} onOpen={onSelectFinding} /></section>
}

function LibraryView({ guidance, searchTerm, onSearch, onOpen }: { guidance: Guidance[]; searchTerm: string; onSearch: (value: string) => void; onOpen: (id: string) => void }) {
  return <section className="surface-page"><div className="view-heading"><div><span className="eyebrow">Current contract context</span><h1>Guidance library</h1><p>Browse the candidate guidance assembled from this contract’s detected language.</p></div><label className="search-field"><Search size={17} /><input value={searchTerm} onChange={(event) => onSearch(event.target.value)} placeholder="Search guidance" /></label></div><GuidanceCards guidance={guidance} onOpen={onOpen} /></section>
}

function GuidanceCards({ guidance, onOpen }: { guidance: Guidance[]; onOpen: (id: string) => void }) {
  return <div className="fatwa-list">{guidance.map((item) => <article className="fatwa-card" key={`${item.finding_id}-${item.title}`}><div><BookOpen size={20} /><span>{item.source}</span></div><h3>{item.title}</h3><p>{item.text}</p><footer><span>Candidate mapping</span><button className="link-action" onClick={() => onOpen(item.finding_id)}>Open finding <ArrowRight size={16} /></button></footer></article>)}{guidance.length === 0 && <div className="empty-state empty-state--wide"><BookOpen size={22} /><strong>No guidance cards available</strong><span>Upload a contract with detected language to assemble candidate review guidance.</span></div>}</div>
}

function InsightsView({ analysis, reviewedFindingIds, reviewRequested, onReturn }: { analysis: Analysis; reviewedFindingIds: Set<string>; reviewRequested: boolean; onReturn: () => void }) {
  const counts = [
    ['Findings detected', analysis.summary.finding_count],
    ['Findings reviewed', reviewedFindingIds.size],
    ['Provisions extracted', analysis.summary.clause_count],
    ['Scholar review', reviewRequested ? 'Requested' : 'Pending'],
  ]
  return <section className="surface-page"><div className="view-heading"><div><span className="eyebrow">Current review session</span><h1>Review insights</h1><p>A live status view for the uploaded contract. Metrics are calculated from this review only.</p></div><button className="primary-action" onClick={onReturn}>Return to workspace <ArrowRight size={17} /></button></div><div className="insights-grid">{counts.map(([label, value]) => <div className="insight-card" key={label}><span>{label}</span><strong>{value}</strong></div>)}</div><div className="insights-note"><ShieldCheck size={19} /><p>Evidence remains reviewable alongside the original contract language. The system retains a preliminary assessment; it does not make an autonomous determination.</p></div></section>
}

function SourceDialog({ finding, analysisId, explanation, onClose, onOpenReference }: {
  finding: Finding
  analysisId: string
  explanation?: CopilotExplanation
  onClose: () => void
  onOpenReference: (reference: AaoifiReference) => void
}) {
  const pdfUrl = `/api/v1/contracts/${analysisId}/source.pdf`
  const previewUrl = `${pdfUrl}#page=${finding.page}&zoom=page-width`
  return <div className="dialog-overlay" role="presentation"><section className="dialog dialog--source" role="dialog" aria-modal="true" aria-labelledby="source-dialog-title"><header><div><span className="eyebrow">Reviewed document</span><h2 id="source-dialog-title">{finding.clause}</h2></div><button className="graph-close" onClick={onClose} aria-label="Close reviewed document"><X size={20} /></button></header><div className="dialog-body source-dialog-body"><section className="source-preview"><div className="source-preview__heading"><div><span className="source-page">Original uploaded PDF · Page {finding.page}</span><strong>Contract preview</strong></div><a className="text-action" href={previewUrl} target="_blank" rel="noreferrer">Open full page <ArrowRight size={16} /></a></div><PdfHighlightPreview url={pdfUrl} pageNumber={finding.page} excerpt={finding.excerpt} /></section><section className="source-evidence"><span className="eyebrow">Highlighted evidence</span><blockquote>{finding.excerpt}</blockquote><div className="source-explanation"><span>Shari’ah review explanation</span><p>{explanation?.explanation ?? finding.match_basis}</p><small>{explanation ? explanation.disclaimer : 'This preliminary explanation is grounded in the highlighted contract wording and must be confirmed by a qualified scholar.'}</small></div><div className="source-candidate"><span>Candidate AAOIFI mapping</span><AaoifiReferenceList citation={finding.citation} onOpen={onOpenReference} /><p>{finding.recommendation}</p></div></section></div><footer><button className="primary-action" onClick={onClose}>Return to evidence</button></footer></section></div>
}

function HelpDialog({ onClose }: { onClose: () => void }) {
  return <div className="dialog-overlay" role="presentation"><section className="dialog" role="dialog" aria-modal="true" aria-labelledby="help-dialog-title"><header><div><span className="eyebrow">How this demo works</span><h2 id="help-dialog-title">Review workflow</h2></div><button className="graph-close" onClick={onClose} aria-label="Close help"><X size={20} /></button></header><div className="dialog-body help-body"><ol><li>Upload a text-based PDF contract of up to 20 MB.</li><li>The semantic copilot extracts readable provisions and infers candidate review issues from their meaning.</li><li>Inspect each evidence item, mark it reviewed, and request scholar review when ready.</li><li>Use the relationship map to inspect source-grounded contract relationships or run its bounded Cypher-compatible query.</li></ol><p>Candidate AAOIFI references are illustrative mappings pending authorized corpus use and scholar review.</p></div><footer><button className="primary-action" onClick={onClose}>Continue review</button></footer></section></div>
}

export default App
