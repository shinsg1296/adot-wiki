/* 배포된 사이트에서 원본 소스 추출 — 브라우저 콘솔용 (설치 불필요)
   대상 사이트를 연 상태에서 F12 → Console 에 붙여넣고 Enter.
   결과는 extracted-source.json 한 파일로 다운로드된다. */
(async () => {
  const sameOrigin = (u) => {
    try { return new URL(u, location.href).origin === location.origin; }
    catch (e) { return false; }
  };

  const assets = [
    ...[...document.querySelectorAll('script[src]')].map((s) => s.src),
    ...[...document.querySelectorAll('link[rel=stylesheet][href]')].map((l) => l.href),
  ].filter(sameOrigin);

  const uniq = [...new Set(assets)];
  console.log(`번들 ${uniq.length}개 발견\n`);

  const out = {};
  let mapCount = 0;

  for (const url of uniq) {
    const label = url.split('/').pop().split('?')[0];
    let mapUrl = url + '.map';

    try {
      const js = await (await fetch(url)).text();
      const m = js.slice(-2048).match(/\/\/[#@]\s*sourceMappingURL=(\S+)/);
      if (m && !m[1].startsWith('data:')) mapUrl = new URL(m[1], url).href;
    } catch (e) { /* 번들을 못 읽어도 .map 은 찍어본다 */ }

    try {
      const res = await fetch(mapUrl);
      if (!res.ok) { console.log(`  [ - ] ${label}`); continue; }
      const map = await res.json();
      const sources = map.sources || [];
      const contents = map.sourcesContent || [];
      let n = 0;

      sources.forEach((src, i) => {
        const body = contents[i];
        if (!body || src.includes('node_modules')) return;
        const name = src
          .replace(/^webpack:\/\/(_N_E\/)?/, '')
          .replace(/^webpack-internal:\/\/\//, '')
          .replace(/^\.\//, '')
          .split('?')[0];
        if (!name) return;
        out[name] = body;
        n++;
      });

      mapCount++;
      console.log(`  [맵] ${label}  →  ${n}개`);
    } catch (e) {
      console.log(`  [ - ] ${label}`);
    }
  }

  const total = Object.keys(out).length;
  console.log(`\n소스맵 ${mapCount}개 / 원본 파일 ${total}개`);

  if (!total) {
    console.log('소스맵이 없습니다. 원본 코드는 가져올 수 없습니다.');
    return;
  }

  const blob = new Blob([JSON.stringify(out, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'extracted-source.json';
  document.body.appendChild(a);
  a.click();
  a.remove();
  console.log('→ 다운로드 폴더에 extracted-source.json 저장됨');
})();
