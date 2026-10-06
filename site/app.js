'use strict';
(() => {
  const d = window.ELECTION_DATA;
  const $ = id => document.getElementById(id);
  if (!d || !Array.isArray(d.neighborhoods) || !d.neighborhoods.length) { $('load-error').hidden = false; return; }
  const nf = new Intl.NumberFormat('pt-BR');
  const pf = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2, minimumFractionDigits: 2 });
  const pct = n => pf.format(n) + '%';
  const esc = x => String(x ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const norm = x => x.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const label = x => String(x).toLocaleLowerCase('pt-BR').replace(/(^|[\s/(-])\p{L}/gu, c => c.toLocaleUpperCase('pt-BR')).replace(/\b(Da|De|Do|Das|Dos|E)\b/g, c => c.toLowerCase()).replace(/\b(Ii|Iii|Iv|Ifsc|Ufsc|Iee|Cemj|Eic|Sesc|Senac|Apae|Ndi|Cefet)\b/g, c => c.toUpperCase());
  const neighborhoods = [...d.neighborhoods].sort((a,b) => b.votes - a.votes || a.name.localeCompare(b.name, 'pt-BR'));
  neighborhoods.forEach((n,i) => n.rank = i + 1);
  let selected = neighborhoods[0].name;
  const total = d.candidate.cityVotes;
  $('city-votes').textContent = nf.format(total);
  $('city-share').textContent = `${pct(total / d.candidate.stateVotes * 100)} dos votos dele em SC`;
  $('neighborhood-count').textContent = nf.format(neighborhoods.length);
  $('location-count').textContent = nf.format(d.coverage.locationCount);
  $('section-count').textContent = `${nf.format(d.coverage.sectionCount)} seções apuradas`;
  $('top-neighborhood').textContent = label(neighborhoods[0].name);
  $('top-votes').textContent = `${nf.format(neighborhoods[0].votes)} votos · ${pct(neighborhoods[0].votes / total * 100)} do total`;
  $('snapshot-date').textContent = d.snapshotLabel || 'Consulta em 6 de outubro de 2026.';
  $('coverage-note').textContent = d.coverageNote || `A soma dos bairros resulta em ${nf.format(total)} votos, conferidos com o resultado municipal do TSE. A base reúne ${nf.format(d.coverage.sectionCount)} seções apuradas, ${nf.format(d.coverage.locationCount)} locais e ${nf.format(neighborhoods.length)} bairros/localidades. Votos sem bairro identificado: ${nf.format(d.coverage.unmatchedVotes || 0)}.`;
  $('relocation-note').textContent = d.relocationNote || '';
  if (!d.relocationNote) $('relocation-note').hidden = true;
  $('sources').innerHTML = d.sources.map(s => `<li><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.title)}</a></li>`).join('');
  function renderRows() {
    const query = norm($('search').value.trim());
    const rows = neighborhoods.filter(n => norm(n.name).includes(query));
    if ($('sort').value === 'name') rows.sort((a,b) => a.name.localeCompare(b.name, 'pt-BR'));
    $('result-count').textContent = `${rows.length} de ${neighborhoods.length} bairros/localidades · selecione para detalhar`;
    $('empty').hidden = rows.length > 0;
    $('neighborhood-rows').innerHTML = rows.map(n => `<tr class="${n.name === selected ? 'selected' : ''}"><td class="position">${String(n.rank).padStart(2,'0')}</td><td><button class="neighborhood-button" data-name="${esc(n.name)}" aria-pressed="${n.name === selected}" aria-controls="detail-title">${esc(label(n.name))}</button><div class="bar-track" aria-hidden="true"><div class="bar" style="width:${n.votes / neighborhoods[0].votes * 100}%"></div></div></td><td class="numeric votes-cell">${nf.format(n.votes)}</td><td class="numeric share-cell">${pct(n.votes / total * 100)}</td></tr>`).join('');
  }
  function renderDetail(name) {
    const n = neighborhoods.find(n => n.name === name);
    if (!n) return;
    selected = n.name;
    $('detail-title').textContent = label(n.name);
    $('detail-votes').textContent = nf.format(n.votes);
    $('detail-share-bar').style.width = `${n.votes / total * 100}%`;
    $('detail-share').innerHTML = `<strong>${pct(n.votes / total * 100)}</strong> dos votos de Felipe em Florianópolis vieram deste bairro.`;
    $('detail-locations').textContent = `${n.locations.length} ${n.locations.length === 1 ? 'local' : 'locais'} de votação`;
    $('detail-sections').textContent = `${n.sections} ${n.sections === 1 ? 'seção apurada' : 'seções apuradas'}`;
    $('locations').innerHTML = [...n.locations].sort((a,b) => b.votes - a.votes || a.name.localeCompare(b.name,'pt-BR')).map(l => `<article class="location"><h4 class="location-name">${esc(label(l.name))}</h4><strong class="location-votes">${nf.format(l.votes)}</strong><p class="location-info">${esc(label(l.address))}<br>Zona ${esc(l.zone)} · Local ${esc(l.number)} · ${esc(l.sections)} ${l.sections === 1 ? 'seção' : 'seções'}</p></article>`).join('');
    $('locations').scrollTop = 0;
  }
  $('neighborhood-rows').addEventListener('click', e => {
    const btn = e.target.closest('[data-name]'); if (!btn) return;
    const name = btn.dataset.name;
    renderDetail(name); renderRows();
    if (matchMedia('(max-width:820px)').matches) {
      $('detail-title').focus({preventScroll:true});
      $('detail-title').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth',block:'start'});
    } else {
      Array.from(document.querySelectorAll('[data-name]')).find(el => el.dataset.name === name)?.focus({preventScroll:true});
    }
  });
  $('search').addEventListener('input', renderRows);
  $('sort').addEventListener('change', renderRows);
  renderDetail(selected); renderRows();
})();
