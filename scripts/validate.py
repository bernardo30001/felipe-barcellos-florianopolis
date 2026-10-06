"""Check public totals against the official snapshot and territorial membership."""
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
read = lambda p: json.loads((ROOT / p).read_text())
d = read('site/data.json')
sections = read('site/secoes.json')
official = read('research/municipio-oficial.json')
candidate = next(c for a in official['carg'][0]['agr'] for p in a['par'] for c in p['cand'] if c['n'] == '1414')
assert d['candidate']['cityVotes'] == int(candidate['vap']) == 3587
assert d['candidate']['year'] == 2026 and d['candidate']['party'] == 'MISSÃO'
assert len(sections) == d['coverage']['sectionCount'] == int(official['s']['st']) == 1207
assert len({(s['zone'], s['section']) for s in sections}) == len(sections)
assert sum(s['votes'] for s in sections) == d['candidate']['cityVotes']
by_location = defaultdict(list)
for s in sections:
    by_location[s['locationId']].append(s)
    assert s['source'].startswith('https://resultados.tse.jus.br/oficial/ele2026/')
fields = ['votes', 'validVotes', 'nominalValidVotes', 'partyVotes', 'blankVotes', 'nullVotes', 'technicalNullVotes', 'subJudiceVotes', 'turnout', 'electorate', 'sections']
locations = []
for n in d['neighborhoods']:
    for field in fields:
        assert sum(l[field] for l in n['locations']) == n[field], (n['name'], field)
    for l in n['locations']:
        locations.append(l)
        ss = by_location[l['id']]
        assert all(s['neighborhood'] == n['name'] for s in ss)
        for field in fields:
            assert sum(s[field] for s in ss) == l[field], (l['id'], field)
assert len(locations) == len(by_location) == d['coverage']['locationCount'] == 139
assert len(d['neighborhoods']) == d['coverage']['neighborhoodCount'] == 62
assert len({n['name'] for n in d['neighborhoods']}) == 62
assert sum(n['votes'] == 0 for n in d['neighborhoods']) == 5
assert sum(n['votes'] for n in d['neighborhoods']) == 3587
assert d['coverage']['unmatchedVotes'] == d['coverage']['unmatchedSections'] == 0
js = (ROOT / 'site/data.js').read_text()
assert json.loads(js.removeprefix('window.ELECTION_DATA = ').strip().removesuffix(';')) == d
with (ROOT / 'site/bairros.csv').open(encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f, delimiter=';'))
assert len(rows) == 62
print('PASS: 3.587 votos; 62 bairros/localidades; 139 locais; 1.207 seções; todos os níveis conferidos.')
