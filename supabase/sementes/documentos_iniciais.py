"""Documentos já partilhados com cada projeto (até 2026-11-05) → migração 0008 (as linhas da tabela documentos) e uma
lista local de carregamento (caminho no PC → caminho no armazenamento privado "documentos").

    python supabase/sementes/documentos_iniciais.py <pasta do BOB privado> <pasta Downloads> <saída da lista.json>

Os ficheiros não vão para o Git (desenhos de clientes): ficam só no armazenamento privado do Supabase, atrás da entrada
do Design. Este script só escreve os nomes e os tamanhos.
"""
import json, re, sys, unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
BOB_PC, DOWN, SAIDA = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
MIME = {".pdf": "application/pdf", ".md": "text/plain; charset=utf-8", ".dwfx": "model/vnd.dwfx+xps", ".dwg": "image/vnd.dwg",
        ".png": "image/png", ".webp": "image/webp"}


def chave(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z0-9._-]+", "-", t)
    return re.sub(r"-{2,}", "-", t).strip("-.")


def legivel(nome):
    base = Path(nome).stem.replace("_", " ").strip()
    return re.sub(r"\s{2,}", " ", base)


docs = []
def junta(projeto, tipo, ficheiro: Path, titulo, descricao, grupo):
    assert ficheiro.is_file(), ficheiro
    caminho = f"{projeto}/{tipo}/{grupo}__{chave(ficheiro.name)}"
    docs.append({"projeto": projeto, "tipo": tipo, "titulo": titulo[:200], "descricao": descricao, "caminho": caminho,
                 "nome": ficheiro.name, "tamanho": ficheiro.stat().st_size, "mime": MIME.get(ficheiro.suffix.lower(), ""),
                 "local": str(ficheiro)})

# Step Inside: a especificação técnica da plataforma 3D/AR/VR (2026-11-05)
junta("plataforma_cliente", "informativo", DOWN / "Discovercasa_Especificacao_Tecnica_Claude_Code_v2.md",
      "Especificação técnica e plano de implementação (v2)", "Pipeline documental → Blender → Unreal → 3D, AR e VR; fases 0–9; custos externos. Versão de trabalho em texto.", "especificacao")
junta("plataforma_cliente", "informativo", DOWN / "Discovercasa_Plano_Tecnico_Revisao_v2.pdf",
      "Plano técnico, revisão v2 (PDF)", "O mesmo conteúdo da especificação, paginado, com a revisão dos formatos de entrada e dos custos médios.", "plano")

# Build Your House: Smart Land, Smart Interiors e Conformidade (2026-11-05)
junta("build_your_house", "informativo", DOWN / "ESPECIFICACAO_CLAUDE_SMART_LAND_INTERIORES_CONFORMIDADE_PT.md",
      "Especificação Smart Land, Smart Interiors e Conformidade", "Terreno, implantação, conformidade municipal e interiores; fases 0–8. Versão de trabalho em texto.", "smart-land")
junta("build_your_house", "informativo", DOWN / "ESPECIFICACAO_CLAUDE_SMART_LAND_INTERIORES_CONFORMIDADE_PT.pdf",
      "Especificação Smart Land, Smart Interiors e Conformidade (PDF)", "O mesmo documento em PDF.", "smart-land")

# Builder: os desenhos das obras e as fontes do método (conhecimento para aprender como a Discovercasa constrói)
for f in sorted((BOB_PC / "Construção Torres Vedras" / "desenhos").iterdir()):
    junta("builder", "adicional", f, f"Torres Vedras · {legivel(f.name)} ({f.suffix[1:].upper()})",
          "Casa já construída: onde se aprende o método e se compara com os materiais realmente gastos.", "torres-vedras")
for f in sorted((BOB_PC / "Construção Sobral" / "desenhos").iterdir()):
    junta("builder", "adicional", f, f"Sobral · {legivel(f.name)} ({f.suffix[1:].upper()})",
          "Loteamento Sobral (16 casas e armazém): desenhos de projeto.", "sobral")
for f in sorted(p for p in (BOB_PC / "conhecimento" / "fontes").rglob("*") if p.is_file()):
    sub = f.parent.name if f.parent.name != "fontes" else ""
    junta("builder", "adicional", f, f"Método · {legivel(sub + ' ' + f.name if sub else f.name)}",
          "Fonte do sistema construtivo Discovercasa (rascunhos da empresa, fichas de produtos, fotografias de obra).", "metodo")

# Gerador: a planta de arquitetura de Torres Vedras com que foi feito e verificado
for nome in ("projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.dwfx", "projeto de arquitetura_geral F01.2_F01.3_F02.1_F03.1.pdf"):
    f = BOB_PC / "Construção Torres Vedras" / "desenhos" / nome
    junta("gerador", "adicional", f, f"Torres Vedras · planta de arquitetura ({f.suffix[1:].upper()})",
          "A planta com que o Gerador foi desenvolvido e testado.", "torres-vedras")

assert len({d["caminho"] for d in docs}) == len(docs), "caminhos repetidos"
q = lambda s: "'" + s.replace("'", "''") + "'"
linhas = ",\n".join(f"  ({q(d['projeto'])}, {q(d['tipo'])}, {q(d['titulo'])}, {q(d['descricao'])}, {q(d['caminho'])}, "
                    f"{q(d['nome'])}, {d['tamanho']}, {q(d['mime'])}, 'Equipa', '2026-11-05T12:00:00Z')" for d in docs)
sql = ("-- Documentos já partilhados com cada projeto até 2026-11-05 (gerado por supabase/sementes/documentos_iniciais.py).\n"
       "-- Os ficheiros estão no armazenamento privado \"documentos\"; aqui só os nomes. Corre uma vez, depois de 0006.\n"
       "insert into public.documentos (projeto, tipo, titulo, descricao, caminho, nome_ficheiro, tamanho, mime, criado_por_nome, criado_em) values\n"
       + linhas + ";\n")
(RAIZ / "supabase" / "migrations" / "0008_documentos_iniciais.sql").write_text(sql, encoding="utf-8")
SAIDA.write_text(json.dumps(docs, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(docs), "documentos;", round(sum(d["tamanho"] for d in docs) / 1e6, 1), "MB;",
      {p: sum(1 for d in docs if d["projeto"] == p) for p in sorted({d["projeto"] for d in docs})})
