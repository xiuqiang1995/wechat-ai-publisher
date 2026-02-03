const fs = require('node:fs/promises')
const path = require('node:path')
const juice = require('juice')
const MarkdownIt = require('markdown-it')

function parseArgs(argv) {
  const out = {}
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i]
    if (!k.startsWith(`--`)) continue
    const key = k.slice(2)
    const v = argv[i + 1]
    if (v && !v.startsWith(`--`)) {
      out[key] = v
      i++
    }
    else {
      out[key] = true
    }
  }
  return out
}

function preprocessMarkdown(md) {
  const lines = md.split(/\r?\n/)
  const out = []
  for (const line of lines) {
    const s = line.trim()
    // 封面不进入正文
    if (s === `![](cover.png)` || s === `![cover](cover.png)`) continue

    // ![](imgN.png) / ![alt](imgN.png) -> 占位符
    const m = s.match(/^!\[([^\]]*)\]\((img(\d+)\.png)\)$/)
    if (m) {
      const alt = (m[1] || ``).trim()
      const n = m[3]
      const altAttr = alt ? ` alt="${alt.replaceAll(`"`, ``)}"` : ``
      out.push(``)
      out.push(`<img src="__WECHAT_IMG_${n}__"${altAttr} />`)
      out.push(``)
      continue
    }

    out.push(line)
  }
  return out.join(`\n`)
}

function replaceVars(css, { primaryColor, fontSize, fontFamily }) {
  let out = css
  out = out.replaceAll(`var(--md-primary-color)`, primaryColor)
  out = out.replaceAll(`var(--md-font-size)`, fontSize)
  out = out.replaceAll(`var(--md-font-family)`, fontFamily)
  out = out.replaceAll(`hsl(var(--foreground))`, `#3f3f3f`)
  out = out.replaceAll(`var(--blockquote-background)`, `#f7f7f7`)
  return out
}

async function main() {
  const args = parseArgs(process.argv)
  const articleMd = args['article-md']
  const theme = args.theme || `default`
  const primaryColor = args['primary-color'] || `#8064a9`

  if (!articleMd) {
    console.error(`缺少参数: --article-md`)
    process.exit(2)
  }

  const scriptDir = path.dirname(__filename)
  const skillRoot = path.resolve(scriptDir, `..`)
  const cssDir = path.join(skillRoot, `references`, `doocs-theme-css`)

  const baseCssPath = path.join(cssDir, `base.css`)
  const themeCssPath = path.join(cssDir, `${theme}.css`)

  const [baseCssRaw, themeCssRaw, mdRaw] = await Promise.all([
    fs.readFile(baseCssPath, `utf8`),
    fs.readFile(themeCssPath, `utf8`),
    fs.readFile(articleMd, `utf8`),
  ])

  const md = preprocessMarkdown(mdRaw)
  const mdIt = new MarkdownIt({ breaks: true, html: true, linkify: true })
  const bodyHtml = mdIt.render(md)

  const css = replaceVars(`${baseCssRaw}\n\n${themeCssRaw}`, {
    primaryColor,
    fontSize: `15px`,
    fontFamily: `-apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif`,
  })

  const html = `<section id="output"><section>${bodyHtml}</section></section>`
  const inlined = juice(`<style>${css}</style>${html}`, {
    inlinePseudoElements: true,
    preserveImportant: true,
    resolveCSSVariables: false,
  })

  // 与 doocs/web 的处理保持一致：top -> transform（避免部分环境样式异常）
  const fixed = inlined.replace(/([^-])top:(.*?)em/g, `$1transform: translateY($2em)`)
  process.stdout.write(fixed)
}

main().catch((err) => {
  console.error(String(err?.stack || err))
  process.exit(1)
})
