# 2026 March Madness Bracket Predictor

A machine learning model that predicts the 2026 NCAA Men's Basketball Tournament bracket using KenPom efficiency metrics, historical seed win rates, logistic regression, and Monte Carlo simulation.

## Model Overview

- **KenPom AdjEM**: Core metric — win probability via normal CDF on efficiency margin difference (σ = 22.70)
- **Ensemble blend**: 72% efficiency-based + 28% historical seed win rates
- **Logistic Regression**: Trained on 10,000 synthetic games; features: AdjEM diff, seed diff, adj. offense/defense diffs
- **Monte Carlo simulation**: 50,000 tournament iterations producing per-team round-by-round probability distributions
- **Historical seed win rates**: Calibrated to 40 years of tournament data (1985–2025)
- **Backtesting**: 97.6% accuracy, log loss 0.279, Brier score 0.0752 on synthetic historical validation set

## Live Site

`https://atomlinsonc.github.io/2026-March-Madness-Bracket-Predictor/`

## Run the Model

Install dependencies:

```bash
pip install -r requirements.txt
```

Run predictions:

```bash
python predict_2026.py
```

Flags:
- `--quick` — skip backtest, run fewer simulations
- `--backtest-only` — run historical validation only
- `--no-backtest` — skip validation, run full Monte Carlo

## Project Structure

```
predict_2026.py          # Main runner
march_madness/
  data.py                # Team ratings, bracket structure, historical data
  model.py               # Efficiency model, logistic regression, ensemble
  tournament.py          # Bracket simulation engine
  backtest.py            # Historical validation
index.html               # Interactive bracket visualization (GitHub Pages)
requirements.txt
```
