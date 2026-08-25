(async () => {
  const same = u => { try { return new URL(u, location.href).origin === location.origin } catch { return false } };
  const cap = (set, n) => [...set].sort().slice(0, n);
  const res = { 주소: location.href, 수집시각: new Date().toISOString() };

  /* 1. 이 화면의 HTML */
  res.html = document.documentElement.outerHTML;

  /* 2. CSS — 같은 도메인 스타일시트 전문 + :root 디자인 토큰 */
  let css = '', tokens = {};
  for (const sheet of document.styleSheets) {
    let rules; try { rules = sheet.cssRules } catch { continue }   // 외부 시트는 못 읽음
    for (const r of rules) {
      css += r.cssText + '\n';
      if (r.style && r.selectorText && /^(:root|html|\[data-theme)/.test(r.selectorText)) {
        for (const p of r.style) if (p.startsWith('--')) tokens[p] = r.style.getPropertyValue(p).trim();
      }
    }
  }
  res.css = css;
  res.디자인토큰 = tokens;

  /* 3. 실제 적용된 본문 스타일 */
  const cs = getComputedStyle(document.body);
  res.본문스타일 = { 글꼴: cs.fontFamily, 크기: cs.fontSize, 글자색: cs.color, 배경: cs.backgroundColor };

  /* 4. 번들에서 구조 힌트 뽑기 */
  const urls = [...new Set([...document.querySelectorAll('script[src]')].map(s => s.src).filter(same))];
  const 라우트 = new Set(), api = new Set(), 한글 = new Set(), 아이콘 = new Set();
  let 읽은번들 = 0, 총바이트 = 0;

  for (const url of urls) {
    let js; try { js = await (await fetch(url)).text() } catch { continue }
    읽은번들++; 총바이트 += js.length;
    for (const m of js.matchAll(/["'`](\/[a-z0-9\-_\/\[\]]{2,60})["'`]/gi)) {
      const p = m[1];
      if (p.startsWith('/api/')) api.add(p);
      else if (!/\.(js|css|png|jpe?g|svg|webp|ico|woff2?|map|json)$/i.test(p) && !p.startsWith('/_next')) 라우트.add(p);
    }
    for (const m of js.matchAll(/["'`]([^"'`\n]*[가-힣][^"'`\n]{0,40})["'`]/g)) {
      const s = m[1].trim();
      if (s.length >= 2 && s.length <= 40) 한글.add(s);
    }
    for (const m of js.matchAll(/\b([A-Z][a-zA-Z]{2,20})(?:Icon|_Icon)\b/g)) 아이콘.add(m[1]);
  }

  res.번들 = { 개수: urls.length, 읽음: 읽은번들, 총크기KB: Math.round(총바이트 / 1024) };
  res.라우트 = cap(라우트, 200);
  res.API경로 = cap(api, 200);
  res.한글문구 = cap(한글, 600);
  res.아이콘 = cap(아이콘, 150);

  console.log(`번들 ${읽은번들}/${urls.length}개 · ${res.번들.총크기KB}KB`);
  console.log(`라우트 ${res.라우트.length} · API ${res.API경로.length} · 한글문구 ${res.한글문구.length} · 아이콘 ${res.아이콘.length}`);
  console.log(`CSS ${Math.round(css.length / 1024)}KB · 디자인토큰 ${Object.keys(tokens).length}개`);
  console.log('\n라우트 미리보기:', res.라우트.slice(0, 25));

  const slug = (location.pathname.replace(/\//g, '_') || '_root').replace(/^_/, '');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(res, null, 2)], { type: 'application/json' }));
  a.download = `분석_${slug || 'root'}.json`; a.click();
  console.log(`\n→ 다운로드 폴더에 ${a.download} 저장됨`);
})();
