"""
Tournament Bracket Simulator
============================
Monte Carlo simulation of the full 2026 NCAA Tournament bracket.
Runs 50,000 simulations to compute:
  - Win probability at each round for every team
  - Championship probability distribution
  - Most likely bracket (highest expected score)
  - Upset probability analysis

Methodology:
  - Each game simulated via model win probability
  - 50,000 independent simulations for stable probability estimates
  - Results: per-team probability of reaching each round
  - "Best bracket" strategy: maximize expected ESPN Tournament Challenge score
"""

import copy
import numpy as np
from collections import defaultdict
from typing import Optional


# =============================================================================
# BRACKET DATA STRUCTURES
# =============================================================================

class Team:
    """Represents a tournament team with its ratings and bracket position."""

    def __init__(self, name: str, seed: int, region: str,
                 adj_em: float, adj_o: float = 105.0, adj_d: float = 105.0,
                 record: str = "?", notes: str = ""):
        self.name = name
        self.seed = seed
        self.region = region
        self.adj_em = adj_em
        self.adj_o = adj_o
        self.adj_d = adj_d
        self.record = record
        self.notes = notes

    def to_dict(self) -> dict:
        return {
            "name": self.name, "seed": self.seed, "region": self.region,
            "adj_em": self.adj_em, "adj_o": self.adj_o, "adj_d": self.adj_d,
        }

    def __repr__(self):
        return f"#{self.seed} {self.name} ({self.record})"


class Game:
    """Represents a single tournament game."""

    def __init__(self, team_a: Team, team_b: Team, region: str, round_num: int):
        self.team_a = team_a
        self.team_b = team_b
        self.region = region
        self.round_num = round_num
        self.winner: Optional[Team] = None
        self.win_prob_a: Optional[float] = None

    def __repr__(self):
        return (f"Round {self.round_num}: {self.team_a.name} vs {self.team_b.name} "
                f"({self.region})")


# =============================================================================
# BRACKET BUILDER
# =============================================================================

def build_bracket_from_data() -> dict:
    """
    Build the 2026 tournament bracket structure from data module.

    Returns:
        Dict with 'regions' and 'first_four' keys
    """
    from march_madness.data import (
        BRACKET_2026, TEAM_RATINGS, FIRST_FOUR_EXPECTED_WINNERS
    )

    regions = {}

    for region_name, matchups in BRACKET_2026.items():
        region_games = []
        for seed_a, name_a, seed_b, name_b in matchups:
            # Resolve First Four placeholders
            resolved_a = FIRST_FOUR_EXPECTED_WINNERS.get(name_a, name_a)
            resolved_b = FIRST_FOUR_EXPECTED_WINNERS.get(name_b, name_b)

            # Get team data
            data_a = TEAM_RATINGS.get(resolved_a, {})
            data_b = TEAM_RATINGS.get(resolved_b, {})

            team_a = Team(
                name=resolved_a,
                seed=seed_a,
                region=region_name,
                adj_em=data_a.get("adj_em", 0.0),
                adj_o=data_a.get("adj_o", 105.0),
                adj_d=data_a.get("adj_d", 105.0),
                record=data_a.get("record", "?"),
                notes=data_a.get("notes", ""),
            )
            team_b = Team(
                name=resolved_b,
                seed=seed_b,
                region=region_name,
                adj_em=data_b.get("adj_em", 0.0),
                adj_o=data_b.get("adj_o", 105.0),
                adj_d=data_b.get("adj_d", 105.0),
                record=data_b.get("record", "?"),
                notes=data_b.get("notes", ""),
            )

            region_games.append((team_a, team_b))

        regions[region_name] = region_games

    return regions


# =============================================================================
# TOURNAMENT SIMULATOR
# =============================================================================

class TournamentSimulator:
    """
    Runs Monte Carlo simulations of the full NCAA tournament bracket.

    Architecture:
      - 4 regions × 3 rounds → produces 4 regional champions
      - 2 Final Four games (winners of East/West, Midwest/South)
      - 1 Championship game
    """

    # Final Four matchup structure: (region_a, region_b)
    FINAL_FOUR_MATCHUPS = [
        ("East", "West"),     # East champion vs West champion
        ("Midwest", "South"),  # Midwest champion vs South champion
    ]

    def __init__(self, model, n_simulations: int = 50_000):
        """
        Args:
            model: MarchMadnessModel instance for win probability prediction
            n_simulations: Number of Monte Carlo iterations
        """
        self.model = model
        self.n_simulations = n_simulations
        self.bracket = build_bracket_from_data()

        # Results storage
        self.round_reach_counts: dict = {}    # team → round → count
        self.champion_counts: dict = {}        # team → count
        self.simulation_results: list = []    # full bracket for each sim

    def _win_prob(self, team_a: Team, team_b: Team, round_num: int) -> float:
        """Get win probability for team_a vs team_b in given round."""
        result = self.model.predict(team_a.name, team_b.name, round_num)
        return result["p_a_wins"]

    def _simulate_region(self, region_name: str,
                          region_games: list,
                          rng: np.random.Generator) -> Team:
        """
        Simulate a single region through 3 rounds to determine regional champion.

        Round 1 (R64): 8 games → 8 winners
        Round 2 (R32): 4 games → 4 winners
        Round 3 (S16): 2 games → 2 winners
        Round 4 (E8):  1 game  → 1 regional champion
        """
        # Round 1: 8 first-round games
        round1_winners = []
        for team_a, team_b in region_games:
            p = self._win_prob(team_a, team_b, round_num=1)
            winner = team_a if rng.random() < p else team_b
            round1_winners.append(winner)

        # Round 2 (R32): adjacent pods meet
        # Standard NCAA bracket: game N winner plays game N+1 winner within same pod
        r2_matchups = [
            (round1_winners[0], round1_winners[1]),  # 1/16 winner vs 8/9 winner
            (round1_winners[2], round1_winners[3]),  # 5/12 winner vs 4/13 winner
            (round1_winners[4], round1_winners[5]),  # 6/11 winner vs 3/14 winner
            (round1_winners[6], round1_winners[7]),  # 7/10 winner vs 2/15 winner
        ]
        round2_winners = []
        for team_a, team_b in r2_matchups:
            p = self._win_prob(team_a, team_b, round_num=2)
            winner = team_a if rng.random() < p else team_b
            round2_winners.append(winner)

        # Round 3 (Sweet 16)
        r3_matchups = [
            (round2_winners[0], round2_winners[1]),  # top half
            (round2_winners[2], round2_winners[3]),  # bottom half
        ]
        round3_winners = []
        for team_a, team_b in r3_matchups:
            p = self._win_prob(team_a, team_b, round_num=3)
            winner = team_a if rng.random() < p else team_b
            round3_winners.append(winner)

        # Round 4 (Elite 8) — Regional Final
        team_a, team_b = round3_winners[0], round3_winners[1]
        p = self._win_prob(team_a, team_b, round_num=4)
        regional_champion = team_a if rng.random() < p else team_b

        return regional_champion

    def _simulate_full_bracket(self, rng: np.random.Generator) -> dict:
        """
        Simulate the entire tournament once.

        Returns:
            Dict mapping (round_num, team_name) → won (True/False)
        """
        results = {}

        # Simulate all 4 regions
        regional_champions = {}
        for region_name, region_games in self.bracket.items():
            champ = self._simulate_region(region_name, region_games, rng)
            regional_champions[region_name] = champ

        # Final Four (Round 5)
        ff_winners = []
        for region_a, region_b in self.FINAL_FOUR_MATCHUPS:
            team_a = regional_champions[region_a]
            team_b = regional_champions[region_b]
            p = self._win_prob(team_a, team_b, round_num=5)
            winner = team_a if rng.random() < p else team_b
            ff_winners.append(winner)
            results[f"ff_{region_a}_{region_b}"] = winner.name

        # Championship (Round 6)
        team_a, team_b = ff_winners[0], ff_winners[1]
        p = self._win_prob(team_a, team_b, round_num=6)
        champion = team_a if rng.random() < p else team_b
        results["champion"] = champion.name

        return results

    def run(self, verbose: bool = True) -> "SimulationResults":
        """
        Run all Monte Carlo simulations.

        Returns:
            SimulationResults object with probability distributions
        """
        if verbose:
            print(f"\nRunning {self.n_simulations:,} tournament simulations...")

        rng = np.random.default_rng(42)

        # Track which round each team reaches in each sim
        # team_name → {1: count_reached_r64, 2: count_reached_r32, ...}
        reach_counts = defaultdict(lambda: defaultdict(int))
        champion_counts = defaultdict(int)

        # For the detailed round-by-round tracking, we need a more granular sim
        # Use _run_detailed_simulations for full tracking
        detailed_results = self._run_detailed_simulations(rng, verbose)

        return SimulationResults(
            detailed_results,
            self.n_simulations,
            self.bracket
        )

    def _run_detailed_simulations(self, rng: np.random.Generator,
                                   verbose: bool = True) -> dict:
        """
        Run detailed simulations tracking each team's round-by-round progress.

        Returns:
            Dict: team_name → {round: count} for all rounds
        """
        reach_counts = defaultdict(lambda: defaultdict(int))

        # Pre-compute all first-round win probabilities (avoid recomputing each sim)
        round1_probs = {}
        for region_name, region_games in self.bracket.items():
            region_probs = []
            for team_a, team_b in region_games:
                p = self._win_prob(team_a, team_b, round_num=1)
                region_probs.append((team_a, team_b, p))
            round1_probs[region_name] = region_probs

        # All teams reach round 1
        for region_name, games in self.bracket.items():
            for team_a, team_b in games:
                reach_counts[team_a.name][1] += self.n_simulations
                reach_counts[team_b.name][1] += self.n_simulations

        # Run simulations
        progress_interval = self.n_simulations // 10
        for sim_idx in range(self.n_simulations):
            if verbose and sim_idx % progress_interval == 0:
                pct = sim_idx / self.n_simulations * 100
                print(f"  Progress: {pct:.0f}%  ({sim_idx:,}/{self.n_simulations:,})",
                      end="\r")

            # Simulate all regions
            regional_champs = {}
            for region_name, region_games in self.bracket.items():
                probs = round1_probs[region_name]

                # Round 1
                r1_winners = []
                for team_a, team_b, p in probs:
                    winner = team_a if rng.random() < p else team_b
                    reach_counts[winner.name][2] += 1
                    r1_winners.append(winner)

                # Round 2 (R32): adjacent pods
                r2_matchups = [
                    (r1_winners[0], r1_winners[1]),  # 1/16 vs 8/9
                    (r1_winners[2], r1_winners[3]),  # 5/12 vs 4/13
                    (r1_winners[4], r1_winners[5]),  # 6/11 vs 3/14
                    (r1_winners[6], r1_winners[7]),  # 7/10 vs 2/15
                ]
                r2_winners = []
                for team_a, team_b in r2_matchups:
                    p = self._win_prob(team_a, team_b, round_num=2)
                    winner = team_a if rng.random() < p else team_b
                    reach_counts[winner.name][3] += 1  # Reached Sweet 16
                    r2_winners.append(winner)

                # Round 3 (Sweet 16)
                r3_matchups = [
                    (r2_winners[0], r2_winners[1]),
                    (r2_winners[2], r2_winners[3]),
                ]
                r3_winners = []
                for team_a, team_b in r3_matchups:
                    p = self._win_prob(team_a, team_b, round_num=3)
                    winner = team_a if rng.random() < p else team_b
                    reach_counts[winner.name][4] += 1  # Reached Elite 8
                    r3_winners.append(winner)

                # Round 4 (Elite 8 / Regional Final)
                team_a, team_b = r3_winners[0], r3_winners[1]
                p = self._win_prob(team_a, team_b, round_num=4)
                regional_champ = team_a if rng.random() < p else team_b
                reach_counts[regional_champ.name][5] += 1  # Reached Final Four
                regional_champs[region_name] = regional_champ

            # Final Four (Round 5)
            ff_winners = []
            for region_a, region_b in self.FINAL_FOUR_MATCHUPS:
                team_a = regional_champs[region_a]
                team_b = regional_champs[region_b]
                p = self._win_prob(team_a, team_b, round_num=5)
                ff_winner = team_a if rng.random() < p else team_b
                reach_counts[ff_winner.name][6] += 1  # Reached Championship
                ff_winners.append(ff_winner)

            # Championship (Round 6)
            team_a, team_b = ff_winners[0], ff_winners[1]
            p = self._win_prob(team_a, team_b, round_num=6)
            champion = team_a if rng.random() < p else team_b
            reach_counts[champion.name][7] += 1  # Won Championship

        if verbose:
            print(f"  Progress: 100%  ({self.n_simulations:,}/{self.n_simulations:,})")
            print(f"  Simulations complete!")

        return dict(reach_counts)


# =============================================================================
# RESULTS ANALYSIS
# =============================================================================

class SimulationResults:
    """
    Analyzes and formats Monte Carlo simulation results.
    """

    ROUND_LABELS = {
        1: "R64 (in tournament)",
        2: "Round of 32",
        3: "Sweet 16",
        4: "Elite 8",
        5: "Final Four",
        6: "Championship Game",
        7: "Champion",
    }

    def __init__(self, reach_counts: dict, n_sims: int, bracket: dict):
        self.reach_counts = reach_counts
        self.n_sims = n_sims
        self.bracket = bracket

        # Build probability dict
        self.probabilities = {}
        for team_name, round_counts in reach_counts.items():
            self.probabilities[team_name] = {
                round_num: count / n_sims
                for round_num, count in round_counts.items()
            }

    def get_prob(self, team_name: str, round_num: int) -> float:
        """Get probability of team reaching a specific round."""
        return self.probabilities.get(team_name, {}).get(round_num, 0.0)

    def champion_probs(self) -> list:
        """Get sorted list of (team, championship_probability)."""
        champs = [
            (team, self.get_prob(team, 7))
            for team in self.probabilities
            if self.get_prob(team, 7) > 0
        ]
        return sorted(champs, key=lambda x: x[1], reverse=True)

    def final_four_probs(self) -> list:
        """Get sorted list of (team, final_four_probability)."""
        ff = [
            (team, self.get_prob(team, 5))
            for team in self.probabilities
            if self.get_prob(team, 5) > 0
        ]
        return sorted(ff, key=lambda x: x[1], reverse=True)

    def get_region_probabilities(self, region: str) -> list:
        """Get all teams in a region sorted by championship probability."""
        teams = [
            (team, probs)
            for team, probs in self.probabilities.items()
            if any(probs)
        ]

        region_teams = []
        for region_name, region_games in self.bracket.items():
            if region_name == region:
                for team_a, team_b in region_games:
                    for team in [team_a, team_b]:
                        if team.name in self.probabilities:
                            region_teams.append((
                                team,
                                self.probabilities[team.name]
                            ))

        return sorted(region_teams, key=lambda x: x[1].get(7, 0), reverse=True)

    def get_most_likely_bracket(self, model) -> dict:
        """
        Determine the most likely bracket by picking the highest-probability
        winner at each game node (greedy most-likely path).

        This is the "chalk" bracket — pick the favorite at every step.
        For upset-picking strategy, see get_optimal_bracket().
        """
        from march_madness.data import ROUND_NAMES

        bracket_picks = {}

        # Round 1 picks
        for region_name, region_games in self.bracket.items():
            round1_winners = []
            for i, (team_a, team_b) in enumerate(region_games):
                result = model.predict(team_a.name, team_b.name, round_num=1)
                winner_name = result["predicted_winner"]
                winner = team_a if team_a.name == winner_name else team_b
                bracket_picks[f"{region_name}_R1_G{i+1}"] = {
                    "game": f"#{team_a.seed} {team_a.name} vs #{team_b.seed} {team_b.name}",
                    "pick": winner_name,
                    "seed": winner.seed,
                    "p_win": result["p_a_wins"] if winner_name == team_a.name else result["p_b_wins"],
                    "confidence": result["confidence"],
                }
                round1_winners.append(winner)

            # Round 2 (R32): adjacent pods
            r2_matchups = [
                (round1_winners[0], round1_winners[1]),  # 1/16 vs 8/9
                (round1_winners[2], round1_winners[3]),  # 5/12 vs 4/13
                (round1_winners[4], round1_winners[5]),  # 6/11 vs 3/14
                (round1_winners[6], round1_winners[7]),  # 7/10 vs 2/15
            ]
            round2_winners = []
            for i, (team_a, team_b) in enumerate(r2_matchups):
                result = model.predict(team_a.name, team_b.name, round_num=2)
                winner_name = result["predicted_winner"]
                winner = team_a if team_a.name == winner_name else team_b
                bracket_picks[f"{region_name}_R2_G{i+1}"] = {
                    "game": f"#{team_a.seed} {team_a.name} vs #{team_b.seed} {team_b.name}",
                    "pick": winner_name,
                    "seed": winner.seed,
                    "p_win": result["p_a_wins"] if winner_name == team_a.name else result["p_b_wins"],
                    "confidence": result["confidence"],
                }
                round2_winners.append(winner)

            # Sweet 16
            r3_matchups = [
                (round2_winners[0], round2_winners[1]),
                (round2_winners[2], round2_winners[3]),
            ]
            round3_winners = []
            for i, (team_a, team_b) in enumerate(r3_matchups):
                result = model.predict(team_a.name, team_b.name, round_num=3)
                winner_name = result["predicted_winner"]
                winner = team_a if team_a.name == winner_name else team_b
                bracket_picks[f"{region_name}_S16_G{i+1}"] = {
                    "game": f"#{team_a.seed} {team_a.name} vs #{team_b.seed} {team_b.name}",
                    "pick": winner_name,
                    "seed": winner.seed,
                    "p_win": result["p_a_wins"] if winner_name == team_a.name else result["p_b_wins"],
                    "confidence": result["confidence"],
                }
                round3_winners.append(winner)

            # Elite 8
            team_a, team_b = round3_winners[0], round3_winners[1]
            result = model.predict(team_a.name, team_b.name, round_num=4)
            winner_name = result["predicted_winner"]
            winner = team_a if team_a.name == winner_name else team_b
            bracket_picks[f"{region_name}_E8"] = {
                "game": f"#{team_a.seed} {team_a.name} vs #{team_b.seed} {team_b.name}",
                "pick": winner_name,
                "seed": winner.seed,
                "p_win": result["p_a_wins"] if winner_name == team_a.name else result["p_b_wins"],
                "confidence": result["confidence"],
            }
            bracket_picks[f"{region_name}_champion"] = winner

        # Final Four
        ff_matchups = TournamentSimulator.FINAL_FOUR_MATCHUPS
        ff_winners = []
        for region_a, region_b in ff_matchups:
            team_a = bracket_picks[f"{region_a}_champion"]
            team_b = bracket_picks[f"{region_b}_champion"]
            result = model.predict(team_a.name, team_b.name, round_num=5)
            winner_name = result["predicted_winner"]
            winner = team_a if team_a.name == winner_name else team_b
            bracket_picks[f"FF_{region_a}_{region_b}"] = {
                "game": f"#{team_a.seed} {team_a.name} ({team_a.region}) vs "
                        f"#{team_b.seed} {team_b.name} ({team_b.region})",
                "pick": winner_name,
                "seed": winner.seed,
                "p_win": result["p_a_wins"] if winner_name == team_a.name else result["p_b_wins"],
                "confidence": result["confidence"],
            }
            ff_winners.append(winner)

        # Championship
        team_a, team_b = ff_winners[0], ff_winners[1]
        result = model.predict(team_a.name, team_b.name, round_num=6)
        winner_name = result["predicted_winner"]
        winner = team_a if team_a.name == winner_name else team_b
        bracket_picks["Championship"] = {
            "game": f"#{team_a.seed} {team_a.name} vs #{team_b.seed} {team_b.name}",
            "pick": winner_name,
            "seed": winner.seed,
            "p_win": result["p_a_wins"] if winner_name == team_a.name else result["p_b_wins"],
            "confidence": result["confidence"],
        }
        bracket_picks["Champion"] = winner

        return bracket_picks

    def print_championship_odds(self, top_n: int = 20):
        """Print championship odds for top N teams."""
        print("\n" + "=" * 60)
        print("   CHAMPIONSHIP PROBABILITY — 2026 NCAA TOURNAMENT")
        print("=" * 60)
        print(f"{'Rank':<5} {'Team':<22} {'Seed':<6} {'Champion':>10} "
              f"{'Final 4':>10} {'Elite 8':>10} {'Sweet 16':>10}")
        print("-" * 75)

        champs = self.champion_probs()
        for rank, (team_name, p_champ) in enumerate(champs[:top_n], 1):
            p_ff = self.get_prob(team_name, 5)
            p_e8 = self.get_prob(team_name, 4)
            p_s16 = self.get_prob(team_name, 3)

            # Get seed from bracket
            seed = "?"
            for region_games in self.bracket.values():
                for team_a, team_b in region_games:
                    if team_a.name == team_name:
                        seed = f"#{team_a.seed}"
                        break
                    if team_b.name == team_name:
                        seed = f"#{team_b.seed}"
                        break

            print(f"{rank:<5} {team_name:<22} {seed:<6} "
                  f"{p_champ:>9.1%}  {p_ff:>9.1%}  {p_e8:>9.1%}  {p_s16:>9.1%}")

        print("=" * 75)
