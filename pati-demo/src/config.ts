// Tudo o que costuma mudar no vídeo fica aqui: textos, cores, tempos e arquivos.
// Os tempos estão em segundos e são convertidos para frames dentro dos componentes.

export const VIDEO = {
  width: 1920,
  height: 1080,
  fps: 30,
  durationInSeconds: 45,
};

// Arquivos em public/. Para trocar uma imagem, substitua o arquivo mantendo o nome
// ou altere o caminho aqui.
export const ASSETS = {
  storyImage: "luis-justo-story.png",
  storyAspect: 1368 / 771, // largura / altura da miniatura
  artImage: "mockup-evento.png",
  artAspect: 1,
  music: "audio/trilha.wav",
  sfxClick: "audio/clique.wav",
  sfxSend: "audio/envio.wav",
  sfxReveal: "audio/revela.wav",
};

// Áreas da imagem do teste 1 que ficam desfocadas e cobertas (em % da imagem).
// A imagem atual é só o slide, sem nome, foto ou @ de quem postou, então nada é coberto.
// Se usar um print do story com a interface do Instagram, cubra o topo e a base, por exemplo:
//   { left: 0, top: 0, width: 100, height: 10 }, // barra de progresso, foto e nome de usuário
//   { left: 0, top: 91, width: 100, height: 9 },  // campo de resposta
export const STORY_PRIVACY_MASKS: { left: number; top: number; width: number; height: number }[] = [];

export const VOLUME = {
  music: 0.65,
  click: 0.5,
  send: 0.45,
  reveal: 0.35,
};

export const COLORS = {
  desk: "#E9E7E2",
  window: "#FFFFFF",
  chrome: "#F1F0ED",
  chromeLine: "#E2E0DC",
  sidebar: "#F7F7F5",
  line: "#E6E5E1",
  text: "#161616",
  textSoft: "#4A4A48",
  textMuted: "#8A8984",
  userBubble: "#EFEFEC",
  accent: "#1F4D3A", // verde escuro da PATI
  accentSoft: "#E3EEE7", // fundo de recomendações
  mark: "#CFE3D6", // marcação editorial nos trechos destacados
  veil: "rgba(240, 239, 235, 0.62)",
};

export const FONT_FAMILY = "Inter";

export const TEXTS = {
  appName: "PATI - Persona para Análise, Teste e Insights",
  tabTitle: "PATI",
  address: "pati / nova conversa",
  composerPlaceholder: "Pergunte à PATI",
  disclaimer:
    "A PATI é uma persona de teste. Use as análises para decidir com o time.",
  sidebarNew: "Nova conversa",
  sidebarSection: "Análises",
  sidebarFooter: "Grupo Gestão RH",

  intro: {
    title: "Conheça a PATI",
    subtitle: "Persona para Análise, Teste e Insights",
  },

  whatSheDoes: {
    line1: "Ela pensa como uma liderança sênior de RH.",
    line2: "E tensiona ideias antes que elas cheguem ao público.",
    criteria: ["Relevância.", "Credibilidade.", "Aplicação."],
  },

  test1: {
    chapter: "Teste 1 de 3",
    chapterTitle: "Gancho de palestra",
    sidebar: "Gancho da palestra",
    user: "Pati, no evento de ontem o Luis Justo, CEO do Rock In Rio tinha esse slide e uma das convidadas postou justo esse story, imaginei por dados que poderia ser um gancho pra uma aspas ou um post da palestra, o que acha?",
    userMarks: ["poderia ser um gancho", "uma aspas ou um post"],
    reply1: "Eu pararia nesse gancho.",
    reply2:
      "Mas a frase sozinha pode virar apenas mais uma inspiração de evento.",
    reco: "Mostre o que sustenta a provocação e qual decisão ela movimenta no RH.",
    recoEmphasis: ["sustenta", "decisão"],
  },

  test2: {
    chapter: "Teste 2 de 3",
    chapterTitle: "Assunto de e-mail",
    sidebar: "Assunto do e-mail",
    userIntro:
      "Estamos com dúvida entre esses dois assuntos pro e-mail da semana:",
    optionA: { label: "Assunto A", text: "IA & RH" },
    optionB: {
      label: "Assunto B",
      text: "O RH pode não estar pronto pra aplicar IA e pouco se fala disso",
    },
    reply1: "‘IA & RH’ é amplo e previsível.",
    reply2: "O assunto B tem tensão, mas antecipa uma conclusão.",
    solutionLabel: "Assunto sugerido",
    solution: "O que precisa estar pronto antes de aplicar IA no RH",
    solutionNote: "Promete utilidade concreta sem subestimar quem lê.",
  },

  test3: {
    chapter: "Teste 3 de 3",
    chapterTitle: "Arte de convite",
    sidebar: "Arte do encontro",
    user: "e essa arte, o que você acha? ignore o fato de ser IA. é só um mockup",
    reply1: "A imagem transmite pausa, intimidade e uma experiência reservada.",
    reply2: "Mas ainda poderia anunciar um retiro de bem-estar.",
    reco: "A emoção abre a conversa. A linha de apoio precisa provar substância.",
    recoEmphasis: ["emoção", "substância."],
    suggestionLabel: "Linha de apoio sugerida",
    suggestion:
      "Um encontro reservado entre lideranças de RH para conversas que exigem confiança, repertório e tempo.",
  },

  closing: {
    line1: "Agentes que conhecem o público ajudam a decidir melhor.",
    line2: ["Antes de publicar.", "Antes de convidar.", "Antes de investir."],
    signature: "PATI | Grupo Gestão RH",
  },
};

// Linha do tempo, em segundos (absolutos no vídeo).
// Cada teste dura do seu `start` até o `start` do próximo; o encerramento vai até o fim do vídeo.
export const TIMING = {
  browserIn: 0,
  introTitle: 0.4,
  introSubtitle: 0.75,
  introToHeader: 2.2, // texto central sobe e se integra ao cabeçalho

  whatLine1: 3.2,
  whatLine2: 4.4,
  criteria: 5.8, // as três palavras entram com 0,4 s entre elas
  scrollToTest1: 7.9,

  // Respostas da PATI: cada bloco fica sozinho na tela o tempo de leitura dele
  // (cerca de 3 palavras por segundo) antes do próximo entrar.
  test1: {
    start: 9,
    cursorIn: 9.0,
    attachClick: 9.5,
    composerText: 9.75,
    sendClick: 10.25,
    send: 10.35,
    mark1: 10.9,
    mark2: 11.4,
    thinking: 12.0,
    reply1: 12.4,
    reply2: 13.5,
    reco: 15.4, // recomendação fica 3,6 s na tela
  },
  test2: {
    start: 19,
    cursorIn: 19.25,
    composerText: 19.2,
    sendClick: 19.75,
    send: 19.85,
    thinking: 21.6,
    reply1: 22.0,
    reply2: 23.2,
    solution: 25.0,
    solutionNote: 25.9, // assunto sugerido fica 4,5 s na tela
  },
  test3: {
    start: 29.5,
    cursorIn: 29.5,
    attachClick: 30.0,
    composerText: 30.25,
    sendClick: 30.75,
    send: 30.85,
    thinking: 31.9,
    reply1: 32.3,
    reply2: 34.0,
    reco: 35.7,
    suggestion: 37.8, // sugestão fica 4,2 s na tela
  },
  closing: {
    start: 42,
    line1: 42.3,
    line2: 42.7, // três partes com 0,2 s entre elas
    signature: 42.9,
    // tudo termina até 43,5 s: o último 1,5 s fica estático
  },
};

// Medidas da interface (em pixels do quadro, antes do zoom da câmera).
export const LAYOUT = {
  window: { x: 60, y: 48, width: 1800, height: 984, radius: 16 },
  chromeHeight: 52,
  sidebarWidth: 272,
  headerHeight: 64,
  columnWidth: 960,
  composerBottom: 20, // distância do composer até a linha de aviso
  disclaimerHeight: 30,
  composerIdleHeight: 112,
  // fonte base dos balões; o ajuste automático reduz até o mínimo se o texto não couber
  userFont: 25,
  userFontMin: 19,
  userBubbleMaxWidth: 720,
  userBubbleMaxHeightRatio: 0.55, // fração da área visível da conversa
  patiFont: 26,
  storyThumbHeight: 250,
  artThumbHeight: 300,
};

// Enquadramento: [segundo, zoom, foco x, foco y]. O foco é o ponto do quadro (antes do zoom)
// que fica no centro da tela; ele é limitado para nunca mostrar além da janela do navegador.
// Os keyframes acompanham TIMING, então mudar um tempo lá move a câmera junto.
const testCamera = (
  t: { send: number; reply1: number; reco?: number; solution?: number },
  next: number,
): [number, number, number, number][] => {
  const highlight = t.reco ?? t.solution ?? t.reply1;
  return [
    [t.send + 0.15, 1.08, 1096, 540],
    [t.send + 0.75, 1.14, 1250, 470], // leitura do prompt
    [t.reply1 - 0.3, 1.14, 1250, 470],
    [t.reply1 + 0.4, 1.1, 1000, 600], // resposta da PATI
    [highlight - 0.7, 1.1, 1000, 600],
    [highlight, 1.15, 1000, 650], // recomendação
    [next - 0.4, 1.15, 1000, 650],
  ];
};

export const CAMERA: [number, number, number, number][] = [
  [0, 1, 960, 540],
  [TIMING.scrollToTest1, 1, 960, 540],
  [TIMING.scrollToTest1 + 1, 1.08, 1096, 540],
  ...testCamera(TIMING.test1, TIMING.test2.start),
  [TIMING.test2.start + 0.2, 1.08, 1096, 540],
  ...testCamera(TIMING.test2, TIMING.test3.start),
  [TIMING.test3.start + 0.2, 1.08, 1096, 540],
  ...testCamera(TIMING.test3, TIMING.closing.start + 0.4),
  [TIMING.closing.start + 1, 0.9, 960, 540], // o chat se afasta no encerramento
];
