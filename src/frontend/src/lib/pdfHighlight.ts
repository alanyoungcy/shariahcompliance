export type HighlightBox = {
  left: number
  top: number
  width: number
  height: number
}

export type PdfPageBox = {
  pageWidth: number
  pageHeight: number
  pageX: number
  pageY: number
}

type PdfGlyph = {
  str: string
  transform: number[]
  width: number
  height: number
  hasEOL: boolean
}

type PlacedGlyph = {
  text: string
  start: number
  left: number
  top: number
  width: number
  height: number
}

function isGlyph(item: object): item is PdfGlyph {
  if (!('str' in item) || typeof item.str !== 'string' || item.str.length === 0) return false
  if (!('transform' in item) || !Array.isArray(item.transform) || item.transform.length < 6) return false
  if (!('width' in item) || typeof item.width !== 'number') return false
  const height = 'height' in item && typeof item.height === 'number' ? item.height : 0
  return Number.isFinite(item.width) && Number.isFinite(height)
}

function multiply(m1: number[], m2: number[]) {
  return [
    m1[0] * m2[0] + m1[2] * m2[1],
    m1[1] * m2[0] + m1[3] * m2[1],
    m1[0] * m2[2] + m1[2] * m2[3],
    m1[1] * m2[2] + m1[3] * m2[3],
    m1[0] * m2[4] + m1[2] * m2[5] + m1[4],
    m1[1] * m2[4] + m1[3] * m2[5] + m1[5],
  ]
}

function foldChar(char: string) {
  if (char === '\u00ad') return null
  if (/\s/u.test(char)) return ' '
  const lower = char.toLowerCase()
  if (lower === '\u201c' || lower === '\u201d' || lower === '\u201e') return '"'
  if (lower === '\u2018' || lower === '\u2019' || lower === '\u201a' || lower === '\u02bc') return "'"
  return lower
}

function fold(value: string) {
  let text = ''
  const map: number[] = []
  let previousSpace = true
  for (let index = 0; index < value.length; index += 1) {
    const next = foldChar(value[index] ?? '')
    if (!next) continue
    if (next === ' ') {
      if (previousSpace) continue
      previousSpace = true
    } else {
      previousSpace = false
    }
    text += next
    map.push(index)
  }
  while (text.endsWith(' ')) {
    text = text.slice(0, -1)
    map.pop()
  }
  return { text, map }
}

function compact(value: string) {
  let text = ''
  const map: number[] = []
  for (let index = 0; index < value.length; index += 1) {
    const folded = foldChar(value[index] ?? '')
    if (!folded || !/[a-z0-9]/i.test(folded)) continue
    text += folded
    map.push(index)
  }
  return { text, map }
}

function matchRange(source: string, excerpt: string) {
  const needle = fold(excerpt)
  if (!needle.text) return null
  const folded = fold(source)
  const found = folded.text.indexOf(needle.text)
  if (found >= 0) {
    const end = folded.map[found + needle.text.length - 1]
    const start = folded.map[found]
    if (start === undefined || end === undefined) return null
    return [start, end + 1] as const
  }
  const compactNeedle = compact(excerpt).text
  if (compactNeedle.length < 12) return null
  const compactSource = compact(source)
  const compactFound = compactSource.text.indexOf(compactNeedle)
  if (compactFound < 0) return null
  const end = compactSource.map[compactFound + compactNeedle.length - 1]
  const start = compactSource.map[compactFound]
  if (start === undefined || end === undefined) return null
  return [start, end + 1] as const
}

function mergeLines(rects: HighlightBox[]) {
  const merged: HighlightBox[] = []
  for (const rect of rects) {
    const current = merged.at(-1)
    if (!current) {
      merged.push({ ...rect })
      continue
    }
    const sameLine = Math.abs(current.top - rect.top) < Math.max(current.height, rect.height) * 0.6
    const gap = rect.left - (current.left + current.width)
    const bridge = Math.max(current.height, rect.height) * 1.4
    if (sameLine && gap <= bridge && gap > -rect.width) {
      const right = Math.max(current.left + current.width, rect.left + rect.width)
      const bottom = Math.max(current.top + current.height, rect.top + rect.height)
      current.left = Math.min(current.left, rect.left)
      current.top = Math.min(current.top, rect.top)
      current.width = right - current.left
      current.height = bottom - current.top
      continue
    }
    merged.push({ ...rect })
  }
  return merged
}

export function highlightExcerpt(items: readonly object[], page: PdfPageBox, excerpt: string): HighlightBox[] {
  if (page.pageWidth <= 0 || page.pageHeight <= 0 || !excerpt.trim()) return []
  const flip = [1, 0, 0, -1, -page.pageX, page.pageY + page.pageHeight]
  let source = ''
  const glyphs: PlacedGlyph[] = []
  for (const item of items) {
    if (!isGlyph(item)) continue
    const placed = multiply(flip, item.transform)
    const fontHeight = Math.hypot(placed[2] ?? 0, placed[3] ?? 0) || item.height
    const start = source.length
    source += item.str
    if (item.str.trim() && fontHeight > 0) {
      const width = item.width > 0 ? item.width : fontHeight * 0.45 * item.str.length
      const ascent = fontHeight * 0.8
      glyphs.push({
        text: item.str,
        start,
        left: placed[4] ?? 0,
        top: (placed[5] ?? 0) - ascent,
        width,
        height: ascent + fontHeight * 0.18,
      })
    }
    if (item.hasEOL) source += '\n'
  }

  const range = matchRange(source, excerpt)
  if (!range) return []
  const [rangeStart, rangeEnd] = range
  const slices: HighlightBox[] = []
  for (const glyph of glyphs) {
    const glyphEnd = glyph.start + glyph.text.length
    const from = Math.max(rangeStart, glyph.start)
    const to = Math.min(rangeEnd, glyphEnd)
    if (to <= from) continue
    const slice = glyph.text.slice(from - glyph.start, to - glyph.start)
    if (!slice.trim()) continue
    const share = (to - from) / glyph.text.length
    const offset = (from - glyph.start) / glyph.text.length
    slices.push({
      left: glyph.left + glyph.width * offset,
      top: glyph.top,
      width: glyph.width * share,
      height: glyph.height,
    })
  }

  return mergeLines(slices).map((rect) => {
    const padX = 1.2
    const padY = rect.height * 0.04
    const left = Math.max(0, rect.left - padX)
    const top = Math.max(0, rect.top - padY)
    const right = Math.min(page.pageWidth, rect.left + rect.width + padX)
    const bottom = Math.min(page.pageHeight, rect.top + rect.height + padY)
    return {
      left: (left / page.pageWidth) * 100,
      top: (top / page.pageHeight) * 100,
      width: ((right - left) / page.pageWidth) * 100,
      height: ((bottom - top) / page.pageHeight) * 100,
    }
  })
}
