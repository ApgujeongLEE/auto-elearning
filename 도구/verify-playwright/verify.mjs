#!/usr/bin/env node
/**
 * verify.mjs — Hyperframes 컴포지션 DOM 기반 타이밍 검증
 *
 * 동작:
 *   1. 헤드리스 Chromium으로 Hyperframes Studio 페이지(localhost:3002) 또는 정적 파일을 띄움
 *   2. 페이지 안의 GSAP timeline을 직접 seek해 각 시점의 DOM 상태 캡처
 *   3. sync_map.json의 resolved 시점에서 expected_element가 visible(opacity > 0.1)인지 검사
 *   4. 결과를 verify_report.md / verify_report.json 으로 저장
 *
 * 입력:
 *   --sync-map <path>     sync_patcher가 만든 sync_map.json
 *   --html <path>         검증할 index.html (file:// 로 로딩) — Studio 서버가 꺼져 있을 때
 *   --studio <url>        Studio URL — 켜져 있을 때 (예: http://localhost:3002/#project/composition)
 *   --report <path>       검증 결과 저장 경로 (디렉토리)
 *   --tolerance <sec>     싱크 허용 오차 (기본 0.15)
 *
 * 사용 예:
 *   node verify.mjs \
 *     --sync-map ../../프로젝트/001_agentic-ai_2026-05-15/06_편집/검증/sync_map.json \
 *     --html ../../프로젝트/001_agentic-ai_2026-05-15/06_편집/hyperframes/index.html \
 *     --report ../../프로젝트/001_agentic-ai_2026-05-15/06_편집/검증
 */

import { chromium } from "playwright";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { pathToFileURL } from "node:url";
import { dirname, resolve, basename } from "node:path";

function parseArgs(argv) {
  const out = { tolerance: 0.15 };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    if (k.startsWith("--")) {
      const key = k.slice(2).replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      out[key] = argv[++i];
    }
  }
  return out;
}

async function main() {
  const args = parseArgs(process.argv);
  if (!args.syncMap) {
    console.error("❌ --sync-map 필수");
    process.exit(1);
  }
  if (!args.html && !args.studio) {
    console.error("❌ --html 또는 --studio 중 하나 필요");
    process.exit(1);
  }

  const syncMap = JSON.parse(await readFile(resolve(args.syncMap), "utf-8"));
  const tolerance = parseFloat(args.tolerance) || 0.15;

  console.log(`📋 검증 대상: ${Object.keys(syncMap.resolved).length}개 이벤트`);
  console.log(`📏 허용 오차: ±${tolerance}초`);

  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  const url = args.studio
    ? args.studio
    : pathToFileURL(resolve(args.html)).toString();

  console.log(`🌐 페이지 로딩: ${url}`);
  await page.goto(url, { waitUntil: "networkidle" });
  // GSAP timeline 준비될 때까지 대기 (최대 5초)
  await page.waitForFunction(() => window.__timelines && window.__timelines.main, { timeout: 5000 })
    .catch(() => console.warn("⚠️  window.__timelines.main을 찾지 못함 — Studio가 켜져 있는지 확인"));

  const results = [];
  // event_id → 예상 보이는 요소 ID (sync_map의 rules.event_id가 곧 GSAP target ID인 경우)
  // 컨벤션: event_id == 요소 셀렉터 (예: s01-check-in 이면 #s01-check)
  const inferTarget = (eventId) => {
    // 트레일링 -in/-out/-on/-off 제거
    const stripped = eventId.replace(/-(in|out|on|off|enter|exit)$/i, "");
    return `#${stripped}`;
  };

  for (const [eventId, t] of Object.entries(syncMap.resolved)) {
    const target = inferTarget(eventId);
    // GSAP timeline을 t로 seek 후, 잠깐 기다린 뒤 DOM 상태 캡처
    const state = await page.evaluate(({ t, target }) => {
      const tl = window.__timelines?.main;
      if (!tl) return { error: "no timeline" };
      tl.seek(t);
      const el = document.querySelector(target);
      if (!el) return { error: "element not found", target };
      const cs = getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      return {
        target,
        seek: t,
        opacity: parseFloat(cs.opacity),
        visibility: cs.visibility,
        display: cs.display,
        transform: cs.transform,
        bbox: { x: rect.x, y: rect.y, w: rect.width, h: rect.height },
      };
    }, { t, target });

    const pass = state && !state.error && state.opacity > 0.1 && state.visibility !== "hidden" && state.display !== "none";
    results.push({ eventId, target, expectedTime: t, pass, state });
    console.log(`   ${pass ? "✅" : "❌"} [${eventId}] @ ${t.toFixed(2)}s  target=${target}  opacity=${state.opacity ?? "?"}`);
  }

  await browser.close();

  // 리포트 저장
  const reportDir = args.report ? resolve(args.report) : dirname(resolve(args.syncMap));
  await mkdir(reportDir, { recursive: true });

  const okCount = results.filter(r => r.pass).length;
  const failCount = results.length - okCount;

  const json = {
    generatedAt: new Date().toISOString(),
    url,
    tolerance,
    summary: { total: results.length, ok: okCount, fail: failCount },
    results,
  };
  await writeFile(resolve(reportDir, "verify_report.json"), JSON.stringify(json, null, 2), "utf-8");

  // 마크다운 리포트
  const lines = [
    `# Verify Report (Playwright DOM)`,
    ``,
    `- 생성 시각: ${json.generatedAt}`,
    `- 검증 URL: \`${url}\``,
    `- 결과: **${okCount} OK / ${failCount} FAIL** (총 ${results.length})`,
    ``,
    `## 상세`,
    ``,
    `| event_id | 시점 (s) | target | 결과 | opacity | display | visibility |`,
    `|---|---|---|---|---|---|---|`,
    ...results.map(r =>
      `| \`${r.eventId}\` | ${r.expectedTime.toFixed(2)} | \`${r.target}\` | ${r.pass ? "✅" : "❌"} | ${r.state?.opacity?.toFixed?.(3) ?? "?"} | ${r.state?.display ?? "?"} | ${r.state?.visibility ?? "?"} |`
    ),
  ];
  await writeFile(resolve(reportDir, "verify_report.md"), lines.join("\n"), "utf-8");

  console.log(`\n📄 저장:`);
  console.log(`   - ${resolve(reportDir, "verify_report.json")}`);
  console.log(`   - ${resolve(reportDir, "verify_report.md")}`);
  console.log(`\n결과: ${okCount} OK / ${failCount} FAIL`);
  if (failCount > 0) process.exit(1);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
