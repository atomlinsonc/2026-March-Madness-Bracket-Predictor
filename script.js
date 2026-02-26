const initialState = {
  inflation: 4.2,
  unemployment: 5.8,
  growth: 2.1,
  moneySupply: 100,
  confidence: 62,
};

const scenarios = [
  {
    title: "Consumer demand is weakening",
    prompt:
      "Households are spending less and businesses are delaying hiring. Analysts warn growth could stall.",
    choices: [
      {
        label: "Lower interest rates by 0.5%",
        effects: { inflation: 0.4, unemployment: -0.5, growth: 0.6, moneySupply: 5, confidence: 4 },
        lesson:
          "Lower rates encourage borrowing and spending. This usually boosts growth and jobs, but can increase inflation if demand overheats.",
      },
      {
        label: "Keep rates unchanged",
        effects: { inflation: -0.1, unemployment: 0.2, growth: -0.2, moneySupply: 0, confidence: -2 },
        lesson:
          "Holding rates steady can protect against inflation, but if demand is already weak, unemployment may rise and growth can slow.",
      },
      {
        label: "Raise interest rates by 0.25%",
        effects: { inflation: -0.5, unemployment: 0.5, growth: -0.6, moneySupply: -3, confidence: -4 },
        lesson:
          "Higher rates cool inflation by reducing borrowing. In a weak economy, though, this can worsen unemployment and recession risk.",
      },
    ],
  },
  {
    title: "Energy prices spike",
    prompt:
      "Oil and gas costs jumped, pushing up transportation and production expenses nationwide.",
    choices: [
      {
        label: "Slightly raise rates and communicate inflation focus",
        effects: { inflation: -0.6, unemployment: 0.2, growth: -0.2, moneySupply: -2, confidence: 3 },
        lesson:
          "When prices rise from supply shocks, modest tightening can keep inflation expectations anchored without crushing demand.",
      },
      {
        label: "Do nothing and wait for prices to settle",
        effects: { inflation: 0.5, unemployment: -0.1, growth: 0.1, moneySupply: 0, confidence: -3 },
        lesson:
          "Waiting can protect short-term employment, but inflation may become persistent if firms and workers expect prices to keep rising.",
      },
      {
        label: "Large emergency rate cut",
        effects: { inflation: 0.8, unemployment: -0.2, growth: 0.4, moneySupply: 6, confidence: -5 },
        lesson:
          "Cutting rates during an inflationary supply shock can add extra demand, making inflation harder to control later.",
      },
    ],
  },
  {
    title: "Banks tighten lending standards",
    prompt:
      "Commercial banks are approving fewer loans, and small businesses report credit is drying up.",
    choices: [
      {
        label: "Buy government bonds (quantitative easing)",
        effects: { inflation: 0.2, unemployment: -0.4, growth: 0.5, moneySupply: 7, confidence: 5 },
        lesson:
          "Bond purchases inject liquidity. This can support lending and jobs, but too much liquidity may fuel inflation in later rounds.",
      },
      {
        label: "Launch targeted lending facility",
        effects: { inflation: 0.1, unemployment: -0.6, growth: 0.6, moneySupply: 4, confidence: 7 },
        lesson:
          "Targeted credit tools help stressed sectors while limiting broad inflation pressure compared with across-the-board stimulus.",
      },
      {
        label: "No intervention",
        effects: { inflation: -0.2, unemployment: 0.6, growth: -0.7, moneySupply: -4, confidence: -6 },
        lesson:
          "If credit contracts too much, businesses cut hiring and investment, increasing recession risk even if inflation eases.",
      },
    ],
  },
  {
    title: "Wages and prices are both rising fast",
    prompt:
      "Workers are demanding bigger raises while companies pass costs on to consumers. Inflation is broadening.",
    choices: [
      {
        label: "Raise rates decisively by 0.75%",
        effects: { inflation: -0.9, unemployment: 0.4, growth: -0.4, moneySupply: -5, confidence: 2 },
        lesson:
          "A stronger rate hike can break an inflation spiral. The trade-off is slower growth and some short-term labor-market pain.",
      },
      {
        label: "Small 0.25% rate hike",
        effects: { inflation: -0.4, unemployment: 0.1, growth: -0.1, moneySupply: -2, confidence: 1 },
        lesson:
          "Gradual tightening can balance inflation control and jobs, but may be insufficient if inflation momentum is strong.",
      },
      {
        label: "Pause hikes to protect employment",
        effects: { inflation: 0.7, unemployment: -0.1, growth: 0.2, moneySupply: 1, confidence: -4 },
        lesson:
          "Protecting jobs now can feel attractive, but persistent inflation eventually hurts purchasing power and long-run stability.",
      },
    ],
  },
  {
    title: "Economy near turning point",
    prompt:
      "Recent data is mixed. Inflation is improving, but unemployment ticked up and business confidence is fragile.",
    choices: [
      {
        label: "Signal future cuts, keep rates steady today",
        effects: { inflation: -0.2, unemployment: -0.1, growth: 0.2, moneySupply: 1, confidence: 5 },
        lesson:
          "Forward guidance can improve confidence without immediate stimulus. Expectations matter almost as much as current rates.",
      },
      {
        label: "Immediate rate cut",
        effects: { inflation: 0.3, unemployment: -0.4, growth: 0.5, moneySupply: 4, confidence: 4 },
        lesson:
          "Rate cuts can quickly support growth and hiring. If inflation is not fully under control, they can reignite price pressures.",
      },
      {
        label: "Another rate hike to finish inflation fight",
        effects: { inflation: -0.5, unemployment: 0.5, growth: -0.5, moneySupply: -3, confidence: -5 },
        lesson:
          "Extra tightening may secure low inflation but increases the chance of policy overshoot and recession.",
      },
    ],
  },
];

const state = { ...initialState };
let currentRound = 0;
let score = 0;

const statGrid = document.getElementById("stat-grid");
const statusMessage = document.getElementById("status-message");
const roundTitle = document.getElementById("round-title");
const scenarioText = document.getElementById("scenario-text");
const choicesEl = document.getElementById("choices");
const lessonEl = document.getElementById("lesson");
const lessonText = document.getElementById("lesson-text");
const nextBtn = document.getElementById("next-btn");
const summaryEl = document.getElementById("summary");
const finalScore = document.getElementById("final-score");
const finalSummary = document.getElementById("final-summary");
const restartBtn = document.getElementById("restart-btn");

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function formatPercent(value) {
  return `${value.toFixed(1)}%`;
}

function renderStats() {
  const indicators = [
    ["Inflation", formatPercent(state.inflation)],
    ["Unemployment", formatPercent(state.unemployment)],
    ["GDP Growth", formatPercent(state.growth)],
    ["Money Supply", `${state.moneySupply.toFixed(0)} index`],
    ["Confidence", `${state.confidence.toFixed(0)} / 100`],
  ];
  statGrid.innerHTML = indicators
    .map(
      ([label, value]) =>
        `<div class="stat-card"><span class="stat-label">${label}</span><span class="stat-value">${value}</span></div>`
    )
    .join("");

  const recessionRisk = state.growth < 0 || state.unemployment > 7.5;
  const inflationRisk = state.inflation > 6.5;

  if (!recessionRisk && !inflationRisk) {
    statusMessage.textContent = "Economy is relatively stable. Keep balancing growth and inflation.";
    statusMessage.className = "status-message good";
  } else if (recessionRisk && inflationRisk) {
    statusMessage.textContent = "Warning: stagflation risk (high inflation + weak growth).";
    statusMessage.className = "status-message bad";
  } else if (recessionRisk) {
    statusMessage.textContent = "Warning: recession risk is rising.";
    statusMessage.className = "status-message warn";
  } else {
    statusMessage.textContent = "Warning: inflation is becoming difficult to control.";
    statusMessage.className = "status-message warn";
  }
}

function calculateScore() {
  const inflationPenalty = Math.abs(state.inflation - 2.5) * 11;
  const unemploymentPenalty = Math.max(0, state.unemployment - 4.5) * 10;
  const growthPenalty = state.growth < 1 ? (1 - state.growth) * 13 : 0;
  const confidenceBonus = state.confidence * 0.3;
  return clamp(100 - inflationPenalty - unemploymentPenalty - growthPenalty + confidenceBonus, 0, 100);
}

function applyChoice(choice) {
  for (const [key, delta] of Object.entries(choice.effects)) {
    state[key] += delta;
  }
  state.inflation = clamp(state.inflation, 0, 12);
  state.unemployment = clamp(state.unemployment, 2.5, 15);
  state.growth = clamp(state.growth, -4, 8);
  state.moneySupply = clamp(state.moneySupply, 70, 160);
  state.confidence = clamp(state.confidence, 10, 100);
  score = calculateScore();
  lessonText.textContent = choice.lesson;
  lessonEl.classList.remove("hidden");
  nextBtn.classList.remove("hidden");
  Array.from(choicesEl.children).forEach((btn) => {
    btn.disabled = true;
    btn.style.opacity = "0.65";
  });
  renderStats();
}

function renderRound() {
  const scenario = scenarios[currentRound];
  roundTitle.textContent = `Round ${currentRound + 1}: ${scenario.title}`;
  scenarioText.textContent = scenario.prompt;
  choicesEl.innerHTML = "";
  scenario.choices.forEach((choice) => {
    const button = document.createElement("button");
    button.className = "choice-btn";
    button.textContent = choice.label;
    button.addEventListener("click", () => applyChoice(choice));
    choicesEl.appendChild(button);
  });
  lessonEl.classList.add("hidden");
  nextBtn.classList.add("hidden");
}

function gameSummaryText(finalScoreValue) {
  if (finalScoreValue >= 85) {
    return "Excellent stewardship. You balanced inflation and employment while avoiding a deep downturn.";
  }
  if (finalScoreValue >= 70) {
    return "Strong performance. A few trade-offs hurt stability, but your economy remained resilient.";
  }
  if (finalScoreValue >= 50) {
    return "Mixed outcome. Some choices stabilized one area while creating pressure in another.";
  }
  return "Your economy struggled. Review how each policy tool affected inflation, jobs, and confidence.";
}

function finishGame() {
  document.querySelector(".scenario").classList.add("hidden");
  summaryEl.classList.remove("hidden");
  finalScore.textContent = `Economic Health Score: ${score.toFixed(0)} / 100`;
  finalSummary.textContent = gameSummaryText(score);
}

function restartGame() {
  Object.assign(state, initialState);
  currentRound = 0;
  score = calculateScore();
  summaryEl.classList.add("hidden");
  document.querySelector(".scenario").classList.remove("hidden");
  renderStats();
  renderRound();
}

nextBtn.addEventListener("click", () => {
  currentRound += 1;
  if (currentRound >= scenarios.length) {
    finishGame();
  } else {
    renderRound();
  }
});

restartBtn.addEventListener("click", restartGame);

score = calculateScore();
renderStats();
renderRound();
