let e=null;async function t(){let t=performance.now(),{loadPyodide:n}=await import(
/* @vite-ignore */
new URL(`/configurador/pyodide/pyodide.mjs`,self.location.origin).href);e=await n({indexURL:new URL(`/configurador/pyodide/`,self.location.origin).href});let r=await(await fetch(`/configurador/motor/lista.json`)).json();try{e.FS.mkdir(`/motor`)}catch{}for(let t of r){let n=await(await fetch(`/configurador/motor/${t}`)).text(),r=t.split(`/`),i=`/motor`;for(let t of r.slice(0,-1)){i+=`/${t}`;try{e.FS.mkdir(i)}catch{}}e.FS.writeFile(`/motor/${t}`,n)}return e.runPython(`
import sys, json
sys.path.insert(0, "/motor")
from ferramentas.configurador.para_construtor import converter, lados as lados_conv
from ferramentas.modelo.casa_planta import construir, niveis_teto
from ferramentas.modelo.camadas import fundir, teto_sob_anel
from ferramentas.modelo import camadas as CM
from ferramentas.modelo import telhado as TL
S0 = json.load(open("/motor/ferramentas/modelo/sistema_construtivo.json", encoding="utf-8"))

def telhado_casa(casa_json):
    # the exposed roof's faces at their heights, quick (no structure): the same telhado.py the builder uses
    casa = json.loads(casa_json)
    planta, cfg, notas = converter(casa, S0)
    C = cfg["cobertura"]
    if C.get("tipo") != "a_vista":
        return json.dumps({"faces": None})
    S = teto_sob_anel(fundir(S0, cfg.get("camadas") or {}), cfg)
    E = fundir(S["estrutura"], {k: v for k, v in (cfg.get("estrutura") or {}).items() if k != "sistema"})
    z_e = niveis_teto(cfg, S, E)[4]
    T = TL.telhado(cfg["fundacao"]["contorno"], C["forma"], C["inclinacao_graus"], C["beirado"], C["empena"])
    faces = [{"pts": f["pts"], "z0": f["z0"] + z_e, "gx": f["gx"], "gy": f["gy"], "subida": f["subida"]} for f in T["faces"]]
    return json.dumps({"faces": faces, "z_beirado": z_e, "z_max": z_e + T["z_max"]})

def construir_casa(casa_json):
    casa = json.loads(casa_json)
    planta, cfg, notas = converter(casa, S0)
    S = teto_sob_anel(fundir(S0, cfg.get("camadas") or {}), cfg)
    E = fundir(S["estrutura"], {k: v for k, v in (cfg.get("estrutura") or {}).items() if k != "sistema"})
    G, resumo = construir(cfg, S, E, planta)
    # the openings the divider moved (a pier between two windows), back in the client's terms: side, centre
    ls = lados_conv(cfg["fundacao"]["contorno"])
    movidas = []
    for m in G.get("aberturas_movidas", []):
        k = int(m["parede"][1:]) - 1
        if k >= len(ls):
            continue  # an interior wall's door
        l = ls[k]
        p0 = l["p0"][0] if l["eixo"] == "x" else l["p0"][1]
        movidas.append({"lado": k, "de": round((sum(m["de"]) / 2 - p0) * l["sentido"], 4),
                        "para": round((sum(m["para"]) / 2 - p0) * l["sentido"], 4)})
    return json.dumps({"G": G, "resumo": resumo, "notas": notas, "rodada": bool(casa.get("_rodada")) or any("rodada" in n for n in notas),
                       "materiais": S0["materiais"], "movidas": movidas}, ensure_ascii=False)

def cobertura_casa(casa_json):
    # the roof as built (camadas.py, the builder's own layers): the hidden roof's slopes, gutters, downpipes, caps and
    # the parapets' top; the exposed roof's gutters, downpipes and trims (its panels: the quick faces above)
    casa = json.loads(casa_json)
    planta, cfg, notas = converter(casa, S0)
    S = teto_sob_anel(fundir(S0, cfg.get("camadas") or {}), cfg)
    E = fundir(S["estrutura"], {k: v for k, v in (cfg.get("estrutura") or {}).items() if k != "sistema"})
    G, resumo = construir(cfg, S, E, planta)
    C = CM.Casa(G)
    out, res = CM.Saida(), []
    (CM.cobertura_platibanda if C.platibanda else CM.cobertura_faces)(C, S, out, res)
    # the exposed panels are the quick faces (6.2); of the parapets' roof-side cladding (6.4.k) only its finish, the
    # last layer — the chapéus wrap it as built
    fim_ = f"6.4.{len(CM.camadas_platibanda(S))}"
    obj = [{"nome": o["nome"], "material": o["material"], "pecas": o["pecas"]} for o in out.objetos
           if o["colecao"] in ("6.3", fim_) or (o["colecao"] == "6.2" and C.platibanda)]
    Cc = cfg["cobertura"]  # the hidden roof's gutter side and the sides the client may choose (one água)
    return json.dumps({"objetos": obj, "z_platibanda": G["niveis"].get("platibanda"),
                       "rodada": bool(casa.get("_rodada")) or any("rodada" in n for n in notas),
                       "uma_agua": bool(Cc.get("uma_agua")), "caleira": Cc.get("lado_caleira"), "caleiras": Cc.get("lados_caleira", [])})

def teto_casa(casa_json):
    # the false ceiling as built (camadas.tetos, the builder's own layers): each room's Pladur on its steel profiles and
    # the perimeter angle, hung under the ceiling beams at the pé direito (user 2026-10-28: "O testo falso ainda não
    # aparece no builder e quero que isso seja possível de aparecer")
    casa = json.loads(casa_json)
    planta, cfg, notas = converter(casa, S0)
    S = teto_sob_anel(fundir(S0, cfg.get("camadas") or {}), cfg)
    E = fundir(S["estrutura"], {k: v for k, v in (cfg.get("estrutura") or {}).items() if k != "sistema"})
    G, resumo = construir(cfg, S, E, planta)
    C = CM.Casa(G)
    C.salas = {}
    for p in C.pisos:  # the rooms, as camadas.interior finds them
        grid, _pan, lista = CM.salas(C, p, S)
        C.salas[p] = (grid, lista)
    out, res = CM.Saida(), []
    CM.tetos(C, S, out, res)
    obj = [{"nome": o["nome"], "material": o["material"], "pecas": o["pecas"]} for o in out.objetos
           if o["colecao"] in ("5.2", "5.3", "5.4")]  # perfis, cantoneira, Pladur (not the réguas or the wool above)
    return json.dumps({"objetos": obj, "rodada": bool(casa.get("_rodada")) or any("rodada" in n for n in notas)})
`),performance.now()-t}self.onmessage=async n=>{let r=n.data;try{if(r.tipo===`carregar`){let n=await t();self.postMessage({tipo:`pronto`,ms:n,materiais:JSON.parse(e.runPython(`json.dumps(S0['materiais'])`)),regras:JSON.parse(e.runPython(`json.dumps({'inclinacao_min_avista_pct': S0['cobertura'].get('inclinacao_min_avista_pct', 15)})`))})}else if(r.tipo===`construir`){e||await t();let n=performance.now(),i=e.globals.get(`construir_casa`)(JSON.stringify(r.casa));self.postMessage({tipo:`estrutura`,dados:i,ms:performance.now()-n,pedido:r.pedido})}else if(r.tipo===`telhado`){e||await t();try{let t=JSON.parse(e.globals.get(`telhado_casa`)(JSON.stringify(r.casa)));self.postMessage({tipo:`telhado`,pedido:r.pedido,faces:t.faces,zBeirado:t.z_beirado,zMax:t.z_max})}catch(e){self.postMessage({tipo:`erro`,msg:e&&e.message?e.message:String(e),pedido:-r.pedido})}}else if(r.tipo===`cobertura`){e||await t();try{let t=JSON.parse(e.globals.get(`cobertura_casa`)(JSON.stringify(r.casa)));self.postMessage({tipo:`cobertura`,pedido:r.pedido,...t})}catch(e){self.postMessage({tipo:`erro`,msg:e&&e.message?e.message:String(e),pedido:-1e6-r.pedido})}}else if(r.tipo===`teto`){e||await t();try{let t=JSON.parse(e.globals.get(`teto_casa`)(JSON.stringify(r.casa)));self.postMessage({tipo:`teto`,pedido:r.pedido,...t})}catch(e){self.postMessage({tipo:`erro`,msg:e&&e.message?e.message:String(e),pedido:-2e6-r.pedido})}}}catch(e){let t=e&&e.message?e.message:e&&e.code?`erro de ficheiros (${e.code})`:JSON.stringify(e);self.postMessage({tipo:`erro`,msg:t,pedido:r.pedido})}};