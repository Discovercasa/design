# Step Inside (`plataforma_cliente`)

Visita 3D, AR e VR das casas DiscoverCasa. A especificação técnica v2 (2026-11-05) está nos documentos do projeto, no
hub. Trabalha-se uma fase de cada vez, em ramos `step-inside/<fase>-<tarefa>`.

| Pasta | Conteúdo |
|---|---|
| `docs/audit/current-architecture.md` | Fase 0: auditoria do sistema atual, riscos, ordem das fases, decisões |
| `docs/fase1/` | Fase 1: contrato de dados, matriz de formatos, resultados |
| `schema/fontes_projeto.schema.json` | O contrato de dados: cada valor da casa com origem e confiança |
| `ferramentas/inventario_workstation.ps1` | Inventário só de leitura de um PC candidato a workstation |
| `ferramentas/fontes/` | Catálogo de documentos, proveniência (`fontes.json`), relatório de faltas e conflitos |
| `projetos-teste/<obra>/` | Projetos de teste: catálogo, declarações à mão, `fontes.json`, relatório |
| `tests/` | `python -m unittest discover -s step-inside/tests` (a partir de `BOB/`) |

Os desenhos dos clientes nunca entram no Git (o repositório é público). Para os ler, as ferramentas usam a pasta
`desenhos/` da obra no PC.
