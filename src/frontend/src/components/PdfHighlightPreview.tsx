import { useEffect, useRef, useState } from 'react'
import { getDocument, GlobalWorkerOptions } from 'pdfjs-dist'
import pdfWorkerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url'
import { highlightExcerpt, type HighlightBox } from '../lib/pdfHighlight'

GlobalWorkerOptions.workerSrc = pdfWorkerUrl

type Props = {
  url: string
  pageNumber: number
  excerpt?: string
}

type Status = 'loading' | 'ready' | 'missing' | 'error'

function isIgnorable(error: unknown) {
  return error instanceof Error && (error.name === 'RenderingCancelledException' || error.name === 'AbortException')
}

export function PdfHighlightPreview({ url, pageNumber, excerpt }: Props) {
  const frameRef = useRef<HTMLDivElement>(null)
  const pageRef = useRef<HTMLDivElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [boxes, setBoxes] = useState<HighlightBox[]>([])
  const [status, setStatus] = useState<Status>('loading')

  useEffect(() => {
    const frame = frameRef.current
    const canvas = canvasRef.current
    if (!frame || !canvas) return

    let cancelled = false
    let currentRender: { cancel: () => void; promise: Promise<unknown> } | null = null
    const loadingTask = getDocument({ url })
    setBoxes([])
    setStatus('loading')

    const paint = async (width: number) => {
      const pdf = await loadingTask.promise
      if (cancelled) return
      const safePage = Math.min(Math.max(pageNumber, 1), pdf.numPages)
      const page = await pdf.getPage(safePage)
      if (cancelled) return
      if (currentRender) {
        const previous = currentRender
        currentRender = null
        previous.cancel()
        try {
          await previous.promise
        } catch (error) {
          if (!isIgnorable(error) && !cancelled) throw error
        }
      }
      if (cancelled) return
      const base = page.getViewport({ scale: 1 })
      const viewport = page.getViewport({ scale: width / base.width })
      const outputScale = window.devicePixelRatio || 1
      canvas.width = Math.floor(viewport.width * outputScale)
      canvas.height = Math.floor(viewport.height * outputScale)
      const context = canvas.getContext('2d', { alpha: false })
      if (!context) return
      const task = page.render({
        canvas,
        viewport,
        transform: outputScale === 1 ? undefined : [outputScale, 0, 0, outputScale, 0, 0],
      })
      currentRender = task
      await task.promise
      if (currentRender === task) currentRender = null
      if (cancelled) return
      const text = await page.getTextContent()
      if (cancelled) return
      const [xMin = 0, yMin = 0, xMax = 0, yMax = 0] = viewport.viewBox
      const needle = excerpt?.trim() ?? ''
      const nextBoxes = needle ? highlightExcerpt(text.items, {
        pageWidth: xMax - xMin,
        pageHeight: yMax - yMin,
        pageX: xMin,
        pageY: yMin,
      }, needle) : []
      setBoxes(nextBoxes)
      setStatus(needle && nextBoxes.length === 0 ? 'missing' : 'ready')
    }

    let lastWidth = 0
    let painting = false
    let queuedWidth = 0
    const schedule = (width: number) => {
      if (!width) return
      queuedWidth = width
      if (painting) return
      painting = true
      const run = async () => {
        try {
          while (!cancelled && queuedWidth !== lastWidth) {
            const nextWidth = queuedWidth
            lastWidth = nextWidth
            await paint(nextWidth)
          }
        } catch (error) {
          if (!cancelled && !isIgnorable(error)) setStatus('error')
        } finally {
          painting = false
          if (!cancelled && queuedWidth !== lastWidth) schedule(queuedWidth)
        }
      }
      void run()
    }

    const observer = new ResizeObserver(() => schedule(Math.floor(frame.clientWidth)))
    observer.observe(frame)
    schedule(Math.floor(frame.clientWidth))

    return () => {
      cancelled = true
      currentRender?.cancel()
      observer.disconnect()
      void loadingTask.destroy()
    }
  }, [excerpt, pageNumber, url])

  useEffect(() => {
    const frame = frameRef.current
    const page = pageRef.current
    if (!frame || !page || boxes.length === 0) return
    const top = (Math.min(...boxes.map((box) => box.top)) / 100) * page.offsetHeight
    const bottom = (Math.max(...boxes.map((box) => box.top + box.height)) / 100) * page.offsetHeight
    frame.scrollTo({ top: Math.max(0, top - (frame.clientHeight - (bottom - top)) / 2) })
  }, [boxes])

  const statusText = status === 'loading'
    ? 'Preparing the page…'
    : status === 'missing'
      ? 'The sentence could not be marked on this page.'
      : status === 'error'
        ? 'The page could not be drawn.'
        : ''

  return (
    <div className="pdf-preview" ref={frameRef} role="region" aria-label={excerpt?.trim() ? `Contract page ${pageNumber} with the evidence sentence highlighted` : `Document page ${pageNumber}`}>
      <div className="pdf-page" ref={pageRef} data-pending={status === 'loading' ? '' : undefined}>
        <canvas ref={canvasRef} />
        <div className="pdf-highlight-layer" aria-hidden="true">
          {boxes.map((box, index) => (
            <span
              className="pdf-highlight"
              key={`${box.left}-${box.top}-${index}`}
              style={{ left: `${box.left}%`, top: `${box.top}%`, width: `${box.width}%`, height: `${box.height}%` }}
            />
          ))}
        </div>
      </div>
      {statusText && <p className="pdf-preview__status" role="status">{statusText}</p>}
    </div>
  )
}
