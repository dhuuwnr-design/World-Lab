#!/usr/bin/env python3
"""Zero-dependency local server for the WORLD LAB showable prototype."""
from __future__ import annotations
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from worldlab.core.interventions import InterventionDefinition, PopulationScope
from worldlab.core.world import World
from worldlab.experiments.scenarios import ScenarioSpec, run_scenario
from worldlab.presentation.contracts import ScenarioDefinition
from worldlab.population.generator import generate_population

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"prototype"/"index.html"
PRESETS={
"clean":dict(name="Affordable clean energy",mechanism_id="technology.diffusion",adoption_benefit=.8,adoption_cost=.1,person_effects={"health":.01,"money":25.0},belief_updates={"technology_trust":.05}),
"education":dict(name="Education access",mechanism_id="human.capital",adoption_benefit=.9,adoption_cost=.05,person_effects={"education_years":.08,"income":8.0},belief_updates={"education_value":.04}),
"health":dict(name="Health access",mechanism_id="health.access",adoption_benefit=.9,adoption_cost=.05,person_effects={"health":.01,"money":10.0},belief_updates={"health_trust":.04}),
"technology":dict(name="New household technology",mechanism_id="technology.adoption",adoption_benefit=.7,adoption_cost=.2,person_effects={"money":15.0,"health":.005},belief_updates={"technology_trust":.03}),
}
def interpret_prompt(prompt):
    text=" ".join(str(prompt).lower().split())
    rules=[
        (("education","school","learning"),"education"),
        (("health","healthcare","medicine"),"health"),
        (("electricity","clean energy","energy"),"clean"),
        (("technology","artificial intelligence"," ai ","technology"),"technology"),
    ]
    for needles,key in rules:
        if any(n in text for n in needles):
            match=re.search(r"(\d+(?:\.\d+)?)\s*%",text)
            scale=min(1.5,max(.25,float(match.group(1))/100.0)) if match else 1.0
            return key,scale
    return None,1.0

def build_run(payload):
    prompt=str(payload.get("prompt","")).strip()
    reference=str(payload.get("reference","")).strip()
    key=str(payload.get("intervention","clean"))
    scale=1.0
    if prompt:
        key,scale=interpret_prompt(prompt)
        if key is None:
            raise ValueError("I could not map this scenario to an executable mechanism yet. Try education, health/healthcare, electricity/energy, technology, or AI.")
        lower=" ".join(prompt.lower().split())
        if any(x in lower for x in ("everyone","every person","all people","entire population","100% of the population")):
            prompt_scope=1.0
        elif "half the population" in lower or "50% of the population" in lower:
            prompt_scope=.5
        elif "quarter of the population" in lower or "25% of the population" in lower:
            prompt_scope=.25
        else:
            prompt_scope=None
    else:
        prompt_scope=None
    people=max(10,min(5000,int(payload.get("people",500))))
    years=max(1,min(100,int(payload.get("years",10))))
    scope=max(.01,min(1.,prompt_scope if prompt_scope is not None else float(payload.get("scope",.5))))
    p=PRESETS.get(key)
    if p is None:
        raise ValueError("Unknown scenario mechanism.")
    iid=f"scenario-{key}-{people}-{years}-{int(scope*100)}"
    effects={name:delta*scale for name,delta in p["person_effects"].items()}
    intervention=InterventionDefinition(
        intervention_id=iid,name=p["name"],mechanism_id=p["mechanism_id"],
        start_day=0,end_day=years*365,scope=PopulationScope(fraction=scope),
        exposure_fraction=1.,access_fraction=1.,
        adoption_benefit=p["adoption_benefit"],adoption_cost=p["adoption_cost"],
        adoption_uncertainty=.1,adoption_social_effect=.15,
        person_effects=effects,belief_updates=p["belief_updates"],
        evidence_references=(f"USER-REFERENCE:{reference}",) if reference else ("WORLD-LAB-DEMO-EVIDENCE-01",),
        uncertainty={"effect_scale":scale,"interpretation":"prototype keyword mapping; not calibrated to referenced real-world evidence"},
    )
    contract=ScenarioDefinition(
        scenario_id=iid,intervention=intervention.to_dict(),
        population_scope=intervention.scope.to_dict(),geography={"world":"prototype"},
        start_time=0,end_time=years*365,seed=99,model_version="0.15-ui-prototype",
        evidence_snapshot_id=None,
    )
    spec=ScenarioSpec(contract,intervention,intervention.scope.to_dict(),intervention.evidence_references,intervention.uncertainty)
    baseline=World(seed=7); generate_population(baseline,people); run=run_scenario(baseline,spec)
    counts={}
    for r in run.result.intervention_engine.records: counts[r.status]=counts.get(r.status,0)+1
    sample=[]
    for person in sorted(run.result.people.values(),key=lambda x:x.person_id)[:12]:
        status=next((r.status for r in reversed(run.result.intervention_engine.records) if r.person_id==person.person_id),"not selected")
        sample.append({"agent_id":person.agent.agent_id if person.agent else f"person:{person.person_id}","age":person.age,"health":person.health,"education":person.education_years,"income":person.income,"status":status})
    out=run.to_dict()
    out["prompt"]=prompt
    out["interpretation"]={"mechanism":key,"name":p["name"],"effect_scale":scale,"reference":reference or None,"assumption":"Explicit rule-based prompt translation; not an LLM claim or calibrated causal estimate."}
    out["exposure"]=counts
    out["people"]=sample
    return out

class Handler(BaseHTTPRequestHandler):
    def send_json(self,status,payload):
        raw=json.dumps(payload).encode(); self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        if self.path=="/api/health": return self.send_json(200,{"ok":True})
        if self.path in ("/","/index.html"):
            raw=INDEX.read_bytes(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw); return
        self.send_error(404)
    def do_POST(self):
        if self.path!="/api/run": return self.send_error(404)
        try:
            n=int(self.headers.get("Content-Length","0")); payload=json.loads(self.rfile.read(n) or b"{}"); self.send_json(200,build_run(payload))
        except Exception as exc: self.send_json(400,{"error":str(exc)})
    def log_message(self,*args): return
if __name__=="__main__":
    print("WORLD LAB prototype: http://127.0.0.1:8765"); ThreadingHTTPServer(("127.0.0.1",8765),Handler).serve_forever()
