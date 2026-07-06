"""Build an interactive artist co-performance map (israeli-singers-network/index.html).
 Reads the graph (artist_network_nodes.csv + artist_network_edges.csv) plus songs.csv for the
Hebrew display names, and renders a self-contained vis-network page.
"""
import json
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
NODES_CSV = ROOT / "artist_network_nodes.csv"
EDGES_CSV = ROOT / "artist_network_edges.csv"
KAGGLE_CSV = ROOT / "songs.csv"
OUT_DIR = ROOT

# muted pastel community palette (works on a light background)
PALETTE = ["#6b9bd1", "#e8927c", "#7fb685", "#b98fc9", "#e0b354",
           "#5bc0be", "#d98cae", "#9c9c6b", "#8aa1b1", "#c0855b"]


def color(community):
    return PALETTE[int(community) % len(PALETTE)]


def build():
    nodes = pd.read_csv(NODES_CSV)
    edges = pd.read_csv(EDGES_CSV)

    # artist_key -> most common Hebrew display name (display only; analysis stays keyed on artist_key)
    raw = pd.read_csv(KAGGLE_CSV)
    name_heb = raw.groupby("artist_key")["artist"].agg(lambda s: s.mode().iat[0]).to_dict()

    totals = nodes["shared_songs_total"]
    lo, hi = int(totals.min()), int(totals.max())

    def base_size(v):
        return round(10 + 36 * (v - lo) / ((hi - lo) or 1))   # matches NODE_MIN..NODE_MAX in the page

    nodes_json = []
    for _, r in nodes.iterrows():
        key = r["artist_key"]
        name = name_heb.get(key, key)
        fill = color(r["community"])
        total = int(r["shared_songs_total"])
        nodes_json.append({
            "id": key, "name": name, "label": " ",
            "size": base_size(total),
            "shared": total,
            "partners": int(r["partners"]),
            "community": int(r["community"]),
            "color": {"background": fill, "border": "#ffffff",
                      "highlight": {"background": fill, "border": "#555555"}},
            "title": f"{name} · {int(r['partners'])} שותפים · {total} שירים משותפים",
        })

    edges_json = [{"from": r["artist_key_1"], "to": r["artist_key_2"], "value": int(r["shared_songs"])}
                  for _, r in edges.iterrows()]

    # community -> leading artist (for the legend)
    legend = []
    for comm, grp in nodes.groupby("community"):
        top_key = grp.sort_values("shared_songs_total", ascending=False).iloc[0]["artist_key"]
        legend.append({"community": int(comm), "color": color(comm), "top": name_heb.get(top_key, top_key)})

    html = (TEMPLATE
            .replace("__NODES__", json.dumps(nodes_json, ensure_ascii=False))
            .replace("__EDGES__", json.dumps(edges_json, ensure_ascii=False))
            .replace("__LEGEND__", json.dumps(legend, ensure_ascii=False)))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "index.html").write_text(html, encoding="utf-8")

    print(f"wrote {OUT_DIR / 'index.html'} ({len(nodes_json)} nodes, {len(edges_json)} edges)")


TEMPLATE = r'''<!DOCTYPE html>
<html lang="he">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>מפת אמנים · Artist Co-Performance Network</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;700&display=swap" rel="stylesheet">
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  html,body{margin:0;height:100%;background:#212329;font-family:'Rubik',system-ui,sans-serif;color:#333;overflow:hidden;}
  #net{width:100vw;height:100vh;}
  #legend{position:absolute;top:16px;right:16px;background:rgba(255,255,255,0.92);border:1px solid #e7e7e3;border-radius:12px;padding:12px 16px;font-size:13px;line-height:1.95;box-shadow:0 2px 12px rgba(0,0,0,0.06);}
  #legend h3{margin:0 0 8px;font-size:14px;font-weight:700;}
  #legend div{cursor:pointer;user-select:none;transition:opacity .15s;}
  #legend div:hover{opacity:0.7;}
  #legend div.active{font-weight:700;background:rgba(0,0,0,0.06);border-radius:6px;margin:2px -6px;padding:0 6px;}
  .dot{display:inline-block;width:11px;height:11px;border-radius:50%;margin-left:7px;vertical-align:middle;}
  #hint{position:absolute;bottom:16px;left:50%;transform:translateX(-50%);background:rgba(255,255,255,0.88);border:1px solid #e7e7e3;border-radius:20px;padding:7px 18px;font-size:12.5px;color:#666;}
  .vis-tooltip{font-family:'Rubik',sans-serif !important;background:#fff !important;border:1px solid #e2e2de !important;border-radius:8px !important;color:#333 !important;box-shadow:0 3px 14px rgba(0,0,0,0.10) !important;padding:7px 11px !important;font-size:13px !important;}
</style>
</head>
<body>
<div id="net"></div>
<div id="legend" dir="rtl"><h3>קהילות</h3></div>
<script>
const NODES = __NODES__;
const EDGES = __EDGES__;
const LEGEND = __LEGEND__;

const nodes = new vis.DataSet(NODES);
const edges = new vis.DataSet(EDGES);
const EDGE_BASE = 'rgba(200,200,200,0.24)';
const options = {
  nodes: { shape:'dot', borderWidth:1.5,
           font:{ face:'Rubik', size:15, color:'#2b2b2b', strokeWidth:4, strokeColor:'#f7f7f4' } },
  edges: { color:{ color:EDGE_BASE, highlight:'rgba(60,60,60,0)', inherit:false },
           scaling:{ min:0.3, max:6 }, smooth:false },
  interaction:{ hover:true, tooltipDelay:120, navigationButtons:false, keyboard:false, hideEdgesOnDrag:true },
  physics:{ solver:'barnesHut',
            barnesHut:{ gravitationalConstant:-32000, centralGravity:0.12, springLength:220,
                        springConstant:0.035, damping:0.4, avoidOverlap:0.7 },
            stabilization:{ iterations:400 } }
};
const network = new vis.Network(document.getElementById('net'), {nodes, edges}, options);
const container = document.getElementById('net');

// ---------- community legend + on/off toggles ----------
const legendEl = document.getElementById('legend');
const nodeComm = {}; NODES.forEach(n => nodeComm[n.id] = n.community);
// click a community to HIGHLIGHT it (dim the rest); click it again to clear.
let selectedComm = null;
let focusId = null, focusKeep = new Set(), lockedNode = null;   // node hover / click-lock focus
function applyCommunitySelect(){
  if(selectedComm === null){
    nodes.update(NODES.map(n => ({ id:n.id, color:{background:baseColor[n.id], border:'#ffffff'}, opacity:1 })));
    edges.update(edges.getIds().map(id => ({ id, color:EDGE_BASE })));
    return;
  }
  nodes.update(NODES.map(n => ({ id:n.id,
    color: n.community===selectedComm ? {background:baseColor[n.id], border:'#ffffff'} : {background:'#33363d', border:'#33363d'},
    opacity: n.community===selectedComm ? 1 : 0.22 })));
  edges.update(edges.getIds().map(id => { const e = edges.get(id);
    const on = nodeComm[e.from]===selectedComm && nodeComm[e.to]===selectedComm;
    return { id, color: on ? 'rgba(255,255,255,0.7)' : 'rgba(200,200,200,0.03)' }; }));
}
LEGEND.forEach(l => {
  const row = document.createElement('div');
  row.innerHTML = '<span class="dot" style="background:' + l.color + '"></span>' + l.top + ' ואחרים';
  row.onclick = () => {
    selectedComm = (selectedComm === l.community) ? null : l.community;
    Array.from(legendEl.querySelectorAll('div')).forEach(d => d.classList.remove('active'));
    if(selectedComm !== null) row.classList.add('active');
    lockedNode = null; focusId = null; focusKeep = new Set();   // a community selection clears any node lock
    applyCommunitySelect();
    refreshLabels();
  };
  legendEl.appendChild(row);
});

// ---------- map-style sizing: constant on-screen size + a focus lens ----------
// nodes/labels hold a constant screen size (divide world size by zoom). on top of that a
// "focus lens" makes whatever is near the viewport centre bigger and far nodes smaller, so
// panning around feels alive.
const NAME = {}, IMP = {}, baseColor = {};
NODES.forEach(n => { NAME[n.id]=n.name; IMP[n.id]=n.shared; baseColor[n.id]=n.color.background; });
const order = NODES.map(n=>n.id).sort((a,b)=>IMP[b]-IMP[a]);
const rank = {}; order.forEach((id,i)=>rank[id]=i);
const shown = {}; NODES.forEach(n=>shown[n.id]=null);

const TARGET_FONT = 16;              // on-screen label size (px)
const NODE_MIN = 10, NODE_MAX = 46;  // on-screen node size range (px)
const EDGE_MIN = 0.6, EDGE_MAX = 6;  // on-screen edge width range (px)
const BORDER = 1.5;                  // node outline width (px)
const BASE = 20;                     // labels shown when fully zoomed out
const FOCUS_R = 280;                 // focus-lens radius (px); smaller = tighter focus
const FOCUS_MAX = 1.6;               // size multiplier at the centre of the view
const FOCUS_MIN = 0.55;              // size multiplier far from the centre
const LABEL_ZOOM_EXP = 1.9;          // >1 = labels appear sooner as you zoom in (higher = fewer zooms needed)
let initScale = 1, ready = false;   // ready gates resize() until after the first fit

const loShared = Math.min(...NODES.map(n=>n.shared)), hiShared = Math.max(...NODES.map(n=>n.shared));
const baseSize = {};
NODES.forEach(n => { baseSize[n.id] = NODE_MIN + (NODE_MAX-NODE_MIN)*(n.shared-loShared)/((hiShared-loShared)||1); });

// ---------- focus (hover / click-lock): highlight a node + its neighbours ----------
const neighSet = id => { const s=new Set([id]); network.getConnectedNodes(id).forEach(x=>s.add(x)); return s; };
function labelBudget(){ const s=network.getScale()||1;
  return Math.min(order.length, Math.max(BASE, Math.round(BASE*Math.pow(s/initScale, LABEL_ZOOM_EXP)))); }
// a focused node forces labels to just its neighbourhood; otherwise the zoom LOD (top hubs) applies
function wantLabel(id, k){ return focusId!==null ? focusKeep.has(id) : rank[id] < k; }
function refreshLabels(){
  const k = labelBudget(); const upd = [];
  NODES.forEach(n => { const show = wantLabel(n.id, k);
    if(shown[n.id] !== show){ upd.push({id:n.id, label:show?NAME[n.id]:' '}); shown[n.id]=show; } });
  if(upd.length) nodes.update(upd);
}
function highlightNode(id){
  focusId = id; focusKeep = neighSet(id);
  nodes.update(NODES.map(n => ({ id:n.id,
    color: focusKeep.has(n.id) ? {background:baseColor[n.id],border:'#ffffff'} : {background:'#33363d',border:'#33363d'},
    opacity: focusKeep.has(n.id) ? 1 : 0.35 })));
  edges.update(edges.getIds().map(eid => { const e=edges.get(eid);
    return { id:eid, color:(e.from===id||e.to===id)?'rgba(255,255,255,0.85)':'rgba(200,200,200,0.04)' }; }));
  refreshLabels();               // hide the faded nodes' labels, keep the neighbourhood's
}
function clearHighlight(){ focusId=null; focusKeep=new Set(); applyCommunitySelect(); refreshLabels(); }

function applyScale(){
  const scale = network.getScale() || 1;
  network.setOptions({
    nodes: { font:{ size:TARGET_FONT/scale, strokeWidth:4/scale }, borderWidth:BORDER },
    edges: { scaling:{ min:EDGE_MIN/scale, max:EDGE_MAX/scale } }
  });
}
function resize(){
  if(!ready) return;                 // don't touch node sizes before the first fit (avoids a zoom/size runaway)
  const scale = network.getScale() || 1;
  const rect = container.getBoundingClientRect();
  const c = network.DOMtoCanvas({ x:rect.width/2, y:rect.height/2 });
  const pos = network.getPositions();
  // label budget grows faster-than-linear as you zoom in
  const k = Math.min(order.length, Math.max(BASE, Math.round(BASE * Math.pow(scale/initScale, LABEL_ZOOM_EXP))));
  const upd = [];
  for(const id in pos){
    const dx=(pos[id].x-c.x)*scale, dy=(pos[id].y-c.y)*scale;   // offset from centre in screen px
    const g = Math.exp(-(dx*dx+dy*dy)/(2*FOCUS_R*FOCUS_R));     // 1 at centre -> 0 far away
    const mult = FOCUS_MIN + (FOCUS_MAX-FOCUS_MIN)*g;
    const show = wantLabel(id, k);                             // focus (hover/lock) overrides the zoom LOD
    const u = { id, size: baseSize[id]*mult/scale };
    if(shown[id] !== show){ u.label = show ? NAME[id] : ' '; shown[id] = show; }
    upd.push(u);
  }
  nodes.update(upd);
}

let raf = null;
function schedule(fn){ if(raf) return; raf=requestAnimationFrame(()=>{ raf=null; fn(); }); }
network.on('zoom', ()=>schedule(()=>{ applyScale(); resize(); }));
network.on('dragging', ()=>schedule(resize));   // the focus lens follows you as you pan
network.on('dragEnd', resize);
network.on('animationFinished', resize);
network.once('stabilizationIterationsDone', ()=>{
  network.setOptions({physics:false});
  network.fit({animation:{duration:700}});
  setTimeout(()=>{ initScale = network.getScale() || 1; ready = true; NODES.forEach(n=>shown[n.id]=null); applyScale(); resize(); }, 760);
});

// ---------- hover to preview a singer's connections; click to lock it ----------
network.on('hoverNode', p => { if(lockedNode === null) highlightNode(p.node); });
network.on('blurNode', () => { if(lockedNode === null) clearHighlight(); });
network.on('click', params => {
  if(params.nodes.length){
    const id = params.nodes[0];
    if(lockedNode === id){ lockedNode = null; clearHighlight(); }   // click the locked node again to release
    else { lockedNode = id; highlightNode(id); }                    // lock this node + its neighbours
  } else if(lockedNode !== null){ lockedNode = null; clearHighlight(); }  // click empty space to release
});
</script>
</body>
</html>'''


if __name__ == "__main__":
    build()
