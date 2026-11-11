"""Lê as migrações 0005, 0007, 0008 e 0012 e escreve tests/fixture.json com as mesmas linhas
(checkpoints, tarefas, decisões, opções) para a base simulada dos testes. Também confirma que cada chamada tem
argumentos válidos (uma gralha no SQL aparece aqui antes de chegar ao Supabase).

    python tests/gerar_fixture.py
"""
import json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MIG = RAIZ / "supabase" / "migrations"


def partir(texto, sep):
    """Divide por `sep` fora de strings SQL ('...' com '' como aspa)."""
    partes, atual, dentro, i, nivel = [], [], False, 0, 0
    while i < len(texto):
        ch = texto[i]
        if ch == "'":
            if dentro and i + 1 < len(texto) and texto[i + 1] == "'":
                atual.append("''"); i += 2; continue
            dentro = not dentro
        if not dentro and sep == "," and ch in "()":
            nivel += 1 if ch == "(" else -1
        if ch == sep and not dentro and nivel == 0:
            partes.append("".join(atual)); atual = []
        else:
            atual.append(ch)
        i += 1
    partes.append("".join(atual))
    return partes


def valor(a):
    a = a.strip()
    if a == "p": return "build_your_house"
    if a.lower() == "null": return None
    if a.startswith("'"): return a[1:-1].replace("''", "'")
    if re.fullmatch(r"-?\d+", a): return int(a)
    if a in ("c", "t", "d"): return ("var", a)
    raise ValueError(f"argumento inesperado: {a!r}")


def corpo_do(sql):
    c = sql[sql.index("do $$"):]
    c = c[c.index("begin") + 5: c.rindex("end $$")]
    c = "\n".join(l for l in c.splitlines() if not l.strip().startswith("--"))
    return re.sub(r"declare[^;]*;", "", c) if c.lstrip().startswith("declare") else c


db = {"checkpoints": [], "tarefas": [], "decisoes": [], "decisoes_opcoes": [], "documentos": []}
var = {}
CRIADO = "2026-11-05T10:00:00Z"
v7 = False   # as funções de 0007 têm outra assinatura

# 0012: procurar e mudar o que já existe (as chamadas encaixadas pg_temp.cpx/tx devolvem o id)
def cpx(p, titulo):
    return next(c["id"] for c in db["checkpoints"] if c["projeto"] == p and c["titulo"] == titulo)
def tx(p, titulo):
    return min(t["id"] for t in db["tarefas"] if t["projeto"] == p and t["titulo"] == titulo)
def abrir(p, ordem):
    for c in db["checkpoints"]:
        if c["projeto"] == p and c["ordem"] >= ordem: c["ordem"] += 1
def mudar(lista, i, **campos):
    next(x for x in db[lista] if x["id"] == i).update(campos)
def nota(t, tipo, texto):
    assert tipo in ("bug", "mudar", "fazer", "nota")
    tarefa = next(x for x in db["tarefas"] if x["id"] == t)
    db["tarefas_notas"].append({"id": len(db["tarefas_notas"]) + 1, "tarefa_id": t, "projeto": tarefa["projeto"], "tipo": tipo, "texto": texto,
        "resolvida": False, "resolvida_por_nome": "", "resolvida_em": None, "tarefa_criada_id": None, "autor_id": None, "autor_nome": "Equipa",
        "criado_em": CRIADO})
NOVAS = {"abrir": abrir, "cpx": cpx, "tx": tx, "nota": nota,
         "crit": lambda c, t: mudar("checkpoints", c, criterio_saida=t), "desc_cp": lambda c, t: mudar("checkpoints", c, descricao=t),
         "desc_t": lambda t, x: mudar("tarefas", t, descricao=x), "rev": lambda t: mudar("tarefas", t, revisao=True)}
def arg(a):
    m = re.fullmatch(r"\s*pg_temp\.(cpx|tx)\((.*)\)\s*", a, re.S)
    if m: return NOVAS[m.group(1)](*[valor(x) for x in partir(m.group(2), ",")])
    return valor(a)
def correr(corpo):
  for st in partir(corpo, ";"):
    st = st.strip()
    if not st: continue
    if st.startswith("p constant"): continue
    m = re.fullmatch(r"(?:([ctd])\s*:=\s*)?(?:perform\s+)?pg_temp\.(\w+)\((.*)\)", st, re.S)
    if not m: sys.exit(f"instrução não reconhecida: {st[:80]}")
    alvo, fn, args = m.group(1), m.group(2), [arg(a) for a in partir(m.group(3), ",")]
    args = [var[a[1]] if isinstance(a, tuple) else a for a in args]
    if fn in NOVAS:
        r = NOVAS[fn](*args)
        if alvo: var[alvo] = r
        continue
    if v7 and fn == "cp": args = args[:4] + ["por_fazer"]
    if v7 and fn == "tf": args = [args[0], args[1], "por_fazer", None] + args[2:]
    if v7 and fn == "op": args = args[:5]
    if fn == "cp":
        p, titulo, desc, ordem, estado, *resto = args
        assert estado in ("por_fazer", "em_curso", "concluido"), estado
        assert 2 <= len(titulo) <= 200
        novo = {"id": len(db["checkpoints"]) + 1, "projeto": p, "titulo": titulo, "descricao": desc, "ordem": ordem, "estado": estado,
                "concluido_em": resto[0] if resto else None, "criado_por": None, "criado_por_nome": "Equipa", "criado_em": CRIADO}
        db["checkpoints"].append(novo)
    elif fn == "tf":
        cpid, titulo, *r = args
        estado, dia, app, custo, desc = (r + ["por_fazer", None, None, "", ""][len(r):])[:5]
        assert estado in ("por_fazer", "em_curso", "bloqueada", "concluida"), estado
        assert 2 <= len(titulo) <= 300, titulo
        cp = db["checkpoints"][cpid - 1]
        ordem = 1 + max([t["ordem"] for t in db["tarefas"] if t["checkpoint_id"] == cpid] or [0])
        novo = {"id": len(db["tarefas"]) + 1, "checkpoint_id": cpid, "projeto": cp["projeto"], "titulo": titulo, "descricao": desc, "estado": estado,
                "responsavel_id": None, "responsavel_nome": "", "app_sugerida": app, "custo": custo, "ordem": ordem, "criado_por": None,
                "criado_por_nome": "Equipa", "criado_em": CRIADO, "concluida_em": dia if estado == "concluida" else None}
        db["tarefas"].append(novo)
    elif fn == "dc":
        p, tarefa, pergunta, contexto = args
        novo = {"id": len(db["decisoes"]) + 1, "projeto": p, "tarefa_id": tarefa, "pergunta": pergunta, "contexto": contexto, "estado": "aberta",
                "opcao_escolhida": None, "justificacao": "", "decidida_por": None, "decidida_por_nome": "", "decidida_em": None,
                "criado_por": None, "criado_por_nome": "Equipa", "criado_em": CRIADO}
        db["decisoes"].append(novo)
    else:
        d, titulo, vant, desv, *r = args
        custo, desc = (r + ["", ""][len(r):])[:2]
        ordem = 1 + len([o for o in db["decisoes_opcoes"] if o["decisao_id"] == d])
        novo = {"id": len(db["decisoes_opcoes"]) + 1, "decisao_id": d, "titulo": titulo, "descricao": desc, "vantagens": vant,
                "desvantagens": desv, "custo": custo, "ordem": ordem}
        db["decisoes_opcoes"].append(novo)
    if alvo: var[alvo] = novo["id"]

correr(corpo_do((MIG / "0005_hub_conteudo_inicial.sql").read_text(encoding="utf-8")))
# 0007: abre espaço (Preços reais 5 → 6, Pronto para clientes 6 → 7) e junta as fases do Smart Land / Interiores
for c in db["checkpoints"]:
    if c["projeto"] == "build_your_house" and c["ordem"] >= 5: c["ordem"] += 1
v7 = True
correr(corpo_do((MIG / "0007_byh_smart_land_interiores.sql").read_text(encoding="utf-8")))
# 0008: as linhas dos documentos
sql8 = (MIG / "0008_documentos_iniciais.sql").read_text(encoding="utf-8")
valores = sql8[sql8.index("values") + 6:].strip().rstrip(";")
linhas, nivel, atual, dentro = [], 0, [], False
for ch in valores:
    if ch == "'": dentro = not dentro
    if not dentro and ch == "(":
        nivel += 1
        if nivel == 1: atual = []; continue
    if not dentro and ch == ")":
        nivel -= 1
        if nivel == 0: linhas.append("".join(atual)); continue
    if nivel >= 1: atual.append(ch)
for l in linhas:
    a = [valor(x) for x in partir(l, ",")]
    db["documentos"].append({"id": len(db["documentos"]) + 1, "projeto": a[0], "tipo": a[1], "titulo": a[2], "descricao": a[3], "caminho": a[4],
        "nome_ficheiro": a[5], "tamanho": a[6], "mime": a[7], "criado_por": None, "criado_por_nome": a[8], "criado_em": a[9]})
# 0011: colunas novas; 0012: conteúdo do documento de hierarquia e as notas de revisão
for c in db["checkpoints"]: c["criterio_saida"] = ""
for t in db["tarefas"]: t["revisao"] = False
db["tarefas_notas"] = []
correr(corpo_do((MIG / "0012_conteudo_hierarquia_revisoes.sql").read_text(encoding="utf-8")))
for c in db["checkpoints"]: c.setdefault("criterio_saida", "")
# 0024: the sections that lived in the titles («Torres Vedras · …») become sections; documents get seccao_id and pasta
db["documentos_seccoes"] = []
for d in db["documentos"]:
    d.setdefault("pasta", ""); d.setdefault("lote", None); d.setdefault("seccao_id", None)
    if d["tipo"] in ("informativo", "adicional") and " · " in d["titulo"]:
        nome = d["titulo"].split(" · ")[0]
        s = next((s for s in db["documentos_seccoes"] if (s["projeto"], s["tipo"], s["nome"]) == (d["projeto"], d["tipo"], nome)), None)
        if s is None:
            s = {"id": len(db["documentos_seccoes"]) + 1, "projeto": d["projeto"], "tipo": d["tipo"], "nome": nome,
                 "ordem": sum(1 for x in db["documentos_seccoes"] if (x["projeto"], x["tipo"]) == (d["projeto"], d["tipo"])) + 1,
                 "criado_por": None, "criado_por_nome": "Claude", "criado_em": d["criado_em"]}
            db["documentos_seccoes"].append(s)
        d["seccao_id"] = s["id"]
        d["titulo"] = d["titulo"][len(nome) + 3:]
for t in db["tarefas"]: t.setdefault("revisao", False)
(RAIZ / "tests" / "fixture.json").write_text(json.dumps(db, ensure_ascii=False, indent=1), encoding="utf-8")
print({k: len(v) for k, v in db.items()})
