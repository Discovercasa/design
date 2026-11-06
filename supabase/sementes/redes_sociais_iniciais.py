"""Importa o planeamento dos posts do Excel "DiscoverCasa Post Mensal - publicações" (folha "Jul  Ago  Set 26":
julho a dezembro de 2026, 24 semanas) para as redes sociais do hub.

Escreve:
  supabase/migrations/0010_redes_sociais_inicial.sql   obras, fases, posts, fotos (linhas) e comentários
  tests/fixture_social.json                            as mesmas linhas para a base simulada dos testes
  <saida>/ficheiros/posts/…                            as fotos tiradas do Excel (ficam no PC, nunca no Git)
  <saida>/carregar_social.json                         a lista para carregar no armazenamento privado "social"

As miniaturas (<saida>/ficheiros/miniaturas/…, 640 px) fazem-se à parte (System.Drawing no Windows).

    python -I supabase/sementes/redes_sociais_iniciais.py "<Excel>.xlsx" "<pasta de saída>" [AAAA-MM-DD de hoje]
"""
import json, re, sys, unicodedata, zipfile
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "xdr": "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "pr": "http://schemas.openxmlformats.org/package/2006/relationships"}
FOLHA = "Jul  Ago  Set 26"
MESES = ["2026-07-01", "2026-08-01", "2026-09-01", "2026-10-01", "2026-11-01", "2026-12-01"]   # 4 semanas cada
LINHA_TITULO, LINHA_LEGENDA, LINHAS_FOTO = 4, 9, [14, 19, 24, 29, 34]                        # base 0, como no Excel

# Obras e fases (parte de baixo da folha). Os nomes das fases por extenso ("Mov" → Movimento de terras, "Bf" → Base
# de fundação); "Feito" → concluída; o resto fica prevista com o período escrito no Excel.
OBRAS = [
    ("Matosinhos", "", [("Movimento de terras", "concluida", "", 1, ""), ("Base de fundação", "concluida", "", 3, ""),
                        ("Estrutura", "prevista", "Julho - Ago", 2, ""), ("Acabamentos", "prevista", "Set - Dez", 2, "2 ou mais publicações.")]),
    ("Casa dos Cães", "3 publicações previstas (Mai - Ago).", []),
    ("Boelhe", "3 publicações previstas.", [("Movimento de terras", "concluida", "", None, ""), ("Base de fundação", "concluida", "", None, ""),
                                            ("Estrutura", "concluida", "", None, ""), ("Acabamentos", "prevista", "Junho", None, "")]),
    ("Ribamar", "", [("Projetos", "concluida", "", None, "Projetos de um gabinete parceiro."), ("Movimento de terras", "prevista", "Jun", None, ""),
                     ("Base de fundação", "prevista", "Jul - Ago", None, ""), ("Estrutura", "prevista", "Set - Out", None, ""),
                     ("Acabamentos", "prevista", "Nov - Fev", None, "")]),
    ("Gaia", "Aumento de uma casa já construída pela Discovercasa.", [("Aumento", "prevista", "Jul", None, "")]),
    ("Oliveira de Azeméis", "Testemunho de um cliente.", [("Garantia", "prevista", "Set", None, "")]),
    ("Lagos", "", [("Projetos", "concluida", "", None, ""), ("Movimento de terras", "prevista", "Nov ??", None, ""),
                   ("Base de fundação", "prevista", "Dez ??", None, ""), ("Estrutura", "prevista", "", None, ""), ("Acabamentos", "prevista", "", None, "")]),
    ("Sobral", "Loteamento com 16 habitações e 3 estruturas de apoio.", []),
    ("Torres Vedras", "Casa concluída.", []),
]
# título do post (como no Excel) → (obra, fase)
PREFIXOS = {"Sobral": "Sobral", "Boelhe": "Boelhe", "Torres Vedras": "Torres Vedras", "Matosinhos": "Matosinhos",
            "Cães": "Casa dos Cães", "Ribamar": "Ribamar", "Gaia": "Gaia"}
FASE_DO_TITULO = [(r"\bBF\b", "Base de fundação"), (r"\bEstrutura\b", "Estrutura"), (r"Mov", "Movimento de terras"), (r"Aumento", "Aumento"),
                  (r"Testemunho projetos", "Projetos")]


def ler_folha(z):
    ss = ["".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS)]
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    sh = next(s for s in wb.find("m:sheets", NS) if s.get("name") == FOLHA)
    caminho = "xl/" + rels[sh.get(f"{{{NS['r']}}}id")]
    root = ET.fromstring(z.read(caminho))
    cel = {}
    for c in root.iter(f"{{{NS['m']}}}c"):
        v = c.find("m:v", NS)
        txt = ss[int(v.text)] if c.get("t") == "s" and v is not None else (v.text if v is not None else None)
        if txt and txt.strip():
            ref = c.get("r"); letras = re.match(r"[A-Z]+", ref).group(0)
            col = 0
            for ch in letras: col = col * 26 + ord(ch) - 64
            cel[(int(ref[len(letras):]) - 1, col - 1)] = txt
    # imagens: âncora (linha, coluna) → ficheiro em xl/media
    pasta, nome = caminho.rsplit("/", 1)
    srels = {r.get("Id"): r for r in ET.fromstring(z.read(f"{pasta}/_rels/{nome}.rels"))}
    desenho = next(r.get("Target") for r in srels.values() if r.get("Type").endswith("/drawing")).replace("../", "xl/")
    dpasta, dnome = desenho.rsplit("/", 1)
    drels = {r.get("Id"): r.get("Target").replace("../", "xl/") for r in ET.fromstring(z.read(f"{dpasta}/_rels/{dnome}.rels"))}
    imgs = {}
    for anc in ET.fromstring(z.read(desenho)):
        fr, blip = anc.find("xdr:from", NS), anc.find(".//a:blip", NS)
        if fr is None or blip is None: continue
        imgs[(int(fr.find("xdr:row", NS).text), int(fr.find("xdr:col", NS).text))] = drels[blip.get(f"{{{NS['r']}}}embed")]
    return cel, imgs


def medidas_jpeg(b):
    i = 2
    while i < len(b):
        if b[i] != 0xFF: i += 1; continue
        m = b[i + 1]
        if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            return int.from_bytes(b[i + 7:i + 9], "big"), int.from_bytes(b[i + 5:i + 7], "big")
        i += 2 + int.from_bytes(b[i + 2:i + 4], "big")
    return None, None


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", t)).strip("-")[:40] or "post"


def q(v):
    if v is None: return "null"
    if isinstance(v, bool): return "true" if v else "false"
    if isinstance(v, int): return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    xlsx, saida = Path(sys.argv[1]), Path(sys.argv[2])
    hoje = sys.argv[3] if len(sys.argv) > 3 else date.today().isoformat()
    z = zipfile.ZipFile(xlsx)
    cel, imgs = ler_folha(z)
    (saida / "ficheiros" / "posts").mkdir(parents=True, exist_ok=True)
    (saida / "ficheiros" / "miniaturas").mkdir(parents=True, exist_ok=True)

    fx = {"obras": [], "obras_fases": [], "posts": [], "posts_media": [], "posts_comentarios": []}
    CRIADO = "2026-11-06T09:00:00Z"
    fase_id = {}
    for i, (nome, desc, fases) in enumerate(OBRAS, 1):
        fx["obras"].append({"id": i, "nome": nome, "descricao": desc, "ativa": True, "ordem": i, "criado_por": None, "criado_por_nome": "Equipa", "criado_em": CRIADO})
        for j, (fn, est, per, n, notas) in enumerate(fases, 1):
            fid = len(fx["obras_fases"]) + 1
            fase_id[(nome, fn)] = fid
            fx["obras_fases"].append({"id": fid, "obra_id": i, "nome": fn, "ordem": j, "estado": est, "periodo": per, "posts_previstos": n,
                "fotos": "por_tirar", "visita_em": None, "fotos_em": None, "notas": notas, "concluida_em": None,
                "criado_por": None, "criado_por_nome": "Equipa", "criado_em": CRIADO})
    obra_id = {o["nome"]: o["id"] for o in fx["obras"]}

    # notas tiradas das linhas das fotos (texto em vez de imagem) e legendas alternativas
    notas_extra = {}
    for (r, c), t in cel.items():
        if r in LINHAS_FOTO and c >= 2 and (r, c) not in imgs:
            semana = (c - 2) // 2 + 1
            if t.strip().startswith(("Estamos", "Nos bastidores")) or len(t) > 200: continue
            notas_extra.setdefault(semana, []).append(f"Foto {LINHAS_FOTO.index(r) + 1}: {t.strip()}")
    alternativas = [cel[(r, 2)].strip() for r in (34, 40) if (r, 2) in cel and len(cel[(r, 2)]) > 200]

    lista_carregar, comentarios_por_celula = [], {}
    for semana in range(1, 25):
        col = 2 + (semana - 1) * 2
        titulo = cel.get((LINHA_TITULO, col), "").strip()
        if not titulo: continue
        legenda = cel.get((LINHA_LEGENDA, col), "").strip()
        mes = MESES[(semana - 1) // 4]; s_mes = (semana - 1) % 4 + 1
        prefixo = next((k for k in PREFIXOS if titulo.startswith(k)), None)
        obra = PREFIXOS.get(prefixo) if prefixo else ("Oliveira de Azeméis" if "Oliveira" in titulo else None)
        fase = None
        if obra:
            for padrao, fn in FASE_DO_TITULO:
                if re.search(padrao, titulo) and (obra, fn) in fase_id: fase = fn; break
            if obra == "Oliveira de Azeméis": fase = "Garantia"
        fotos = [(r, imgs[(r, col)]) for r in LINHAS_FOTO if (r, col) in imgs]
        # estado: as semanas que já passaram com legenda ficam publicadas; as seguintes com legenda e fotos esperam aprovação
        fim_semana = date.fromisoformat(mes).replace(day=min(28, s_mes * 7))
        passou = fim_semana.isoformat() < hoje
        # as semanas que passaram sem legenda não foram feitas
        estado = ("publicado" if passou else ("por_aprovar" if fotos else "rascunho")) if legenda else ("nao_feito" if passou else "ideia")
        notas = notas_extra.get(semana, [])
        if semana == 1 and alternativas:
            notas.append("Legendas alternativas que estavam no Excel:\n\n" + "\n\n— — —\n\n".join(alternativas))
        tipo = "video" if not fotos and ("Video" in titulo or "Testemunho" in titulo) else "carrossel"
        pid = len(fx["posts"]) + 1
        fx["posts"].append({"id": pid, "mes": mes, "semana": s_mes, "obra_id": obra_id.get(obra), "fase_id": fase_id.get((obra, fase)),
            "titulo": titulo, "tipo": tipo, "redes": ["instagram", "facebook"], "legenda": legenda, "notas": "\n".join(notas), "estado": estado,
            "legenda_aprovada": False, "legenda_aprovada_por_nome": "", "legenda_aprovada_em": None, "fotos_aprovadas": False,
            "fotos_aprovadas_por_nome": "", "fotos_aprovadas_em": None, "publicar_em": None, "publicado_em": None, "mes_original": None, "semana_original": None,
            "criado_por": None, "criado_por_nome": "Equipa", "criado_em": CRIADO, "atualizado_em": CRIADO, "_obra": obra, "_fase": fase})
        for k, (r, media) in enumerate(fotos, 1):
            b = z.read(media)
            base = f"{mes[:7]}-s{s_mes}-f{k}__{slug(titulo)}"
            caminho, mini = f"posts/{base}.jpg", f"miniaturas/{base}.jpg"
            (saida / "ficheiros" / caminho).write_bytes(b)
            w, h = medidas_jpeg(b)
            mid = len(fx["posts_media"]) + 1
            fx["posts_media"].append({"id": mid, "post_id": pid, "caminho": caminho, "miniatura": mini, "nome_ficheiro": f"{slug(titulo)}-{k}.jpg",
                "mime": "image/jpeg", "tamanho": len(b), "largura": w, "altura": h, "ordem": k, "criado_por": None, "criado_por_nome": "Equipa", "criado_em": CRIADO})
            lista_carregar += [{"caminho": caminho, "local": str(saida / "ficheiros" / caminho), "mime": "image/jpeg"},
                               {"caminho": mini, "local": str(saida / "ficheiros" / mini), "mime": "image/jpeg"}]
            comentarios_por_celula[(r, col)] = (pid, mid)
        for r in LINHAS_FOTO: comentarios_por_celula.setdefault((r, col), (pid, None))

    # comentários do Excel (sem os nomes de quem os escreveu: o repositório é público)
    for ref, textos, resolvido in [("K30", ["já vi e está top"], False), ("M15", ["enviado ao cliente, à espera de aprovação"], False),
                                   ("O25", ["consegues tirar aquele saco?", "imagina eu conseguir consigo com ai mas a imagem perde muita qualidade"], True)]:
        letras = re.match(r"[A-Z]+", ref).group(0); col = sum((ord(ch) - 64) * 26 ** i for i, ch in enumerate(reversed(letras))) - 1
        pid, mid = comentarios_por_celula[(int(ref[len(letras):]) - 1, col)]
        for t in textos:
            fx["posts_comentarios"].append({"id": len(fx["posts_comentarios"]) + 1, "post_id": pid, "media_id": mid, "texto": t, "resolvido": resolvido,
                                           "autor_id": None, "autor_nome": "Equipa", "criado_em": CRIADO})

    # ---------------------------------------------------------------- SQL
    L = ["-- Redes sociais: o planeamento que estava no Excel \"DiscoverCasa Post Mensal - publicações\" (folha \"Jul  Ago  Set 26\":",
         "-- julho a dezembro de 2026). Gerado por supabase/sementes/redes_sociais_iniciais.py; corre uma vez, depois de 0009.",
         f"-- Estados: semanas já passadas com legenda = publicado, sem legenda = não feito; seguintes com legenda e fotos = por",
         f"-- aprovar (hoje = {hoje}).",
         "-- As fotos ficam no armazenamento privado \"social\" (carregadas à parte); aqui só as linhas.", ""]
    L.append("insert into public.obras (nome, descricao, ordem, criado_por_nome) values")
    L.append(",\n".join(f"  ({q(o['nome'])}, {q(o['descricao'])}, {o['ordem']}, 'Equipa')" for o in fx["obras"]) + ";")
    L.append("")
    L.append("insert into public.obras_fases (obra_id, nome, ordem, estado, periodo, posts_previstos, notas, criado_por_nome) values")
    L.append(",\n".join(f"  ((select id from public.obras where nome = {q(fx['obras'][f['obra_id'] - 1]['nome'])}), {q(f['nome'])}, {f['ordem']}, "
                        f"{q(f['estado'])}, {q(f['periodo'])}, {q(f['posts_previstos'])}, {q(f['notas'])}, 'Equipa')" for f in fx["obras_fases"]) + ";")
    L.append("")
    for p in fx["posts"]:
        obra = f"(select id from public.obras where nome = {q(p['_obra'])})" if p["_obra"] else "null"
        fase = (f"(select f.id from public.obras_fases f join public.obras o on o.id = f.obra_id where o.nome = {q(p['_obra'])} and f.nome = {q(p['_fase'])})"
                if p["_fase"] else "null")
        L.append(f"insert into public.posts (mes, semana, obra_id, fase_id, titulo, tipo, legenda, notas, estado, criado_por_nome) values\n"
                 f"  ({q(p['mes'])}, {p['semana']}, {obra}, {fase}, {q(p['titulo'])}, {q(p['tipo'])},\n  {q(p['legenda'])},\n  {q(p['notas'])}, {q(p['estado'])}, 'Equipa');")
    L.append("")
    post_sql = lambda pid: (lambda p: f"(select id from public.posts where mes = {q(p['mes'])} and semana = {p['semana']} and titulo = {q(p['titulo'])})")(fx["posts"][pid - 1])
    L.append("insert into public.posts_media (post_id, caminho, miniatura, nome_ficheiro, mime, tamanho, largura, altura, ordem, criado_por_nome) values")
    L.append(",\n".join(f"  ({post_sql(m['post_id'])}, {q(m['caminho'])}, {q(m['miniatura'])}, {q(m['nome_ficheiro'])}, 'image/jpeg', {m['tamanho']}, "
                        f"{q(m['largura'])}, {q(m['altura'])}, {m['ordem']}, 'Equipa')" for m in fx["posts_media"]) + ";")
    L.append("")
    L.append("insert into public.posts_comentarios (post_id, media_id, texto, resolvido, autor_nome) values")
    L.append(",\n".join(f"  ({post_sql(c['post_id'])}, {('(select id from public.posts_media where caminho = ' + q(fx['posts_media'][c['media_id'] - 1]['caminho']) + ')') if c['media_id'] else 'null'}, "
                        f"{q(c['texto'])}, {q(c['resolvido'])}, 'Equipa')" for c in fx["posts_comentarios"]) + ";")
    (RAIZ / "supabase" / "migrations" / "0010_redes_sociais_inicial.sql").write_text("\n".join(L) + "\n", encoding="utf-8")

    for p in fx["posts"]: p.pop("_obra"); p.pop("_fase")
    (RAIZ / "tests" / "fixture_social.json").write_text(json.dumps(fx, ensure_ascii=False, indent=1), encoding="utf-8")
    (saida / "carregar_social.json").write_text(json.dumps(lista_carregar, ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: len(v) for k, v in fx.items()}, "ficheiros:", len(lista_carregar))
    for p in fx["posts"]:
        print(f"  {p['mes'][:7]} S{p['semana']} {p['estado']:<11} {len([m for m in fx['posts_media'] if m['post_id'] == p['id']])} fotos  {p['titulo']}")


if __name__ == "__main__":
    main()
