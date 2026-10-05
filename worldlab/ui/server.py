"""Minimal dependency-free browser interface for testing the World Lab kernel."""
from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from worldlab.core.world import World
from worldlab.population.generator import generate_population

HTML = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WORLD LAB</title>
<style>:root{color-scheme:dark;font-family:system-ui;background:#080b10;color:#eef2f7}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 20% 0%,#172033,#080b10 45%);min-height:100vh}main{max-width:1100px;margin:auto;padding:20px}.eyebrow{font-size:12px;letter-spacing:.18em;color:#8ea2bd}.title{font-size:32px;font-weight:800;margin:5px 0}.sub{color:#9ba8b8}.grid{display:grid;grid-template-columns:320px 1fr;gap:16px}@media(max-width:800px){.grid{grid-template-columns:1fr}}.card{background:#10151e;border:1px solid #263140;border-radius:18px;padding:16px;box-shadow:0 12px 30px #0005}.card h2{font-size:16px;margin:0 0 14px}.field{margin:12px 0}.field label{display:block;font-size:12px;color:#9ba8b8;margin-bottom:6px}input,button{width:100%;border-radius:11px;border:1px solid #303b4b;background:#0b1017;color:#eef2f7;padding:11px;font:inherit}button{cursor:pointer;background:#eef2f7;color:#080b10;font-weight:700;margin-top:6px}button.secondary{background:#151d28;color:#dbe4ef}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}@media(max-width:650px){.metrics{grid-template-columns:repeat(2,1fr)}}.metric{padding:13px;border-radius:14px;background:#0b1017;border:1px solid #222c39}.metric b{display:block;font-size:22px;margin-top:3px}.metric span{font-size:11px;color:#8f9daf}.table{margin-top:14px;overflow:auto;max-height:430px}.person{display:grid;grid-template-columns:70px 1fr 1fr;gap:8px;padding:10px 0;border-bottom:1px solid #202a36;font-size:13px}.muted{color:#8f9daf}.trace{margin-top:14px;padding:12px;border-radius:12px;background:#0b1017;color:#b8c4d2;font-size:12px;line-height:1.5}.warning{color:#e5bd78}</style></head>
<body><main><div class="eyebrow">RESEARCH SIMULATION / EARLY TEST BUILD</div><div class="title">WORLD LAB</div><div class="sub">Run a small world. Inspect people. Advance time. Results are simulations, not predictions.</div><div class="grid">
<section class="card"><h2>World setup</h2><div class="field"><label>Population</label><input id="population" type="number" min="1" max="10000" value="100"></div><div class="field"><label>Seed</label><input id="seed" type="number" value="42"></div><div class="field"><label>Years to advance</label><input id="years" type="number" min="0" max="500" value="10"></div><button onclick="createWorld()">Create world</button><button class="secondary" onclick="advanceWorld()">Advance simulation</button><div id="status" style="margin-top:10px;color:#8fd3a8;min-height:20px"></div><div class="trace"><b>Current engine</b><br>Individual agents, households, demographics, social state and deterministic long-horizon execution.</div><div class="trace warning">Early test console — not yet the complete civilization-scale World Lab.</div></section>
<section><div class="card"><h2>World state</h2><div class="metrics"><div class="metric"><span>YEAR</span><b id="year">—</b></div><div class="metric"><span>PEOPLE</span><b id="people">—</b></div><div class="metric"><span>HOUSEHOLDS</span><b id="households">—</b></div><div class="metric"><span>EMPLOYMENT</span><b id="employment">—</b></div></div></div><div class="card" style="margin-top:16px"><h2>Individual people</h2><div id="list" class="table"><div class="muted">Create a world to inspect individuals.</div></div></div></section></div></main>
<script>async function call(p,o){const r=await fetch(p,o),d=await r.json();if(!r.ok)throw Error(d.error||'request failed');return d}function show(d){year.textContent=d.snapshot.year;people.textContent=d.snapshot.population;households.textContent=d.snapshot.households;employment.textContent=(d.snapshot.working_age_employment_rate*100).toFixed(1)+'%';list.innerHTML=d.people.map(p=>'<div class="person"><b>#'+p.id+'</b><span>Age '+p.age+' · '+p.sex+'</span><span>Health '+p.health.toFixed(2)+' · Edu '+p.education.toFixed(1)+'y</span></div>').join('')}async function createWorld(){try{const d=await call('/api/world',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({population:Number(population.value),seed:Number(seed.value)})});show(d);status.textContent='World created.'}catch(e){status.textContent=e.message}}async function advanceWorld(){try{const d=await call('/api/advance',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({years:Number(years.value)})});show(d);status.textContent='Simulation advanced.'}catch(e){status.textContent=e.message}}</script></body></html>'''

WORLD=None
def payload():
    people=[{"id":p.person_id,"age":p.age,"sex":p.sex,"health":p.health,"education":p.education_years} for p in sorted(WORLD.people.values(),key=lambda x:x.person_id)[:200]]
    return {"snapshot":WORLD.snapshot(),"people":people}
class Handler(BaseHTTPRequestHandler):
    def _send(self,s,d,ct="application/json"):
        raw=d if isinstance(d,bytes) else json.dumps(d).encode();self.send_response(s);self.send_header("Content-Type",ct);self.send_header("Content-Length",str(len(raw)));self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/": self._send(200,HTML.encode(),"text/html; charset=utf-8");return
        if path=="/api/state": self._send(409,{"error":"no world has been created"} if WORLD is None else payload());return
        self._send(404,{"error":"not found"})
    def do_POST(self):
        global WORLD
        try:
            body=json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))) or b"{}");path=urlparse(self.path).path
            if path=="/api/world":
                n,seed=int(body.get("population",100)),int(body.get("seed",42))
                if not 1<=n<=10000:raise ValueError("population must be between 1 and 10000")
                WORLD=World(seed=seed,start_year=2026);generate_population(WORLD,n);self._send(200,payload());return
            if path=="/api/advance":
                if WORLD is None:raise ValueError("create a world first")
                y=int(body.get("years",1))
                if not 0<=y<=500:raise ValueError("years must be between 0 and 500")
                WORLD.advance_days(y*365);self._send(200,payload());return
            self._send(404,{"error":"not found"})
        except Exception as e:self._send(400,{"error":str(e)})
    def log_message(self,*a):pass
def run(host="127.0.0.1",port=8000):ThreadingHTTPServer((host,port),Handler).serve_forever()
if __name__=="__main__":run()
