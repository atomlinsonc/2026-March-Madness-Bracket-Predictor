# -*- coding: utf-8 -*-
"""
2026 NCAA March Madness Bracket Predictor
==========================================
Generates a complete bracket prediction for the 2026 NCAA Tournament.

Model: KenPom-style efficiency margins + historical seed win rates
       Logistic regression ensemble + Monte Carlo simulation (50,000 iterations)

Usage:
    python predict_2026.py                    # Full analysis
    python predict_2026.py --quick            # Skip Monte Carlo, show bracket only
    python predict_2026.py --backtest-only    # Run validation only, skip 2026 predictions
    python predict_2026.py --no-backtest      # Skip validation, run 2026 predictions only

Output:
    - Model validation / backtesting results
    - Championship probability rankings
    - Complete round-by-round bracket predictions
    - Key upset picks and analysis
"""

import sys
import io
import time
import numpy as np

# Force UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


def print_header():
    print("\n" + "=" * 70)
    print("       2026 NCAA MARCH MADNESS BRACKET PREDICTION MODEL")
    print("       Based on KenPom Efficiency Ratings + Monte Carlo Simulation")
    print("=" * 70)
    print(f"  Model: Ensemble (Efficiency + Seed History + Logistic Regression)")
    print(f"  Simulations: 50,000 Monte Carlo iterations")
    print(f"  Efficiency blend: 72% efficiency / 28% historical seed rates")
    print(f"  Sigma (calibrated): 13.5 AdjEM points")
    print("=" * 70)


def print_full_bracket(bracket_picks: dict, sim_results=None):
    """Print the complete bracket prediction in a readable format."""

    REGIONS = ["East", "West", "Midwest", "South"]
    R1_GAME_LABELS = [
        "1/16", "8/9", "5/12", "4/13", "6/11", "3/14", "7/10", "2/15"
    ]

    print("\n" + "=" * 70)
    print("   COMPLETE 2026 BRACKET PREDICTION")
    print("=" * 70)

    for region in REGIONS:
        print(f"\n  ┌─ {region.upper()} REGION ──────────────────────────────────────────┐")

        # Round 1
        print(f"  │  ROUND OF 64:")
        for i in range(8):
            key = f"{region}_R1_G{i+1}"
            if key in bracket_picks:
                g = bracket_picks[key]
                conf_str = f"{g['confidence']:.0%}"
                upset_flag = ""
                if g["seed"] > int(R1_GAME_LABELS[i].split("/")[0]):
                    upset_flag = " ← UPSET PICK"
                print(f"  │    {R1_GAME_LABELS[i]:>5}  {g['game']:<38}  "
                      f"PICK: #{g['seed']} {g['pick']:<16} ({conf_str}){upset_flag}")

        # Round 2
        print(f"  │  ROUND OF 32:")
        for i in range(4):
            key = f"{region}_R2_G{i+1}"
            if key in bracket_picks:
                g = bracket_picks[key]
                conf_str = f"{g['confidence']:.0%}"
                print(f"  │         {'':>5}  {g['game']:<38}  "
                      f"PICK: #{g['seed']} {g['pick']:<16} ({conf_str})")

        # Sweet 16
        print(f"  │  SWEET 16:")
        for i in range(2):
            key = f"{region}_S16_G{i+1}"
            if key in bracket_picks:
                g = bracket_picks[key]
                conf_str = f"{g['confidence']:.0%}"
                print(f"  │         {'':>5}  {g['game']:<38}  "
                      f"PICK: #{g['seed']} {g['pick']:<16} ({conf_str})")

        # Elite 8
        key = f"{region}_E8"
        if key in bracket_picks:
            g = bracket_picks[key]
            conf_str = f"{g['confidence']:.0%}"
            print(f"  │  ELITE 8:  {g['game']:<38}  "
                  f"PICK: #{g['seed']} {g['pick']:<16} ({conf_str})")

        # Regional champion
        key = f"{region}_champion"
        if key in bracket_picks:
            champ = bracket_picks[key]
            p_champ = ""
            if sim_results:
                p = sim_results.get_prob(champ.name, 7)
                p_champ = f"  [{p:.1%} to win title]"
            print(f"  │  ★ REGIONAL CHAMPION: #{champ.seed} {champ.name} "
                  f"({champ.record}){p_champ}")

        print(f"  └────────────────────────────────────────────────────────────────┘")

    # Final Four
    print(f"\n  ┌─ FINAL FOUR ──────────────────────────────────────────────────────┐")
    print(f"  │  Location: Lucas Oil Stadium, Indianapolis, IN (April 4, 2026)")
    ff_matchups = [("East", "West"), ("Midwest", "South")]
    ff_winners = []
    for region_a, region_b in ff_matchups:
        key = f"FF_{region_a}_{region_b}"
        if key in bracket_picks:
            g = bracket_picks[key]
            conf_str = f"{g['confidence']:.0%}"
            print(f"  │  {region_a}/{region_b}: {g['game']}")
            print(f"  │    ➤ PICK: #{g['seed']} {g['pick']:<20} ({conf_str})")
            team_a_region = bracket_picks.get(f"{region_a}_champion")
            team_b_region = bracket_picks.get(f"{region_b}_champion")
            winner = team_a_region if team_a_region and team_a_region.name == g["pick"] else team_b_region
            if winner:
                ff_winners.append(winner)
    print(f"  └────────────────────────────────────────────────────────────────────┘")

    # Championship
    print(f"\n  ┌─ NATIONAL CHAMPIONSHIP ───────────────────────────────────────────┐")
    print(f"  │  Date: April 6, 2026 | Location: Indianapolis, IN")
    if "Championship" in bracket_picks:
        g = bracket_picks["Championship"]
        conf_str = f"{g['confidence']:.0%}"
        print(f"  │  Matchup: {g['game']}")
        print(f"  │  ➤ PREDICTED WINNER: #{g['seed']} {g['pick']:<20} ({conf_str})")
    if "Champion" in bracket_picks:
        champ = bracket_picks["Champion"]
        p_title = ""
        if sim_results:
            p = sim_results.get_prob(champ.name, 7)
            p_title = f"  (Model: {p:.1%} championship probability)"
        print(f"  │")
        print(f"  │  🏆 2026 NATIONAL CHAMPION PICK: #{champ.seed} {champ.name} "
              f"({champ.record}){p_title}")
    print(f"  └────────────────────────────────────────────────────────────────────┘")


def print_upset_analysis(model, bracket):
    """Analyze upset probability for all first-round games."""
    print("\n" + "=" * 70)
    print("   FIRST ROUND UPSET ANALYSIS")
    print("=" * 70)
    print(f"  Games where the model gives the 'worse' seed >25% win probability:")
    print(f"  {'Matchup':<40} {'Underdog Win%':>14} {'Historical':>12}")
    print(f"  {'-'*68}")

    from march_madness.data import HISTORICAL_SEED_WIN_RATES

    upsets_flagged = []
    for region_name, region_games in bracket.items():
        for team_a, team_b in region_games:
            result = model.predict(team_a.name, team_b.name, round_num=1)
            # Underdog = higher seed number
            underdog = team_b if team_b.seed > team_a.seed else team_a
            favorite = team_a if team_b.seed > team_a.seed else team_b
            p_upset = result["p_b_wins"] if team_b == underdog else result["p_a_wins"]

            hist_p = HISTORICAL_SEED_WIN_RATES.get(
                (favorite.seed, underdog.seed),
                1 - HISTORICAL_SEED_WIN_RATES.get((underdog.seed, favorite.seed), 0.5)
            )
            hist_upset = 1 - hist_p

            if p_upset >= 0.25:  # Flag upset-worthy games
                upsets_flagged.append({
                    "matchup": f"#{favorite.seed} {favorite.name} vs #{underdog.seed} {underdog.name}",
                    "underdog": f"#{underdog.seed} {underdog.name}",
                    "p_upset": p_upset,
                    "hist_upset": hist_upset,
                    "region": region_name,
                })

    upsets_flagged.sort(key=lambda x: x["p_upset"], reverse=True)

    for u in upsets_flagged:
        flag = " ← HIGH UPSET RISK" if u["p_upset"] > 0.38 else ""
        print(f"  {u['matchup']:<40} {u['p_upset']:>13.1%}  {u['hist_upset']:>11.1%}{flag}")

    print(f"\n  Note: 5v12 historically upsets 35.7% | 6v11: 37.1% | 8v9: 52.1%")
    print(f"  The model adjusts these based on each team's actual efficiency rating.")


def print_model_picks_summary(bracket_picks: dict, sim_results=None):
    """Print a clean summary of all picks."""
    print("\n" + "=" * 70)
    print("   BRACKET PICKS SUMMARY (Fill Out Your Bracket)")
    print("=" * 70)

    regions = ["East", "West", "Midwest", "South"]
    rounds = [
        ("R1", "Round of 64", range(1, 9)),
        ("R2", "Round of 32", range(1, 5)),
        ("S16", "Sweet 16", range(1, 3)),
        ("E8", "Elite 8", None),
    ]

    for round_code, round_name, game_range in rounds:
        print(f"\n  {round_name.upper()}:")
        for region in regions:
            if game_range is None:
                key = f"{region}_{round_code}"
                if key in bracket_picks:
                    g = bracket_picks[key]
                    print(f"    {region:<10}: #{g['seed']} {g['pick']:<20} ({g['confidence']:.0%})")
            else:
                for i in game_range:
                    key = f"{region}_{round_code}_G{i}"
                    if key in bracket_picks:
                        g = bracket_picks[key]
                        print(f"    {region:<10} G{i}: #{g['seed']} {g['pick']:<20} ({g['confidence']:.0%})")

    print(f"\n  FINAL FOUR:")
    for region_a, region_b in [("East", "West"), ("Midwest", "South")]:
        key = f"FF_{region_a}_{region_b}"
        if key in bracket_picks:
            g = bracket_picks[key]
            print(f"    {region_a} vs {region_b}: #{g['seed']} {g['pick']:<20} ({g['confidence']:.0%})")

    if "Championship" in bracket_picks:
        g = bracket_picks["Championship"]
        print(f"\n  CHAMPIONSHIP:")
        print(f"    #{g['seed']} {g['pick']:<20} ({g['confidence']:.0%})")

    if "Champion" in bracket_picks:
        champ = bracket_picks["Champion"]
        p_title = ""
        if sim_results:
            p = sim_results.get_prob(champ.name, 7)
            p_title = f" — Model championship probability: {p:.1%}"
        print(f"\n  ★ CHAMPION: #{champ.seed} {champ.name} ({champ.record}){p_title}")


def main():
    args = sys.argv[1:]
    quick_mode = "--quick" in args
    backtest_only = "--backtest-only" in args
    no_backtest = "--no-backtest" in args
    n_sims = 50_000 if not quick_mode else 10_000

    print_header()
    t_start = time.time()

    # ==========================================================================
    # STEP 1: Initialize and train model
    # ==========================================================================
    print("\n[1/5] Initializing model...")
    from march_madness.model import MarchMadnessModel
    model = MarchMadnessModel(efficiency_blend=0.72, sigma=13.5)

    # Calibrate sigma against historical seed win rates
    print("  Calibrating efficiency model sigma...")
    model.calibrate_sigma(verbose=True)

    # Train logistic regression on synthetic historical data
    print("  Training logistic regression component...")
    model.train(use_synthetic=True, n_synthetic=10_000)

    print(f"  Model ready. Elapsed: {time.time() - t_start:.1f}s")

    # ==========================================================================
    # STEP 2: Backtesting / Model Validation
    # ==========================================================================
    if not no_backtest:
        print("\n[2/5] Running backtesting validation...")
        from march_madness.backtest import (
            run_historical_validation, run_bracket_score_simulation
        )
        backtest_results = run_historical_validation(model, verbose=True)
        score_results = run_bracket_score_simulation(model, n_sims=500, verbose=True)
        print(f"\n  Backtesting complete. Elapsed: {time.time() - t_start:.1f}s")

    if backtest_only:
        print("\n  [Backtest-only mode. Exiting.]")
        return

    # ==========================================================================
    # STEP 3: Monte Carlo Simulation
    # ==========================================================================
    if not quick_mode:
        print(f"\n[3/5] Running Monte Carlo simulation ({n_sims:,} iterations)...")
        from march_madness.tournament import TournamentSimulator
        simulator = TournamentSimulator(model, n_simulations=n_sims)
        sim_results = simulator.run(verbose=True)
        print(f"  Simulation complete. Elapsed: {time.time() - t_start:.1f}s")

        # Print championship odds
        sim_results.print_championship_odds(top_n=25)
    else:
        sim_results = None
        print("\n[3/5] Skipped Monte Carlo (--quick mode)")

    # ==========================================================================
    # STEP 4: Generate Most Likely Bracket
    # ==========================================================================
    print(f"\n[4/5] Generating bracket predictions...")
    from march_madness.tournament import TournamentSimulator, build_bracket_from_data

    bracket = build_bracket_from_data()

    # Create a lightweight sim just for bracket generation (no Monte Carlo)
    from march_madness.tournament import SimulationResults
    if sim_results is not None:
        bracket_picks = sim_results.get_most_likely_bracket(model)
    else:
        # Quick mode: generate bracket without Monte Carlo
        dummy_results = SimulationResults({}, 1, bracket)
        bracket_picks = dummy_results.get_most_likely_bracket(model)

    # ==========================================================================
    # STEP 5: Output Results
    # ==========================================================================
    print(f"\n[5/5] Generating output...")

    # Upset analysis
    print_upset_analysis(model, bracket)

    # Full bracket
    print_full_bracket(bracket_picks, sim_results)

    # Clean summary (fill-out-your-bracket format)
    print_model_picks_summary(bracket_picks, sim_results)

    # Key insights
    print_key_insights(model, bracket, sim_results)

    print(f"\n  Total elapsed time: {time.time() - t_start:.1f}s")
    print("\n" + "=" * 70)
    print("  PREDICTION COMPLETE — Good luck with your bracket!")
    print("=" * 70 + "\n")


def print_key_insights(model, bracket, sim_results=None):
    """Print analytical insights about the 2026 bracket."""
    print("\n" + "=" * 70)
    print("   KEY ANALYTICAL INSIGHTS — 2026 TOURNAMENT")
    print("=" * 70)

    print("""
  METHODOLOGY NOTES:
  ─────────────────────────────────────────────────────────────────────
  • Win probabilities use KenPom-style adjusted efficiency margins (AdjEM)
  • Formula: P(A wins) = Φ(AdjEM_diff / sigma), sigma calibrated to 13.5
  • Efficiency ratings are approximate — replace with actual KenPom/Torvik
    data from kenpom.com or barttorvik.com for improved accuracy
  • Historical seed win rates provide a calibration anchor (28% weight)
  • Monte Carlo simulates 50,000 full bracket scenarios

  2026 BRACKET ANALYSIS:
  ─────────────────────────────────────────────────────────────────────
  • FAVORITE: Duke (#1 East, KenPom #1, 32-2)
    Strongest overall efficiency profile. Cameron Boozer era begins.

  • CONTENDERS: Michigan (#1 Midwest), Arizona (#1 West), Florida (#1 South)
    Michigan has nation's #1 defense (KenPom). Arizona safest bracket draw.
    Florida is defending champion but faces South bracket with Houston.

  • VALUE PICK: Houston (#2 South)
    Plays Sweet 16 + Elite 8 IN HOUSTON — massive home court advantage.
    Top-5 KenPom defense. Only 2nd seed but near-home venue = undervalued.

  • WATCH OUT FOR: Gonzaga (#3 West)
    30-3 record, elite offense (AdjO ~119). Can beat anyone on their day.

  • UPSET ALERT — 5v12 MATCHUPS (historically 36% upset rate):
    • Wisconsin (#5) vs High Point (#12): High Point went 30-4! Big threat.
    • Vanderbilt (#5) vs McNeese (#12): McNeese 28-5, dangerous mid-major.
    • Texas Tech (#5) vs Akron (#12): Akron 29-5, strong conference record.

  • UPSET ALERT — 6v11 MATCHUPS (historically 37% upset rate):
    • BYU (#6) vs Texas/NC State (#11 FF winner): Power-conf bubble team.
    • Louisville (#6) vs South Florida (#11): 25-8 USF is no easy out.

  • BIGGEST QUESTION: Can Florida defend its title?
    Only 26-7 (weakest 1-seed), faces Houston in Sweet 16/E8 Houston venue.
    Still top-10 KenPom but not as dominant as 2025 version.

  HISTORICAL CONTEXT:
  ─────────────────────────────────────────────────────────────────────
  • #1 seeds win ~65% of championships since 1985
  • 23 of 24 recent champions ranked top-21 in KenPom AdjO
  • 5v12 upset rate: 35.7% (expect 1-2 per tournament)
  • 8v9 matchups: true coin flip (9-seed has slight all-time edge)
  • #11 seeds reach Final Four at higher rate than #9 or #10 (power-conf teams)
  • Houston's venue advantage in South is the most underrated factor in this bracket
""")


if __name__ == "__main__":
    main()
