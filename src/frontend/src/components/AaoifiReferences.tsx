import { ArrowRight, X } from 'lucide-react'
import { parseAaoifiReferences, type AaoifiReference } from '../lib/aaoifiReferences'
import { PdfHighlightPreview } from './PdfHighlightPreview'

export function AaoifiReferenceList({ citation, onOpen }: {
  citation: string
  onOpen: (reference: AaoifiReference) => void
}) {
  const references = parseAaoifiReferences(citation)
  if (references.length === 0) return <p>{citation}</p>
  return (
    <ul className="aaoifi-references">
      {references.map((reference) => (
        <li key={`${reference.standardNumber}-${reference.pdfPage}`}>
          <button type="button" className="aaoifi-reference" onClick={() => onOpen(reference)}>
            <strong>SS {reference.standardNumber} · {reference.title}</strong>
            <small>Printed p. {reference.printedPage}</small>
            <span>Open source page <ArrowRight size={14} /></span>
          </button>
        </li>
      ))}
    </ul>
  )
}

export function StandardsDialog({ reference, onClose }: {
  reference: AaoifiReference
  onClose: () => void
}) {
  const pdfUrl = '/api/v1/standards/source.pdf'
  const previewUrl = `${pdfUrl}#page=${reference.pdfPage}`
  return (
    <div className="dialog-overlay dialog-overlay--standards" role="presentation">
      <section className="dialog dialog--source" role="dialog" aria-modal="true" aria-labelledby="standards-dialog-title">
        <header>
          <div>
            <span className="eyebrow">AAOIFI draft compilation</span>
            <h2 id="standards-dialog-title">SS {reference.standardNumber} · {reference.title}</h2>
          </div>
          <button className="graph-close" onClick={onClose} aria-label="Close standard"><X size={20} /></button>
        </header>
        <div className="dialog-body source-dialog-body source-dialog-body--single">
          <section className="source-preview">
            <div className="source-preview__heading">
              <div>
                <span className="source-page">Source PDF · page {reference.pdfPage}</span>
                <strong>Printed page {reference.printedPage}</strong>
              </div>
              <a className="text-action" href={previewUrl} target="_blank" rel="noreferrer">Open full page <ArrowRight size={16} /></a>
            </div>
            <PdfHighlightPreview url={pdfUrl} pageNumber={reference.pdfPage} />
            <p className="standards-note">This opens the supplied English compilation at the mapped source page. A qualified scholar confirms whether the mapping applies.</p>
          </section>
        </div>
        <footer><button className="primary-action" onClick={onClose}>Return to evidence</button></footer>
      </section>
    </div>
  )
}
