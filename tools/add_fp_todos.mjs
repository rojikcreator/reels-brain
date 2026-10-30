// tools/add_fp_todos.mjs
// Jednorazovo zapíše FirstPrinciple to-do (NDA, BNI, INR, FIG) do CRM
// checklistu "Moje úlohy" (owner_todos). Duplicitu stráži názov: úloha, ktorá
// už v checkliste je a nie je odškrtnutá, sa nepridá druhýkrát.
//
// Spúšťa sa z priečinka crm-ops (kvôli balíčku pg):
//   cd C:\Users\jakub\crm-ops
//   node scripts\add_fp_todos.mjs
import { readFileSync } from 'node:fs'
import { Client } from 'pg'

const TODOS = [
  // dnes, pi 30. 10.
  ['NDA FP: podpísať a poslať Jakubovi', '2026-10-30'],
  ['FIG: dokončiť otázky na CIA cally', '2026-10-30'],
  ['FIG: obvolať zákazníkov, CIA cally na 2.–6. 11. (nie 3. 11.)', '2026-10-30'],
  ['INR: prejsť SOPčka Profile Funnel a poslať otázky Filipovi na Slack', '2026-10-30'],
  // do ne 1. 11. 19:00
  ['BNI: content research IG + FB, 10+ príkladov (link + 1 veta prečo funguje)', '2026-11-01'],
  ['BNI: analýza 10+ personal brandov, ženy po 40 (link + 1 veta)', '2026-11-01'],
  ['BNI: avatar research z CIA callov (začínajúci + zaseknutý podnikateľ)', '2026-11-01'],
  ['BNI: positioning, piliere obsahu a formáty (IG, FB)', '2026-11-01'],
  ['BNI: USP doc Natália Vicsápiová (Zone of Genius)', '2026-11-01'],
  ['BNI: content štruktúra Natália + kreatívy a formáty (podľa SCH)', '2026-11-01'],
  ['INR: wireframe company profilu, poslať Filipovi na schválenie', '2026-11-01'],
  ['INR: texty company profilu (až po schválení wireframu)', '2026-11-01'],
  ['FIG: dokončiť naštudovanie biznisu (FIGA MR)', '2026-11-01'],
  ['FIG: pre-production doc MR, CR, USP podľa šablóny', '2026-11-01'],
  ['FIG: TPA v Miro boarde (všetci konkurenti)', '2026-11-01'],
  ['FP: poslať všetko Filipovi do 19:00', '2026-11-01'],
]

function parseEnv(p) {
  const o = {}
  for (let l of readFileSync(p, 'utf8').split(/\r?\n/)) {
    l = l.trim(); if (!l || l.startsWith('#')) continue
    const i = l.indexOf('='); if (i === -1) continue
    let v = l.slice(i + 1).trim()
    if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) v = v.slice(1, -1)
    o[l.slice(0, i).trim()] = v
  }
  return o
}
const env = parseEnv('C:\\Users\\jakub\\crm-ops\\.env.prod.local')

const c = new Client({ host: env.PGHOST, port: Number(env.PGPORT || 5432), user: env.PGUSER, password: env.PGPASSWORD, database: env.PGDATABASE, ssl: { rejectUnauthorized: false } })
try {
  await c.connect()
  const { rows: owners } = await c.query(`select id from profiles where role = 'admin' and is_active`)
  if (owners.length !== 1) throw new Error(`cakal som 1 ownera, nasiel som ${owners.length}`)
  const ownerId = owners[0].id

  await c.query('begin')
  let added = 0
  for (const [title, due] of TODOS) {
    const { rowCount } = await c.query(
      `insert into owner_todos (owner_id, title, due_date)
       select $1, $2, $3
       where not exists (select 1 from owner_todos where owner_id = $1 and title = $2 and done = false)`,
      [ownerId, title, due],
    )
    added += rowCount
  }
  await c.query('commit')
  console.log(`pridane ulohy: ${added} z ${TODOS.length} (zvysok uz v checkliste bol)`)
  await c.end()
} catch (e) {
  try { await c.query('rollback') } catch {}
  console.error('CHYBA:', e.message)
  try { await c.end() } catch {}
  process.exit(1)
}
