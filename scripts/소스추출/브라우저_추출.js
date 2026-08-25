(async () => {
  const same = u => { try { return new URL(u, location.href).origin === location.origin } catch { return false } };
  const urls = [...new Set([
    ...[...document.querySelectorAll('script[src]')].map(s => s.src),
    ...[...document.querySelectorAll('link[rel=stylesheet][href]')].map(l => l.href)
  ].filter(same))];
  console.log(`번들 ${urls.length}개 발견\n`);
  const out = {}; let maps = 0;
  for (const url of urls) {
    const name = url.split('/').pop().split('?')[0];
    let mapUrl = url + '.map';
    try {
      const js = await (await fetch(url)).text();
      const m = js.slice(-2048).match(/\/\/[#@]\s*sourceMappingURL=(\S+)/);
      if (m && !m[1].startsWith('data:')) mapUrl = new URL(m[1], url).href;
    } catch {}
    try {
      const res = await fetch(mapUrl);
      if (!res.ok) { console.log(`  [ - ] ${name}`); continue }
      const map = await res.json(); let n = 0;
      (map.sources || []).forEach((src, i) => {
        const body = (map.sourcesContent || [])[i];
        if (!body || src.includes('node_modules')) return;
        out[src.replace(/^webpack:\/\/(_N_E\/)?/, '').replace(/^\.\//, '').split('?')[0]] = body;
        n++;
      });
      maps++; console.log(`  [맵] ${name}  →  ${n}개`);
    } catch { console.log(`  [ - ] ${name}`) }
  }
  const total = Object.keys(out).length;
  console.log(`\n소스맵 ${maps}개 / 원본 파일 ${total}개`);
  if (!total) return console.log('소스맵 없음 — 원본 코드는 못 가져옵니다.');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(out, null, 2)], { type: 'application/json' }));
  a.download = 'extracted-source.json'; a.click();
  console.log('→ 다운로드 폴더에 extracted-source.json 저장됨');
})();
