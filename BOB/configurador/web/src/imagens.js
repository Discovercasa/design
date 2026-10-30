// Small drawings for the menus (user 2026-10-21: "imagens representativas de cada opção"): the doors and windows of the
// company caixilharia (aluminium RAL 7016, double glazing), the interior wall and the roof types. Plain SVG, one style.
const AL = "#383E42", VID = "#A9CFE3", VID2 = "#D9E8EF", PAR = "#E9E4DC", LIN = "#8A8F94";

const svg = (corpo, vb = "0 0 96 72") => `<svg viewBox="${vb}" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">${corpo}</svg>`;
const parede = `<rect x="0" y="0" width="96" height="72" fill="${PAR}"/>`;
const vidro = (x, y, w, h, fosco = false) =>
  `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fosco ? VID2 : VID}"/>` +
  `<path d="M${x + w * 0.2} ${y + h * 0.75} L${x + w * 0.55} ${y + h * 0.25} M${x + w * 0.4} ${y + h * 0.85} L${x + w * 0.7} ${y + h * 0.42}" stroke="#fff" stroke-width="1.5" opacity=".7"/>`;
const aro = (x, y, w, h, e = 3) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="none" stroke="${AL}" stroke-width="${e}"/>`;
// a sliding window of n leaves (3, 4 — user 2026-10-22), the arrows on the leaves that slide
function correr(n) {
  const x0 = 6, w = 84, f = (w - 6) / n;
  let s = `${parede}<rect x="${x0}" y="6" width="${w}" height="62" fill="${AL}"/>`;
  for (let i = 0; i < n; i++) s += vidro(x0 + 3 + i * f + 0.8, 9, f - 1.6, 56);
  for (let i = 1; i < n; i++) s += `<line x1="${x0 + 3 + i * f}" y1="7" x2="${x0 + 3 + i * f}" y2="67" stroke="${AL}" stroke-width="2.6"/>`;
  const m = x0 + 3 + f / 2, mf = x0 + 3 + (n - 0.5) * f;
  s += `<path d="M${m - 6} 38 h12 m-3 -3 l3 3 l-3 3 M${mf + 6} 38 h-12 m3 -3 l-3 3 l3 3" fill="none" stroke="${AL}" stroke-width="1.6"/>`;
  return svg(s);
}

export const IMAGENS = {
  janela: svg(`${parede}<rect x="26" y="12" width="44" height="44" fill="${AL}"/>${vidro(29, 15, 18.5, 38)}${vidro(48.5, 15, 18.5, 38)}
    <line x1="48" y1="13" x2="48" y2="55" stroke="${AL}" stroke-width="2.5"/><rect x="44" y="32" width="2" height="7" fill="#c7ccd0"/>
    <path d="M29 15 L47 34 L29 53" fill="none" stroke="${LIN}" stroke-width=".8" stroke-dasharray="2 2"/>
    <rect x="22" y="56" width="52" height="3" fill="#cfc8bc"/>`),
  janela_correr: svg(`${parede}<rect x="10" y="6" width="76" height="62" fill="${AL}"/>${vidro(13, 9, 34, 56)}${vidro(49, 9, 34, 56)}
    <line x1="48" y1="7" x2="48" y2="67" stroke="${AL}" stroke-width="3"/>
    <path d="M22 38 h16 m-4 -4 l4 4 l-4 4 M74 38 h-16 m4 -4 l-4 4 l4 4" fill="none" stroke="${AL}" stroke-width="1.8"/>`),
  janela_correr_3: correr(3),
  janela_correr_4: correr(4),
  porta: svg(`${parede}<rect x="30" y="6" width="36" height="62" fill="${AL}"/><rect x="33" y="9" width="30" height="59" fill="#4b5257"/>
    <rect x="57" y="36" width="3" height="12" rx="1" fill="#c7ccd0"/><line x1="33" y1="25" x2="63" y2="25" stroke="${AL}" stroke-width=".8"/>`),
  basculante: svg(`${parede}<rect x="31" y="16" width="34" height="30" fill="${AL}"/>${vidro(34, 19, 28, 24, true)}
    <path d="M34 19 L48 43 L62 19" fill="none" stroke="${LIN}" stroke-width=".9" stroke-dasharray="2 2"/>
    <rect x="45" y="20" width="6" height="2" fill="#c7ccd0"/><rect x="28" y="46" width="40" height="3" fill="#cfc8bc"/>`),
  fixo: svg(`${parede}<rect x="12" y="20" width="72" height="34" fill="${AL}"/>${vidro(15, 23, 66, 28)}
    <text x="48" y="41" font-size="10" text-anchor="middle" fill="${AL}" font-family="Segoe UI, sans-serif" opacity=".55">fixo</text>
    <rect x="9" y="54" width="78" height="3" fill="#cfc8bc"/>`),
  portao: svg(`${parede}<rect x="6" y="10" width="84" height="58" fill="${AL}"/>
    ${[0, 1, 2, 3].map((i) => `<rect x="9" y="${13 + i * 13.7}" width="78" height="12.2" fill="#555c61"/><line x1="9" y1="${19 + i * 13.7}" x2="87" y2="${19 + i * 13.7}" stroke="#4a5055" stroke-width=".8"/>`).join("")}
    <rect x="44" y="60" width="8" height="2" fill="#c7ccd0"/>`),
  // the interior door (method: 0,80 x 2,00) in an interior wall, its leaf as cena.js draws it
  porta_interior: svg(`<rect width="96" height="72" fill="#F1EFE9"/><rect x="31" y="8" width="34" height="64" fill="#cfc4b0"/>
    <rect x="34" y="11" width="28" height="61" fill="#D9CDB8"/><rect x="56" y="40" width="4" height="2" rx="1" fill="#8a8f94"/>`),
  parede_interior: svg(`<rect width="96" height="72" fill="#f3f4f6"/>
    <polygon points="14,58 62,40 62,14 14,32" fill="#F1EFE9" stroke="${LIN}" stroke-width="1"/>
    <polygon points="62,40 76,46 76,20 62,14" fill="#DCD8CF" stroke="${LIN}" stroke-width="1"/>
    <polygon points="14,32 62,14 76,20 28,38" fill="#E7E3DA" stroke="${LIN}" stroke-width="1"/>
    <path d="M28 38 L28 64 M14 58 L28 64 L76 46" fill="none" stroke="${LIN}" stroke-width="1"/>
    <path d="M80 52 l8 3 m-3 -5 l3 5 l-5 2" fill="none" stroke="#e2a43a" stroke-width="2"/>`),
  // roofs: hidden behind the parapet; exposed with 2 slopes (gables) or 4 slopes (hips)
  escondida: svg(`<rect width="96" height="72" fill="#eef0f2"/>
    <polygon points="12,34 52,22 84,32 44,46" fill="#b0603f"/>
    <polygon points="12,30 52,18 84,28 44,42 44,64 12,52" fill="none"/>
    <polygon points="12,30 44,42 44,64 12,52" fill="#7a573b"/><polygon points="44,42 84,28 84,50 44,64" fill="#6e4b31"/>
    <polygon points="12,30 52,18 84,28 44,42 44,45 81,32 52,21.5 15,32.5" fill="#8a6545"/>`),
  duas_aguas: svg(`<rect width="96" height="72" fill="#eef0f2"/>
    <polygon points="14,40 44,50 44,66 14,56" fill="#7a573b"/><polygon points="44,50 84,36 84,52 44,66" fill="#6e4b31"/>
    <polygon points="14,40 29,22 44,50" fill="#8a6545"/>
    <polygon points="29,22 69,8 84,36 44,50" fill="#8f4e35"/><polygon points="10,41 29,19 31,21 14,43" fill="#383e42"/>`),
  // várias águas with empenas (L / T / U): the hipped body and a wing ending in a gable
  misto: svg(`<rect width="96" height="72" fill="#eef0f2"/>
    <polygon points="10,40 40,50 40,64 10,54" fill="#7a573b"/><polygon points="40,50 80,36 80,50 40,64" fill="#6e4b31"/>
    <polygon points="10,40 32,28 40,50" fill="#b0603f"/><polygon points="32,28 60,18 80,36 40,50" fill="#8f4e35"/>
    <polygon points="60,18 80,36 72,22" fill="#80402a"/>
    <polygon points="58,43.7 73,48.7 73,62.7 58,57.7" fill="#7a573b"/><polygon points="73,48.7 87,43.8 87,57.8 73,62.7" fill="#6e4b31"/>
    <polygon points="73,48.7 80,36.3 87,43.8" fill="#8a6545"/>
    <polygon points="80,36.3 65,31.3 72,38.8 87,43.8" fill="#80402a"/><polygon points="80,36.3 65,31.3 58,43.7 73,48.7" fill="#b0603f"/>`),
  // step 7 (user 2026-10-29): a pergola against the facade, a garage, an annex
  pergola: svg(`<rect width="96" height="72" fill="#eef0f2"/>
    <polygon points="8,26 40,14 40,62 8,70" fill="#6e4b31"/>
    <path d="M40 28 L88 40 M40 31 L88 43" stroke="#a9834f" stroke-width="3"/>
    <rect x="80" y="41" width="4" height="27" fill="#b88d55"/><rect x="58" y="36" width="4" height="27" fill="#b88d55"/>
    <path d="M44 27 L60 31 M50 26 L66 30 M56 25 L72 29 M62 24 L78 28 M68 23 L84 27 M74 22 L88 25" stroke="#c9a06a" stroke-width="2"/>
    <path d="M40 22 L88 34 L88 37 L40 25 Z" fill="#c9a06a"/>`),
  garagem: svg(`<rect width="96" height="72" fill="#eef0f2"/>
    <polygon points="10,30 46,40 46,66 10,56" fill="#7a573b"/><polygon points="46,40 86,28 86,54 46,66" fill="#6e4b31"/>
    <polygon points="10,30 50,18 86,28 46,40" fill="#8f4e35"/>
    <polygon points="16,40 40,47 40,63 16,56" fill="#43494d"/>
    <path d="M16 44 L40 51 M16 48 L40 55 M16 52 L40 59" stroke="#5c6267" stroke-width="1"/>`),
  anexo: svg(`<rect width="96" height="72" fill="#eef0f2"/>
    <polygon points="6,34 34,42 34,66 6,58" fill="#7a573b"/><polygon points="34,42 60,34 60,58 34,66" fill="#6e4b31"/>
    <polygon points="6,34 32,26 60,34 34,42" fill="#8f4e35"/>
    <polygon points="66,44 80,48 80,64 66,60" fill="#7a573b"/><polygon points="80,48 92,44 92,60 80,64" fill="#6e4b31"/>
    <polygon points="66,44 78,40 92,44 80,48" fill="#8f4e35"/>
    <rect x="70" y="50" width="5" height="11" fill="#383e42" transform="skewY(16) translate(0,-20)"/>`),
};
