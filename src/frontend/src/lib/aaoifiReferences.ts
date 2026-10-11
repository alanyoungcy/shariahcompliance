export type AaoifiReference = {
  standardNumber: string
  title: string
  pdfPage: number
  printedPage: number
}

const REFERENCE = /^Candidate AAOIFI SS (\d+)\s+page:(\d+)\s+·\s+(.+?)\s+·\s+printed p\.\s+(\d+)$/

export function parseAaoifiReferences(citation: string): AaoifiReference[] {
  return citation.split(';').flatMap((part) => {
    const match = REFERENCE.exec(part.trim())
    if (!match) return []
    return [{
      standardNumber: match[1] ?? '',
      pdfPage: Number(match[2]),
      title: match[3] ?? '',
      printedPage: Number(match[4]),
    }]
  }).filter((reference) => reference.standardNumber && reference.title && reference.pdfPage > 0)
}
