# Step Inside · Fase 0 — Arquitetura atual (auditoria)

**Data:** 2026-11-07. **Âmbito:** tarefas 46–51 do hub (checkpoint «Fase 0 · Auditoria do sistema atual»).
**Como foi feita:** só leitura. Não se mudou nada em produção: nem código publicado, nem base de dados (exceto o estado
das tarefas no hub), nem Cloudflare. Não se mostram segredos. Referência: especificação técnica v2 de 2026-11-05
(documento do projeto no hub), §13 Fase 0 e §17.

---

## 1. Resumo

- **O que existe hoje:**
  - o hub Design: site estático na Cloudflare Pages;
  - o Supabase «Design», no plano Free;
  - um motor em Python que lê DWFx e PDF vetorial e gera o modelo Blender sem interface, com um GLB simples;
  - o Build Your House e o gerador, que correm o mesmo motor no browser (Pyodide + three.js).
- **O que não existe:** Unreal, Pixel Streaming, R2, Workers, exportação FBX/USDZ, terreno, IDs estáveis de material,
  proveniência por campo.
- **Workstation atual:**
  - serve para o que se faz hoje (Blender, scripts, documentos);
  - não serve para o Unreal Engine 5: 4 núcleos, 16 GB DDR3, GTX 1050 Ti com 4 GB, Windows 10;
  - **pôr só uma GPU nova não resolve:** a plataforma Z97 tem no máximo 32 GB DDR3, PCIe 3.0 e não é suportada pelo
    Windows 11.
- **Supabase Free:**
  - pausa o projeto ao fim de 1 semana sem atividade;
  - tem 1 GB para ficheiros e 50 MB por ficheiro;
  - serve para os dados, mas não para os ficheiros 3D nem para links de clientes sem passar a Pro.
- **Problema encontrado fora do Step Inside:** há **5 desenhos de clientes no repositório público** (4 `.dwg` de Torres
  Vedras, incluindo o levantamento topográfico, e 1 `.skp` do Sobral). Isto vai contra a regra «os desenhos dos clientes
  ficam no PC». Ver §11 e §15.

## 2. Mapa da arquitetura atual

```text
 Documentos do cliente (DWFx, PDF vetorial; DWG só para ver)      ── ficam no PC (não no Git)
                 │
                 ▼
 Motor Python (BOB/ferramentas, só biblioteca padrão)
   leitor DWFx / PDF → planta_paredes.json + config.json → geometria G → camadas
                 │                                   │
                 │ (Blender 4.4, sem interface)      │ (o mesmo motor no browser: Pyodide)
                 ▼                                   ▼
 .blend + GLB (cores lisas) + quantidades.csv   Build Your House / gerador (three.js r186)
 + documentos PDF/CSV (Módulos, Cobertura, Listagem)
                 │
                 ▼
 Repositório GitHub Discovercasa/design (público) ── push para main ──► Cloudflare Pages
                                                                     design.discovercasa.pt
                                                                              │
                                    entrada pela conta do Hub (botão) ────────┤
                                                                              ▼
                                         Supabase «Design» (Free, eu-west-1): Auth, Postgres + RLS,
                                         Realtime, Storage privado (documentos, social, anexos)

 Não existe: Unreal · Pixel Streaming · GPU cloud · R2 · Workers · FBX/USDZ · terreno · links de cliente
```

## 3. Repositório, scripts e publicação (tarefa 46)

| Item | Estado encontrado |
|---|---|
| Repositório | `Discovercasa/design`, **público**, `main` = online, cerca de 23 MB, desde 2026-10-30 |
| Pastas | `public/` (site publicado), `BOB/` (conhecimento, ferramentas Python, código-fonte das apps), `supabase/migrations` (0001–0014) + `sementes/`, `tests/` (Playwright) |
| Publicação | Integração GitHub → Cloudflare Pages (cada commit tem o check «Cloudflare Pages»). Não há GitHub Actions, `wrangler.toml` nem Pages Functions. |
| Cabeçalhos | `public/_headers`: HSTS, `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy`. `public/_redirects`: `/configurador` → `/build-your-house/` |
| Compilação | `python BOB/ferramentas/construir_site.py` copia o motor para `public/build-your-house/motor` e `public/gerador/motor`. O BYH é compilado com Vite 8.2.4. O resultado compilado vai no commit. |
| Bibliotecas no browser | Por CDN: supabase-js 2.45.4 e gsap 3.15.0 (jsDelivr), Google Fonts. No próprio site: three.js 0.186.1 e Pyodide 314.0.7. O maior ficheiro é `pyodide.asm.wasm` com 9,6 MB, abaixo do limite de 25 MiB por ficheiro da Cloudflare Pages. |
| Segredos / variáveis | Nenhum `.env` no repositório (`.env*` está no `.gitignore`). A única chave no código é a publishable do Supabase (`public/js/design-core.js`). Não há segredos de build. |
| Service worker | Só serve para instalar como app: não guarda páginas em cache. |
| Testes | Playwright 1.64.1 com base de dados simulada. Não há CI. O 3D do BYH não tem testes; o fluxo completo do gerador só corre com um desenho local. |

## 4. Cloudflare (tarefa 47)

**Confirmado sem entrar na conta:**
- `design.discovercasa.pt` é um CNAME para o projeto Pages `design` (`*.pages.dev`), servido pela Cloudflare.
- **A zona DNS `discovercasa.pt` não está na Cloudflare.** Os nameservers são de um alojamento cPanel, por isso a
  Cloudflare só serve o projeto Pages. Isto tem duas consequências:
  - **Precisam da zona na Cloudflare** (ou de mudar o DNS): um Worker com domínio próprio e um bucket R2 com domínio
    público.
  - **Não precisam dela:** Pages Functions no próprio `design.discovercasa.pt`, e um bucket R2 privado com URLs
    assinados pelo endpoint S3. Chegam para os uploads e downloads do Step Inside (especificação §10.3).
- Limites da Cloudflare Pages (documentação da Cloudflare, atualizada a 2026-09-05):

  | Limite | Plano Free | Uso hoje |
  |---|---|---|
  | Builds por mês | 500 | |
  | Builds em simultâneo | 1 | |
  | Duração de um build | 20 min | |
  | Ficheiros por site | 20 000 | 94 |
  | Tamanho de um ficheiro | 25 MiB | |
  | Domínios por projeto | 100 | |
  | Tamanho do site | | 18 MB |

- **Workers Free:** 100 000 pedidos por dia e 10 ms de CPU por pedido.
- **R2** (documentação de 2026-10-30): 0,015 USD por GB-mês. Grátis por mês: 10 GB, 1 milhão de operações Classe A e
  10 milhões Classe B. A saída de dados é grátis.

**Falta (precisa de acesso de leitura à conta Cloudflare):** o plano da conta, se já existem Workers, R2, KV ou D1, o
uso real de builds e quem administra a conta. Esta tarefa fica fechada só com uma captura do painel ou com acesso de
leitura.

## 5. Supabase (tarefa 48)

| Item | Estado encontrado |
|---|---|
| Projeto | «Design», região eu-west-1, Postgres 17.11. Organização «Design», **plano Free**. |
| Uso | Base de dados: 13,9 MB de 500 MB. Storage: cerca de 73 MB de 1 GB. |
| Storage | 3 buckets privados com limite de 50 MB por ficheiro: `documentos` (41 ficheiros, 54 MB), `social` (102 ficheiros, 18,8 MB), `anexos` (vazio). |
| Auth | 3 utilizadores, só email. Entra-se pela conta do Hub (sem registo). O nível vem de `app_metadata.nivel` e é verificado por `pode_ver()` / `pode_editar()`. |
| Tabelas | 19, todas com RLS: sugestoes, sugestoes_comentarios, projetos, perfis, checkpoints, tarefas, tarefas_notas, decisoes, decisoes_opcoes, notificacoes, notificacoes_lidas, vistos, documentos, anexos, obras, obras_fases, posts, posts_media, posts_comentarios |
| Regras RLS | Seguem o modelo `(select public.pode_ver())` / `(select public.pode_editar())`. O autor pode apagar ou editar o que escreveu (comentários, notas, anexos). |
| Triggers | `*_antes` valida e carimba; `*_depois` cria as notificações. Não correm em SQL sem sessão (`auth.uid()` nulo). |
| Realtime | 14 tabelas |
| Funções | RPC `inserir_checkpoint`, `mover_checkpoint`, `acrescentar_opcao`, `definir_fases`. As duas últimas são SECURITY DEFINER e verificam `pode_editar()` por dentro. |
| Edge Functions | 1, `carregar-documentos-iniciais`, **desligada**: responde 410. Pode ser apagada. |
| Extensões | plpgsql, pg_stat_statements, uuid-ossp, pgcrypto, supabase_vault |
| Avisos do linter | (1) as 2 funções SECURITY DEFINER acima, que são intencionais e se protegem por dentro; (2) a proteção contra palavras-passe vazadas está desligada, mas não se usam palavras-passe (entra-se pelo Hub). |

**Quotas do plano Free que contam para o Step Inside** (supabase.com/pricing):
- 500 MB de base de dados, 1 GB de ficheiros, 5 GB de saída por mês e 50 MB por ficheiro;
- 200 ligações Realtime em simultâneo e 500 000 invocações de Edge Functions;
- **pausa ao fim de 1 semana sem atividade**.

O plano Pro custa a partir de 25 USD por mês: 8 GB de disco, 100 GB de ficheiros, 250 GB de saída e sem pausa.

**Para o Step Inside:**
- A tabela `projetos` é a dos 5 projetos internos do hub, não a das casas dos clientes. A tabela `obras` (redes sociais)
  já lista obras.
- Na Fase 6 é preciso decidir se as casas do Step Inside usam `obras` ou uma tabela nova. As versões, os ficheiros, os
  jobs, as sessões e os links ficam sempre em tabelas novas.
- Os ficheiros 3D vão para o R2, não para o Supabase Storage (§2.2 da especificação; aqui o limite de 1 GB decide).

## 6. Pipeline existente PDF/DWFx → Claude Code → Blender (tarefa 49)

**Entradas** (com as categorias da especificação):

| Formato | Categoria | Como é lido |
|---|---|---|
| DWFx | DIRECT | `BOB/ferramentas/dwfx/leitor.py`, só biblioteca padrão. As imagens das folhas são só para ver e só funcionam em Windows. |
| PDF vetorial (plot do AutoCAD) | DIRECT | `dwfx/leitor_pdf.py` dá os mesmos traços do DWFx. Um PDF digitalizado não dá geometria. |
| JSON do configurador | DIRECT | `ferramentas/configurador/para_construtor.py` |
| Desenhos de módulos da empresa ou do engenheiro (DWFx) | DIRECT | `modelo/modulos_dc.py`, `modelo/extrair_casa.py` |
| DWG | CONVERT_REQUIRED | O gerador pede para exportar para PDF ou DWFx. Não há leitor. |
| DXF, IFC | UNSUPPORTED | Não há leitor. |
| Imagens, fotos, SketchUp `.skp` | REFERENCE_ONLY | Não se tira geometria delas. |

**Como a planta é lida:**
- A leitura depende das convenções do desenho: traço vermelho para as paredes, azul para os vidros e magenta para as
  aberturas das portas.
- A escala é deduzida (1:50, 1:100 ou 1:200).
- **Só funciona com paredes ortogonais.**
- A partir de uma planta só se faz 1 piso. Dois pisos só a partir dos desenhos do engenheiro.

**Representações intermédias:**
- **Planta** (`planta_paredes.json`): paredes por eixo com as aberturas. A origem do desenho fica registada (ficheiro,
  folha, escala), mas as alturas dos vãos não estão no desenho.
- **Configuração** (`config.json`): o ficheiro que se edita. Tem níveis, aberturas, cobertura, estrutura e camadas.
- **Norma da empresa** (`modelo/sistema_construtivo.json`): as camadas de cada elemento e 39 materiais pelo nome
  português, só com cor e rugosidade.
- **Geometria G** (`casa_planta.py`, `estrutura_dc.py`, `extrair_casa.py`) e depois `camadas.py`.
- **Proveniência:** só existe ao nível do ficheiro e em notas («assumido», avisos). **Não há proveniência nem confiança
  por campo** (CONFIRMED / INFERRED / MISSING / NEEDS_HUMAN_REVIEW). Por exemplo, as alturas dos vãos vêm de valores
  por omissão e a escala é deduzida.

**Blender:**
- Comando: `ferramentas/modelo/construir_casa.py <config.json>`, cerca de 35 s por casa.
- Blender sem interface (`--background --factory-startup`). É usada a versão mais baixa instalada, ≥ 4.4.
- Metros, X para este, Y para norte, Z para cima a partir do topo da laje. **Origem local, sem georreferência.**
- **Collections numeradas em português** («1 Estrutura de madeira», «2 …», …) e um Empty por módulo, com o nome dos
  desenhos. As peças levam propriedades: secção, tipo, comprimento e volume; as camadas levam produto, área e unidade.
- **Materiais:** Principled BSDF só com cor base e rugosidade, criados pelo nome. **Sem texturas, sem UVs, sem IDs
  estáveis.**
- **Saídas:**
  - `.blend`;
  - GLB da estrutura e GLB da casa completa (`export_scene.gltf`, só a opção de acabamento visível);
  - `quantidades.csv`;
  - pré-visualizações Workbench;
  - documentos PDF/CSV (`documentos/gerar.py`, sem Blender).
- **Validação:** `blender/validar.py` (tem de dar `issues: 0`), `modelo/verificar.py` (choques e peças fora do
  contorno), `configurador/auditar_cobertura.py --formas`.

**No browser** (Build Your House e gerador):
- O mesmo motor Python corre em Pyodide 314.0.7 (Python 3.14) num Web Worker, e o 3D é desenhado com three.js r186.
- As texturas do BYH são procedimentais e separadas dos materiais do Blender.
- Nenhuma das duas apps exporta GLB, e não há WebXR.

**Terreno:**
- Não existe modelo de terreno. O BYH tem um plano plano e o Blender só uma laje indicativa.
- O levantamento topográfico de Torres Vedras existe em DWG, mas não está lido.

**Tamanho por casa hoje:**
- desenhos: cerca de 7,5 MB (Torres Vedras, DWG);
- modelos: cerca de 5,4 MB (`.blend` 0,6 MB + GLB 1,1 e 3,8 MB).

Muito abaixo dos 8–15 GB por casa previstos para o Step Inside, que vêm sobretudo das texturas e do conteúdo Unreal.

## 7. O que funciona e o que é protótipo

| Componente | Estado |
|---|---|
| Leitor DWFx / PDF vetorial | Funcional, usado em casas reais (Torres Vedras, Sobral) |
| Modelo Blender + quantidades + documentos | Funcional. Torres Vedras: Módulos aprovado; Cobertura e Listagem de material em revisão. O `.blend` publicado é anterior à última correção do motor (reconstrução pendente). Sobral Tipo 1: 0 erros (obra parada). |
| Build Your House / gerador | Protótipos publicados atrás do login desde 2026-10-30 |
| Hub (tarefas, decisões, documentos, notificações, redes sociais) | Funcional, em uso |
| Exportações para visualização (FBX, USDZ, GLB com texturas, manifest) | Não existem |
| Unreal, Pixel Streaming, GPU, R2, links de cliente, AR, VR | Não existem |

## 8. Workstation (tarefa 50)

O inventário é do computador onde esta auditoria correu. **Falta confirmar que é a workstation que se quer usar.**

| Peça | Encontrado | UE 5.8, recomendado pela Epic | Especificação §6.2 |
|---|---|---|---|
| CPU | Intel i7-4790K, 4 núcleos / 8 threads (2014) | 4 núcleos a 2,5 GHz | «plataforma moderna, vários núcleos» |
| RAM | 16 GB DDR3-1600 (2 × 8 GB); a motherboard aceita no máximo 32 GB | 32 GB | 64 GB |
| GPU | NVIDIA GTX 1050 Ti, 4 GB, driver 560.94; sem ray tracing por hardware | 8 GB ou mais, DirectX 12. Para o Lumen com ray tracing por hardware: RTX 2000 ou mais recente | RTX 5070 Ti 16 GB no mínimo |
| Disco | SSD SATA de 1 TB (C:, 445 GB livres) + **disco USB externo de 4 TB (D:)**, onde está a pasta de trabalho | — | NVMe de 2 TB + 4 TB |
| Motherboard | Gigabyte Z97X-Gaming 7 (PCIe 3.0, DDR3) | — | — |
| Sistema | Windows 10 Home 22H2 | Windows 11 | Windows 11 |

**Software instalado:**
- **3D e render:** Blender 4.4 e 5.2.2, SketchUp 2025, Enscape 4.16, Chaos (Cloud Client, Envision, Cosmos), D5 Render
  3.0, Autodesk DWG TrueView 2026 e Design Review.
- **VR:** Meta Horizon Link 1.103 (software para ligar um Meta Quest ao PC).
- **Desenvolvimento:** Python 3.12.10, Node 24.18, git 2.54, GitHub CLI 2.96, VS Code.
- **Não instalado:** Unreal, Epic Games Launcher, Visual Studio (é preciso para compilar projetos Unreal com código) e
  wrangler.

**Conclusão:**
- Este PC serve para o que já se faz (Blender, scripts, documentos), mas **não para o Unreal Editor nem para o cook**.
- **Não se recomenda comprar só uma GPU para este PC:**
  - a motherboard fica limitada a 32 GB DDR3 e PCIe 3.0;
  - o CPU de 4.ª geração não é suportado pelo Windows 11;
  - o suporte do Windows 10 pela Microsoft terminou em 2025-10-14.
- As opções são uma workstation nova, como na §6.2, ou começar as Fases 4 e 5 numa GPU cloud de teste. Qualquer das duas
  só com autorização.
- **Atenção:** a pasta de trabalho está num disco USB externo. É lento para caches do Unreal, e falta confirmar onde
  ficam as cópias de segurança.
- **Não se lê por software:** a fonte de alimentação (W) e o tamanho da caixa. Só interessam se se mantiver este PC.

## 9. Dependências e versões

| Componente | Versão |
|---|---|
| Python (ferramentas) | ≥ 3.10, só biblioteca padrão; 3.12.10 neste PC |
| Blender | ≥ 4.4 (4.4 e 5.2.2 instalados; as ferramentas usam a 4.4) |
| Pyodide (browser) | 314.0.7 (Python 3.14.2) |
| three.js | 0.186.1 |
| Vite (BYH) | 8.2.4 |
| supabase-js | 2.45.4 (CDN) |
| gsap | 3.15.0 (CDN) |
| Playwright | 1.64.1 |
| Node | 24.18 neste PC |
| Postgres (Supabase) | 17.11 |
| Unreal Engine / Pixel Streaming | **não instalado**. A versão atual da documentação é a 5.8; fixá-la é a tarefa 66 |

## 10. Inventário de dados

| Dados | Onde | Notas |
|---|---|---|
| Desenhos dos clientes (DWFx, PDF, DWG) | PC (`desenhos/`), **5 ficheiros também no Git público** | ver §11 |
| Planta, configuração, norma da empresa | Git (`BOB/…`) | JSON pequenos |
| Modelos `.blend` / GLB / CSV | Git (`Construção */modelos/`) | cerca de 5 MB por casa |
| Documentos dos projetos (especificações, desenhos de referência) | Supabase Storage `documentos` (privado) | 41 ficheiros, 54 MB |
| Fotos das redes sociais | Supabase Storage `social` (privado) | 102 ficheiros, 18,8 MB |
| Tarefas, decisões, notificações, obras, posts | Supabase Postgres | 13,9 MB |
| Utilizadores | Supabase Auth (vindos do Hub) | 3, só email |

## 11. Mapa de riscos

| # | Risco | Impacto | Ação proposta |
|---|---|---|---|
| R1 | **5 desenhos de clientes no repositório público** desde 2026-10-30 (`*.dwg` e `*.skp` não estão no `.gitignore`) | Alto: dados de clientes expostos | Tirá-los do Git já (ficam no PC) e acrescentar `*.dwg`/`*.skp` ao `.gitignore`. Apagá-los também do histórico obriga a reescrever o histórico público: decisão à parte. |
| R2 | A workstation não corre o UE5 | Alto para as Fases 4–5 | Decidir: workstation nova ou GPU cloud de teste (§15) |
| R3 | Supabase Free: pausa ao fim de 1 semana sem atividade, 1 GB de ficheiros | Médio agora; alto com links de clientes | Pro (25 USD/mês) antes de haver links de clientes; ficheiros 3D no R2 |
| R4 | A zona DNS não está na Cloudflare | Médio: limita Workers e R2 com domínio próprio | Usar Pages Functions + R2 privado com URLs assinados; mudar o DNS só se for preciso |
| R5 | Sem proveniência nem confiança por campo; alturas por omissão; escala deduzida | Médio: vai contra a regra 9 (não inventar) | Fase 1: uma camada de proveniência por cima da planta e da configuração, sem reescrever o motor |
| R6 | Materiais sem IDs, texturas nem UVs | Médio para as Fases 3–4 | Fase 3: tabela de correspondência material → `MAT_*` no momento de exportar |
| R7 | Collections em português e numeradas, não semânticas | Baixo | Mapear para `ARCH_*`/`SITE_*` ao exportar; o modelo de produção fica como está |
| R8 | Sem terreno, CRS nem cotas de controlo | Médio para a Fase 2 | Ler o levantamento topográfico (DWG → DXF/PDF); pedir DEM ou levantamento por obra |
| R9 | Só paredes ortogonais; 1 piso a partir de planta | Médio: limita projetos de outros arquitetos | Registar na matriz de formatos (Fase 1); alargar depois |
| R10 | Trabalho num disco USB externo; cópias de segurança por confirmar | Médio | Confirmar as cópias; o Git cobre só o que não é dos clientes |
| R11 | Sem CI; 3D não testado | Baixo/médio | Testes por fase, como pede a especificação |
| R12 | Licença do Unreal por confirmar com a Epic | Alto antes de vender | Já é a tarefa 93 |

## 12. O que se reutiliza sem custo

- **Hub + Supabase:** entrada pelo Hub, RLS, Realtime, notificações, documentos, decisões. Chegam para projetos, jobs,
  estado e links. Não se cria um segundo portal nem uma segunda base de dados.
- **Leitores DWFx/PDF + motor + Blender sem interface + exportação GLB:** são a base das exportações da Fase 3.
- **Visualizador three.js do BYH e do gerador:** serve de base ao «Visualizador 3D para quem não tem AR» (tarefa 85) e à
  pré-visualização dos GLB.
- **Pages Functions** no `design.discovercasa.pt`, grátis até ao limite dos Workers: servem para emitir URLs assinados do
  R2 sem mexer no DNS.
- **Enscape, Chaos e D5 já instalados:** servem de referência de qualidade na aprovação visual (tarefa 71).
- **Meta Horizon Link instalado:** se a empresa tem um Meta Quest, é o candidato natural a headset de referência
  (tarefa 86).

## 13. Alterações mínimas propostas

Nenhuma destas alterações está feita. Cada uma espera aprovação.

1. Tirar do Git os 5 desenhos de clientes e ignorar `*.dwg`/`*.skp` (R1).
2. Fase 1, sem custos: definir o schema com proveniência e confiança por campo como camada por cima de
   `planta_paredes.json` e `config.json`.
3. Fases 2–3, sem custos: exportação para visualização separada da exportação de produção, com collections semânticas,
   `MAT_*` estáveis, texturas e UVs, GLB e USDZ (o Blender exporta USDZ) e `manifest.json` com SHA-256.
4. Supabase: tabelas novas só na Fase 6. Até lá nada de ficheiros 3D no Supabase.
5. Apagar a Edge Function desligada `carregar-documentos-iniciais` (opcional).
6. Workstation: não comprar só uma GPU para este PC (§8).

## 14. Proposta de ordem das fases

**Fases 1 → 2 → 3, já, a 0 €:** correm neste PC só com Python e Blender.

**Sugestão nossa: a Fase 7 (AR) logo a seguir à 3, antes das Fases 4–5 (Unreal e Pixel Streaming):**
- O AR precisa só de GLB/USDZ leves e do telemóvel do cliente: sem GPU, sem Unreal, sem custo por sessão.
- Dá ao cliente uma primeira visita à casa enquanto se decide o hardware.
- No iPhone abre o USDZ diretamente (Quick Look) e no Android o GLB (Scene Viewer), sem bibliotecas novas.

**Fases 4–5:** dependem da decisão sobre a workstation ou a GPU cloud.

**Fase 6:** quando houver ficheiros para guardar e links para dar.

**Fases 8–9:** no fim, como na especificação.

## 15. Decisões que precisam de aprovação

O hub já tem 6 decisões abertas do Step Inside (n.º 3 a 8: GPU da workstation, empacotamento Unreal, resolução e FPS, GPU
cloud, onde guardar os ficheiros 3D, VR). Os factos desta auditoria foram acrescentados ao contexto das decisões 3 e 7.

1. **Desenhos de clientes no Git público:** tirá-los já e, à parte, decidir se se reescreve o histórico.
2. **Workstation:** nova (64 GB, RTX 5070 Ti ou superior, NVMe 2 TB, Windows 11) ou começar o Unreal numa GPU cloud de
   teste. E confirmar se este PC é a workstation que se quer usar.
3. **Ordem das fases:** Fase 7 (AR) antes das Fases 4–5?
4. **Dois projetos de teste para a Fase 1:**
   - sugestão: Torres Vedras (tem levantamento topográfico e casa construída) e uma casa simples do Build Your House;
   - falta um projeto de outro arquiteto, se houver.
5. **Cloudflare:** dar acesso de leitura ao painel, ou uma captura, para fechar a tarefa 47.
6. **Headset VR de referência:** há um Meta Quest na empresa?
7. **Supabase Pro** (a partir de 25 USD/mês) antes de haver links de clientes.
8. **Da especificação §16.1:** resolução e FPS de lançamento, GPU cloud, VR por link como requisito ou só depois da prova
   de conceito, fonte topográfica mínima, retenção de versões, número de sessões no piloto.
9. **Documento de custos externos:** o «Custos Externos Plataforma 3D AR VR v2» (PDF de 2026-10-30) nunca foi partilhado
   nesta conversa. Pertence ao Step Inside?
