(async () => {
  const same = u => { try { return new URL(u, location.href).origin === location.origin } catch { return false } };
  const urls = [...new Set([...document.querySelectorAll('script[src]')].map(s => s.src).filter(same))];
  const out = {}; const rep = { 인라인: 0, 외부: 0, 없음: 0, 못읽음: 0 };
  const take = (map, from) => {
    let n = 0;
    (map.sources || []).forEach((src, i) => {
      const body = (map.sourcesContent || [])[i];
      if (!body || src.includes('node_modules')) return;
      out[src.replace(/^webpack:\/\/(_N_E\/)?/, '').replace(/^\.\//, '').split('?')[0]] = body;
      n++;
    });
    console.log(`  [${from}] ${n}개`);
  };
  console.log(`번들 ${urls.length}개 검사\n`);
  for (const url of urls) {
    const name = url.split('/').pop().split('?')[0];
    let js;
    try { js = await (await fetch(url)).text() } catch { rep.못읽음++; console.log(`  [못읽음] ${name}`); continue }
    const m = js.slice(-4096).match(/\/\/[#@]\s*sourceMappingURL=(\S+)/);
    if (!m) { rep.없음++; console.log(`  [주석없음] ${name}`); continue }
    if (m[1].startsWith('data:')) {
      rep.인라인++;
      console.log(`  [인라인맵] ${name}`);
      try { take(JSON.parse(atob(m[1].split(',')[1])), '인라인'); }
      catch { console.log('     (디코드 실패)') }
      continue;
    }
    const mapUrl = new URL(m[1], url).href;
    try {
      const res = await fetch(mapUrl);
      if (!res.ok) { rep.없음++; console.log(`  [맵 ${res.status}] ${name}  ← ${m[1]}`); continue }
      rep.외부++; console.log(`  [외부맵] ${name}`); take(await res.json(), '외부');
    } catch { rep.없음++; console.log(`  [맵실패] ${name}`) }
  }
  const total = Object.keys(out).length;
  console.log(`\n요약 — 인라인 ${rep.인라인} / 외부 ${rep.외부} / 없음 ${rep.없음} / 못읽음 ${rep.못읽음}`);
  console.log(`복원된 원본 파일 ${total}개`);
  if (!total) return console.log('\n결론: 소스맵이 배포되지 않았습니다. 원본 코드는 가져올 수 없습니다.');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(out, null, 2)], { type: 'application/json' }));
  a.download = 'extracted-source.json'; a.click();
  console.log('→ 다운로드 폴더에 extracted-source.json 저장됨');
})();
