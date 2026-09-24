"""Explicit, resumable research import. Never called by the production build."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.firecrawl'

def collect(service):
    target = CACHE / (service['id'] + '.json')
    if not target.exists():
        cli = Path(shutil.which('firecrawl.cmd')).parent/'node_modules/firecrawl-cli/dist/index.js'
        result = subprocess.run([shutil.which('node'), str(cli), 'scrape', service['source_url'], '--format', 'markdown,links',
                                 '--max-age', '0', '--wait-for', '3000', '-o', str(target)],
                                capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=240)
        if result.returncode:
            return {**service, 'status':'fetch_failed', 'error':result.stderr[-500:]}
    data = json.loads(target.read_text(encoding='utf-8'))
    text = data.get('markdown', '')
    metadata = data.get('metadata', {})
    headings = [{'level':len(m.group(1)), 'title':m.group(2)}
                for m in re.finditer(r'^(#{1,6})\s+(.+)$', text, re.M)]
    return {**service, 'status':'researched' if len(text)>2000 and metadata.get('statusCode')==200 else 'needs_review',
            'retrieved_at': datetime.now(timezone.utc).isoformat(), 'source_status':metadata.get('statusCode'),
            'resolved_url':metadata.get('url') or metadata.get('sourceURL'), 'characters':len(text),
            'headings':headings, 'cache':target.relative_to(ROOT).as_posix()}

if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--ids', nargs='*'); parser.add_argument('--workers',type=int,default=2); args=parser.parse_args()
    services=json.loads((ROOT/'audit/navigation-services.json').read_text(encoding='utf-8'))
    if args.ids: services=[s for s in services if s['id'] in args.ids]
    CACHE.mkdir(exist_ok=True)
    manifest=ROOT/'audit/research-manifest.json'
    results={}
    if manifest.exists(): results={x['id']:x for x in json.loads(manifest.read_text(encoding='utf-8'))}
    with ThreadPoolExecutor(max_workers=min(2,max(1,args.workers))) as pool:
        futures={pool.submit(collect,s):s for s in services}
        for future in as_completed(futures):
            service=futures[future]
            try: row=future.result()
            except Exception as e: row={**service,'status':'fetch_failed','error':str(e)}
            results[row['id']]=row
            manifest.write_text(json.dumps(list(results.values()),ensure_ascii=False,indent=2),encoding='utf-8')
            print(row['id'],row['status'],row.get('characters',0),flush=True)
