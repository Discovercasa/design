"""Lê supabase/migrations/0005_hub_conteudo_inicial.sql e escreve tests/fixture.json com as mesmas linhas
(checkpoints, tarefas, decisões, opções) para a base simulada dos testes. Também confirma que cada chamada tem
argumentos válidos (uma gralha no SQL aparece aqui antes de chegar ao Supabase).

    python tests/gerar_fixture.py
"""
import json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SQL = (RAIZ / "supabase" / "migrations" / "0005_hub_conteudo_inicial.sql").read_text(encoding="utf-8")


def partir(texto, sep):
    """Divide por `sep` fora de strings SQL ('...' com '' como aspa)."""
    partes, atual, dentro, i = [], [], False, 0
    while i < len(texto):
        ch = texto[i]
        if ch == "'":
            if dentro and i + 1 < len(texto) and texto[i + 1] == "'":
                atual.append("''"); i += 2; continue
            dentro = not dentro
        if ch == sep and not dentro:
            partes.append("".join(atual)); atual = []
        else:
            atual.append(ch)
        i += 1
    partes.append("".join(atual))
    return partes


def valor(a):
    a = a.strip()
    if a.lower() == "null": return None
    if a.startswith("'"): return a[1:-1].replace("''", "'")
    if re.fullmatch(r"-?\d+", a): return int(a)
    if a in ("c", "t", "d"): return ("var", a)
    raise ValueError(f"argumento inesperado: {a!r}")


corpo = SQL[SQL.index("do $$"):]
corpo = corpo[corpo.index("begin") + 5: corpo.rindex("end $$")]
corpo = "\n".join(l for l in corpo.splitlines() if not l.strip().startswith("--"))
db = {"checkpoints": [], "tarefas": [], "decisoes": [], "decisoes_opcoes": []}
var = {}
CRIADO = "2026-11-05T10:00:00Z"
for st in partir(corpo, ";"):
    st = st.strip()
    if not st: continue
    m = re.fullmatch(r"(?:([ctd])\s*:=\s*)?(?:perform\s+)?pg_temp\.(cp|tf|dc|op)\((.*)\)", st, re.S)
    if not m: sys.exit(f"instrução não reconhecida: {st[:80]}")
    alvo, fn, args = m.group(1), m.group(2), [valor(a) for a in partir(m.group(3), ",")]
    args = [var[a[1]] if isinstance(a, tuple) else a for a in args]
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

(RAIZ / "tests" / "fixture.json").write_text(json.dumps(db, ensure_ascii=False, indent=1), encoding="utf-8")
print({k: len(v) for k, v in db.items()})
