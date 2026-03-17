"""
2026 NCAA Tournament Data
=========================
Complete bracket structure, team efficiency ratings, and historical seed win rates.

Efficiency ratings are approximated from KenPom rank order, public reporting on
AdjO/AdjD profiles, and historical typical AdjEM values by seed. For improved
accuracy, replace adj_em values with actual KenPom/Torvik data from kenpom.com
or barttorvik.com before running predictions.

Data sources:
- 2026 bracket: NCAA.com Selection Sunday announcement (March 15, 2026)
- KenPom rank estimates: BetMGM, CBS Sports, ESPN reporting (March 2026)
- Historical seed win rates: 1985-2025 NCAA tournament (40 tournaments)
"""

# =============================================================================
# FIRST FOUR GAMES (Dayton, OH — March 17-18, 2026)
# Each tuple: (team1, seed, region_slot, vs_team2) — winner fills bracket slot
# =============================================================================
FIRST_FOUR_2026 = [
    # (team_a, team_b, seed, region, bracket_slot, plays_seed, plays_region_position)
    # 16-seeds in Midwest (winner plays Michigan, #1)
    {"team_a": "UMBC",          "team_b": "Howard",     "seed": 16, "region": "Midwest",
     "slot": "Midwest_16",      "plays": "Michigan",    "plays_seed": 1,  "date": "Mar 17"},
    # 11-seeds in West (winner plays BYU, #6)
    {"team_a": "Texas",         "team_b": "NC State",   "seed": 11, "region": "West",
     "slot": "West_11",         "plays": "BYU",         "plays_seed": 6,  "date": "Mar 17"},
    # 16-seeds in South (winner plays Florida, #1)
    {"team_a": "Prairie View",  "team_b": "Lehigh",     "seed": 16, "region": "South",
     "slot": "South_16",        "plays": "Florida",     "plays_seed": 1,  "date": "Mar 18"},
    # 11-seeds in Midwest (winner plays Tennessee, #6)
    {"team_a": "Miami OH",      "team_b": "SMU",        "seed": 11, "region": "Midwest",
     "slot": "Midwest_11",      "plays": "Tennessee",   "plays_seed": 6,  "date": "Mar 18"},
]

# =============================================================================
# 2026 BRACKET — First Round Matchups
# Format: (seed_a, team_a, seed_b, team_b)
# Upper seed (lower number) listed first
# =============================================================================
BRACKET_2026 = {
    "East": [
        # Bracket position → (high_seed, team, low_seed, team)
        (1,  "Duke",          16, "Siena"),
        (8,  "Ohio State",     9, "TCU"),
        (5,  "St. Johns",     12, "Northern Iowa"),
        (4,  "Kansas",        13, "Cal Baptist"),
        (6,  "Louisville",    11, "South Florida"),
        (3,  "Michigan State",14, "North Dakota State"),
        (7,  "UCLA",          10, "UCF"),
        (2,  "UConn",         15, "Furman"),
    ],
    "West": [
        (1,  "Arizona",       16, "LIU"),
        (8,  "Villanova",      9, "Utah State"),
        (5,  "Wisconsin",     12, "High Point"),
        (4,  "Arkansas",      13, "Hawaii"),
        (6,  "BYU",           11, "FF_West_11"),      # First Four winner
        (3,  "Gonzaga",       14, "Kennesaw State"),
        (7,  "Miami FL",      10, "Missouri"),
        (2,  "Purdue",        15, "Queens"),
    ],
    "Midwest": [
        (1,  "Michigan",      16, "FF_Midwest_16"),   # First Four winner
        (8,  "Georgia",        9, "Saint Louis"),
        (5,  "Texas Tech",    12, "Akron"),
        (4,  "Alabama",       13, "Hofstra"),
        (6,  "Tennessee",     11, "FF_Midwest_11"),   # First Four winner
        (3,  "Virginia",      14, "Wright State"),
        (7,  "Kentucky",      10, "Santa Clara"),
        (2,  "Iowa State",    15, "Tennessee State"),
    ],
    "South": [
        (1,  "Florida",       16, "FF_South_16"),     # First Four winner
        (8,  "Clemson",        9, "Iowa"),
        (5,  "Vanderbilt",    12, "McNeese"),
        (4,  "Nebraska",      13, "Troy"),
        (6,  "North Carolina",11, "VCU"),
        (3,  "Illinois",      14, "Penn"),
        (7,  "Saint Marys",   10, "Texas AM"),
        (2,  "Houston",       15, "Idaho"),
    ],
}

# First Four expected winners (for "most likely bracket" predictions)
# Based on efficiency ratings: pick higher-rated team
FIRST_FOUR_EXPECTED_WINNERS = {
    "FF_Midwest_16": "UMBC",        # UMBC slight edge over Howard
    "FF_West_11":    "NC State",    # NC State edge over Texas
    "FF_South_16":   "Lehigh",      # Lehigh slight edge over Prairie View
    "FF_Midwest_11": "Miami OH",    # Miami OH (31-1) strong favorite
}

# =============================================================================
# TEAM EFFICIENCY RATINGS — 2026
# =============================================================================
# adj_em: Adjusted Efficiency Margin (offense - defense per 100 possessions)
# adj_o:  Adjusted Offensive Efficiency (pts scored per 100 possessions)
# adj_d:  Adjusted Defensive Efficiency (pts allowed per 100 possessions)
# kenpom_rank: Approximate KenPom ranking
# seed: Tournament seed
# region: Tournament region
#
# NOTE: These are approximated from public reporting. Replace with actual
# KenPom/Torvik data at kenpom.com or barttorvik.com for improved accuracy.
# Typical AdjEM range: #1 seed ~27-35, #16 seed ~-7 to ~-2
# =============================================================================
TEAM_RATINGS = {
    # --- EAST REGION ---
    "Duke": {
        "seed": 1, "region": "East", "record": "32-2",
        "kenpom_rank": 1, "adj_em": 34.5, "adj_o": 125.0, "adj_d": 90.5,
        "notes": "#1 overall seed. Cameron Boozer. #4 AdjO, #2 AdjD (KenPom).",
    },
    "Ohio State": {
        "seed": 8, "region": "East", "record": "21-12",
        "kenpom_rank": 31, "adj_em": 11.0, "adj_o": 108.0, "adj_d": 97.0,
    },
    "TCU": {
        "seed": 9, "region": "East", "record": "22-11",
        "kenpom_rank": 34, "adj_em": 9.5, "adj_o": 106.0, "adj_d": 96.5,
    },
    "St. Johns": {
        "seed": 5, "region": "East", "record": "28-6",
        "kenpom_rank": 20, "adj_em": 18.5, "adj_o": 113.0, "adj_d": 94.5,
        "notes": "Rick Pitino. National champion coach.",
    },
    "Northern Iowa": {
        "seed": 12, "region": "East", "record": "23-12",
        "kenpom_rank": 53, "adj_em": 2.0, "adj_o": 104.0, "adj_d": 102.0,
    },
    "Kansas": {
        "seed": 4, "region": "East", "record": "23-10",
        "kenpom_rank": 16, "adj_em": 20.5, "adj_o": 114.0, "adj_d": 93.5,
        "notes": "Bill Self. National champion coach.",
    },
    "Cal Baptist": {
        "seed": 13, "region": "East", "record": "25-8",
        "kenpom_rank": 55, "adj_em": 1.0, "adj_o": 103.5, "adj_d": 102.5,
    },
    "Louisville": {
        "seed": 6, "region": "East", "record": "23-10",
        "kenpom_rank": 23, "adj_em": 15.0, "adj_o": 110.0, "adj_d": 95.0,
        "notes": "Rick Pitino former team. National champion coach currently at St. Johns.",
    },
    "South Florida": {
        "seed": 11, "region": "East", "record": "25-8",
        "kenpom_rank": 46, "adj_em": 3.5, "adj_o": 103.5, "adj_d": 100.0,
    },
    "Michigan State": {
        "seed": 3, "region": "East", "record": "25-7",
        "kenpom_rank": 9, "adj_em": 24.2, "adj_o": 115.0, "adj_d": 90.8,
        "notes": "Tom Izzo. National champion coach.",
    },
    "North Dakota State": {
        "seed": 14, "region": "East", "record": "27-7",
        "kenpom_rank": 59, "adj_em": -1.0, "adj_o": 102.0, "adj_d": 103.0,
    },
    "UCLA": {
        "seed": 7, "region": "East", "record": "23-11",
        "kenpom_rank": 32, "adj_em": 12.5, "adj_o": 109.5, "adj_d": 97.0,
    },
    "UCF": {
        "seed": 10, "region": "East", "record": "21-11",
        "kenpom_rank": 38, "adj_em": 7.5, "adj_o": 106.0, "adj_d": 98.5,
    },
    "UConn": {
        "seed": 2, "region": "East", "record": "29-5",
        "kenpom_rank": 6, "adj_em": 27.0, "adj_o": 116.0, "adj_d": 89.0,
        "notes": "Dan Hurley. 2023, 2024 national champion.",
    },
    "Furman": {
        "seed": 15, "region": "East", "record": "22-12",
        "kenpom_rank": 65, "adj_em": -4.0, "adj_o": 100.0, "adj_d": 104.0,
    },

    # --- WEST REGION ---
    "Arizona": {
        "seed": 1, "region": "West", "record": "32-2",
        "kenpom_rank": 3, "adj_em": 32.1, "adj_o": 122.0, "adj_d": 89.9,
        "notes": "#2 overall seed. Big 12 Champions. #5 AdjO, #3 AdjD.",
    },
    "Villanova": {
        "seed": 8, "region": "West", "record": "24-8",
        "kenpom_rank": 30, "adj_em": 11.5, "adj_o": 108.0, "adj_d": 96.5,
    },
    "Utah State": {
        "seed": 9, "region": "West", "record": "28-6",
        "kenpom_rank": 33, "adj_em": 10.0, "adj_o": 109.0, "adj_d": 99.0,
    },
    "Wisconsin": {
        "seed": 5, "region": "West", "record": "24-10",
        "kenpom_rank": 24, "adj_em": 16.5, "adj_o": 110.0, "adj_d": 93.5,
    },
    "High Point": {
        "seed": 12, "region": "West", "record": "30-4",
        "kenpom_rank": 50, "adj_em": 1.5, "adj_o": 106.0, "adj_d": 104.5,
        "notes": "30-4 record. Dangerous 12-seed. Mid-major star.",
    },
    "Arkansas": {
        "seed": 4, "region": "West", "record": "26-8",
        "kenpom_rank": 17, "adj_em": 20.0, "adj_o": 116.0, "adj_d": 96.0,
    },
    "Hawaii": {
        "seed": 13, "region": "West", "record": "24-8",
        "kenpom_rank": 54, "adj_em": -0.5, "adj_o": 103.0, "adj_d": 103.5,
    },
    "BYU": {
        "seed": 6, "region": "West", "record": "23-11",
        "kenpom_rank": 28, "adj_em": 14.5, "adj_o": 111.0, "adj_d": 96.5,
    },
    "FF_West_11": {
        "seed": 11, "region": "West", "record": "20-13",
        "kenpom_rank": 45, "adj_em": 6.0, "adj_o": 105.0, "adj_d": 99.0,
        "notes": "First Four winner: Texas vs NC State",
    },
    "Gonzaga": {
        "seed": 3, "region": "West", "record": "30-3",
        "kenpom_rank": 11, "adj_em": 23.0, "adj_o": 119.0, "adj_d": 96.0,
    },
    "Kennesaw State": {
        "seed": 14, "region": "West", "record": "21-13",
        "kenpom_rank": 62, "adj_em": -2.5, "adj_o": 101.0, "adj_d": 103.5,
    },
    "Miami FL": {
        "seed": 7, "region": "West", "record": "25-8",
        "kenpom_rank": 27, "adj_em": 13.0, "adj_o": 108.0, "adj_d": 95.0,
    },
    "Missouri": {
        "seed": 10, "region": "West", "record": "20-12",
        "kenpom_rank": 39, "adj_em": 7.0, "adj_o": 106.0, "adj_d": 99.0,
    },
    "Purdue": {
        "seed": 2, "region": "West", "record": "27-8",
        "kenpom_rank": 8, "adj_em": 25.8, "adj_o": 124.0, "adj_d": 98.2,
        "notes": "#2 AdjO nationally. High-tempo offensive team.",
    },
    "Queens": {
        "seed": 15, "region": "West", "record": "21-13",
        "kenpom_rank": 66, "adj_em": -4.5, "adj_o": 99.5, "adj_d": 104.0,
        "notes": "First-ever tournament appearance in first year of eligibility.",
    },

    # --- MIDWEST REGION ---
    "Michigan": {
        "seed": 1, "region": "Midwest", "record": "31-3",
        "kenpom_rank": 2, "adj_em": 33.2, "adj_o": 118.5, "adj_d": 85.3,
        "notes": "#3 overall seed. #1 defense in nation. #8 AdjO. Betting favorite +325.",
    },
    "Georgia": {
        "seed": 8, "region": "Midwest", "record": "22-10",
        "kenpom_rank": 36, "adj_em": 10.5, "adj_o": 107.0, "adj_d": 96.5,
    },
    "Saint Louis": {
        "seed": 9, "region": "Midwest", "record": "28-5",
        "kenpom_rank": 35, "adj_em": 9.0, "adj_o": 107.0, "adj_d": 98.0,
    },
    "Texas Tech": {
        "seed": 5, "region": "Midwest", "record": "22-10",
        "kenpom_rank": 22, "adj_em": 17.5, "adj_o": 108.0, "adj_d": 90.5,
    },
    "Akron": {
        "seed": 12, "region": "Midwest", "record": "29-5",
        "kenpom_rank": 48, "adj_em": 2.5, "adj_o": 105.0, "adj_d": 102.5,
        "notes": "29-5 record. Strong mid-major 12-seed.",
    },
    "Alabama": {
        "seed": 4, "region": "Midwest", "record": "23-9",
        "kenpom_rank": 15, "adj_em": 21.0, "adj_o": 115.0, "adj_d": 94.0,
    },
    "Hofstra": {
        "seed": 13, "region": "Midwest", "record": "24-10",
        "kenpom_rank": 56, "adj_em": 0.5, "adj_o": 102.5, "adj_d": 102.0,
    },
    "Tennessee": {
        "seed": 6, "region": "Midwest", "record": "22-11",
        "kenpom_rank": 21, "adj_em": 16.0, "adj_o": 109.0, "adj_d": 93.0,
    },
    "FF_Midwest_11": {
        "seed": 11, "region": "Midwest", "record": "31-1",
        "kenpom_rank": 44, "adj_em": 4.5, "adj_o": 107.0, "adj_d": 102.5,
        "notes": "First Four winner: Miami OH vs SMU. Miami OH went 31-1 in regular season.",
    },
    "Virginia": {
        "seed": 3, "region": "Midwest", "record": "29-5",
        "kenpom_rank": 13, "adj_em": 22.5, "adj_o": 111.0, "adj_d": 88.5,
    },
    "Wright State": {
        "seed": 14, "region": "Midwest", "record": "23-11",
        "kenpom_rank": 57, "adj_em": -2.0, "adj_o": 102.0, "adj_d": 104.0,
    },
    "Kentucky": {
        "seed": 7, "region": "Midwest", "record": "21-13",
        "kenpom_rank": 25, "adj_em": 14.0, "adj_o": 110.0, "adj_d": 96.0,
    },
    "Santa Clara": {
        "seed": 10, "region": "Midwest", "record": "26-8",
        "kenpom_rank": 37, "adj_em": 8.0, "adj_o": 107.0, "adj_d": 99.0,
    },
    "Iowa State": {
        "seed": 2, "region": "Midwest", "record": "27-7",
        "kenpom_rank": 7, "adj_em": 26.5, "adj_o": 113.0, "adj_d": 86.5,
        "notes": "Elite defense. Iowa State defensive system.",
    },
    "Tennessee State": {
        "seed": 15, "region": "Midwest", "record": "23-9",
        "kenpom_rank": 63, "adj_em": -3.0, "adj_o": 100.5, "adj_d": 103.5,
        "notes": "First tournament appearance since 1994.",
    },
    "FF_Midwest_16": {
        "seed": 16, "region": "Midwest", "record": "24-8",
        "kenpom_rank": 61, "adj_em": -2.5, "adj_o": 101.0, "adj_d": 103.5,
        "notes": "First Four winner: UMBC vs Howard",
    },

    # --- SOUTH REGION ---
    "Florida": {
        "seed": 1, "region": "South", "record": "26-7",
        "kenpom_rank": 4, "adj_em": 30.5, "adj_o": 119.5, "adj_d": 89.0,
        "notes": "Defending national champion. Thomas Haugh 17.1 ppg. Betting +600.",
    },
    "Clemson": {
        "seed": 8, "region": "South", "record": "24-10",
        "kenpom_rank": 29, "adj_em": 12.0, "adj_o": 107.0, "adj_d": 95.0,
    },
    "Iowa": {
        "seed": 9, "region": "South", "record": "21-12",
        "kenpom_rank": 36, "adj_em": 8.5, "adj_o": 108.0, "adj_d": 99.5,
    },
    "Vanderbilt": {
        "seed": 5, "region": "South", "record": "26-8",
        "kenpom_rank": 18, "adj_em": 19.5, "adj_o": 112.0, "adj_d": 92.5,
    },
    "McNeese": {
        "seed": 12, "region": "South", "record": "28-5",
        "kenpom_rank": 47, "adj_em": 3.0, "adj_o": 106.0, "adj_d": 103.0,
        "notes": "28-5. Strong mid-major. Dangerous 12-seed.",
    },
    "Nebraska": {
        "seed": 4, "region": "South", "record": "26-6",
        "kenpom_rank": 14, "adj_em": 21.8, "adj_o": 113.5, "adj_d": 91.7,
    },
    "Troy": {
        "seed": 13, "region": "South", "record": "22-11",
        "kenpom_rank": 53, "adj_em": 0.0, "adj_o": 103.0, "adj_d": 103.0,
    },
    "North Carolina": {
        "seed": 6, "region": "South", "record": "24-8",
        "kenpom_rank": 22, "adj_em": 15.5, "adj_o": 113.0, "adj_d": 97.5,
    },
    "VCU": {
        "seed": 11, "region": "South", "record": "27-7",
        "kenpom_rank": 45, "adj_em": 4.0, "adj_o": 103.5, "adj_d": 99.5,
        "notes": "27-7. Strong defensive team. Annual tournament darling.",
    },
    "Illinois": {
        "seed": 3, "region": "South", "record": "24-8",
        "kenpom_rank": 10, "adj_em": 23.5, "adj_o": 114.0, "adj_d": 90.5,
    },
    "Penn": {
        "seed": 14, "region": "South", "record": "18-11",
        "kenpom_rank": 60, "adj_em": -1.5, "adj_o": 101.5, "adj_d": 103.0,
        "notes": "Ivy League champion.",
    },
    "Saint Marys": {
        "seed": 7, "region": "South", "record": "27-5",
        "kenpom_rank": 26, "adj_em": 13.5, "adj_o": 109.0, "adj_d": 95.5,
    },
    "Texas AM": {
        "seed": 10, "region": "South", "record": "21-11",
        "kenpom_rank": 40, "adj_em": 6.5, "adj_o": 105.0, "adj_d": 98.5,
    },
    "Houston": {
        "seed": 2, "region": "South", "record": "28-6",
        "kenpom_rank": 5, "adj_em": 27.8, "adj_o": 112.0, "adj_d": 84.2,
        "notes": "Sweet 16 / Elite 8 in Houston (near home-court). Kelvin Sampson.",
    },
    "Idaho": {
        "seed": 15, "region": "South", "record": "21-14",
        "kenpom_rank": 64, "adj_em": -3.5, "adj_o": 100.0, "adj_d": 103.5,
        "notes": "First tournament appearance since 1990.",
    },
    "FF_South_16": {
        "seed": 16, "region": "South", "record": "21-16",
        "kenpom_rank": 64, "adj_em": -4.0, "adj_o": 100.0, "adj_d": 104.0,
        "notes": "First Four winner: Prairie View A&M vs Lehigh",
    },

    # --- FIRST FOUR TEAMS (individual ratings before matchup) ---
    "UMBC": {
        "seed": 16, "region": "Midwest", "record": "24-8",
        "kenpom_rank": 60, "adj_em": -2.0, "adj_o": 102.0, "adj_d": 104.0,
    },
    "Howard": {
        "seed": 16, "region": "Midwest", "record": "23-10",
        "kenpom_rank": 63, "adj_em": -3.0, "adj_o": 100.5, "adj_d": 103.5,
    },
    "Texas": {
        "seed": 11, "region": "West", "record": "18-14",
        "kenpom_rank": 42, "adj_em": 5.5, "adj_o": 104.5, "adj_d": 99.0,
    },
    "NC State": {
        "seed": 11, "region": "West", "record": "20-13",
        "kenpom_rank": 41, "adj_em": 6.0, "adj_o": 105.0, "adj_d": 99.0,
    },
    "Prairie View": {
        "seed": 16, "region": "South", "record": "21-11",
        "kenpom_rank": 66, "adj_em": -4.5, "adj_o": 99.5, "adj_d": 104.0,
    },
    "Lehigh": {
        "seed": 16, "region": "South", "record": "18-16",
        "kenpom_rank": 63, "adj_em": -3.5, "adj_o": 100.0, "adj_d": 103.5,
    },
    "Miami OH": {
        "seed": 11, "region": "Midwest", "record": "31-1",
        "kenpom_rank": 44, "adj_em": 4.5, "adj_o": 107.0, "adj_d": 102.5,
        "notes": "31-1 in regular season! MAC tournament runner-up.",
    },
    "SMU": {
        "seed": 11, "region": "Midwest", "record": "20-13",
        "kenpom_rank": 43, "adj_em": 5.0, "adj_o": 104.5, "adj_d": 99.5,
    },
}


# =============================================================================
# HISTORICAL SEED WIN RATES (1985-2025, 40 tournaments)
# P(lower_seed_wins) where lower seed number = better team
# Source: NCAA tournament historical records
# =============================================================================
HISTORICAL_SEED_WIN_RATES = {
    # (favorite_seed, underdog_seed): favorite_win_probability
    (1,  16): 0.993,   # 139-1 all time (UMBC beat Virginia 2018 only upset)
    (2,  15): 0.943,   # ~8 upsets in 160 games
    (3,  14): 0.850,
    (4,  13): 0.793,
    (5,  12): 0.643,   # Famous "5-12 upset" matchup; ~1-2 upsets/year
    (6,  11): 0.629,   # 11-seeds recently very strong (incl. power-conf bubble)
    (7,  10): 0.607,
    (8,   9): 0.479,   # True coin flip; 9-seed has slight all-time edge!
    # Second round (round of 32) historical rates vs common matchups
    (1,   9): 0.840,
    (1,   8): 0.770,
    (2,  10): 0.790,
    (2,   7): 0.730,
    (3,  11): 0.740,
    (3,   6): 0.620,
    (4,  12): 0.690,
    (4,   5): 0.530,
    (1,   5): 0.710,
    (1,   4): 0.620,
    (2,   3): 0.540,
    (1,   2): 0.540,
    (1,   3): 0.590,
    (1,   6): 0.680,
    (1,   7): 0.720,
    (2,   6): 0.660,
    (2,   7): 0.720,
    (2,  11): 0.770,
    (3,   7): 0.620,
    (3,  10): 0.690,
    (4,  13): 0.793,
    (4,   6): 0.570,
}


# =============================================================================
# HISTORICAL TOURNAMENT RESULTS (2015-2025)
# Used for backtesting. Format: list of games per year.
# Each game: (winner_seed, loser_seed, winner_name, loser_name, round)
# Rounds: 1=Round of 64, 2=Round of 32, 3=Sweet 16, 4=Elite 8,
#         5=Final Four, 6=Championship
# =============================================================================
HISTORICAL_RESULTS = {
    2025: {
        "champion": "Florida",  "champion_seed": 1,
        "runner_up": "Houston", "runner_up_seed": 2,
        "final_four": [("Florida", 1), ("Houston", 2), ("Auburn", 4), ("Duke", 1)],
        "notable_upsets": [
            ("Ole Miss", 11, "Iowa State", 2, 2),  # example upsets
        ],
    },
    2024: {
        "champion": "UConn",    "champion_seed": 1,
        "runner_up": "Purdue",  "runner_up_seed": 1,
        "final_four": [("UConn", 1), ("Purdue", 1), ("Alabama", 4), ("NC State", 11)],
        "notable_upsets": [
            ("NC State", 11, "Texas Tech", 2, 3),
            ("NC State", 11, "Marquette", 2, 4),
        ],
    },
    2023: {
        "champion": "UConn",       "champion_seed": 4,
        "runner_up": "San Diego St","runner_up_seed": 5,
        "final_four": [("UConn", 4), ("San Diego St", 5), ("Florida Atlantic", 9), ("Miami", 5)],
        "notable_upsets": [
            ("Princeton", 15, "Arizona", 2, 1),
            ("Furman", 13, "Virginia", 4, 1),
            ("Fairleigh Dickinson", 16, "Purdue", 1, 1),
        ],
    },
    2022: {
        "champion": "Kansas",     "champion_seed": 1,
        "runner_up": "UNC",       "runner_up_seed": 8,
        "final_four": [("Kansas", 1), ("UNC", 8), ("Duke", 2), ("Villanova", 2)],
        "notable_upsets": [
            ("Saint Peter's", 15, "Kentucky", 2, 1),
            ("Saint Peter's", 15, "Murray St", 7, 2),
        ],
    },
    2021: {
        "champion": "Baylor",     "champion_seed": 1,
        "runner_up": "Gonzaga",   "runner_up_seed": 1,
        "final_four": [("Baylor", 1), ("Gonzaga", 1), ("Houston", 2), ("UCLA", 11)],
        "notable_upsets": [
            ("Oral Roberts", 15, "Ohio State", 2, 1),
        ],
    },
    2019: {
        "champion": "Virginia",   "champion_seed": 1,
        "runner_up": "Texas Tech","runner_up_seed": 3,
        "final_four": [("Virginia", 1), ("Texas Tech", 3), ("Auburn", 5), ("Michigan St", 2)],
        "notable_upsets": [
            ("UC Irvine", 13, "Kansas State", 4, 1),
            ("Oregon", 12, "Wisconsin", 5, 1),
        ],
    },
    2018: {
        "champion": "Villanova",  "champion_seed": 1,
        "runner_up": "Michigan",  "runner_up_seed": 3,
        "final_four": [("Villanova", 1), ("Michigan", 3), ("Loyola Chicago", 11), ("Kansas", 1)],
        "notable_upsets": [
            ("UMBC", 16, "Virginia", 1, 1),   # Only #16 over #1 upset in history
            ("Marshall", 13, "Wichita State", 4, 1),
        ],
    },
    2017: {
        "champion": "North Carolina","champion_seed": 1,
        "runner_up": "Gonzaga",    "runner_up_seed": 1,
        "final_four": [("North Carolina", 1), ("Gonzaga", 1), ("Oregon", 3), ("South Carolina", 7)],
        "notable_upsets": [
            ("Xavier", 11, "Maryland", 6, 2),
            ("South Carolina", 7, "Florida", 4, 4),
        ],
    },
    2016: {
        "champion": "Villanova",  "champion_seed": 2,
        "runner_up": "North Carolina","runner_up_seed": 1,
        "final_four": [("Villanova", 2), ("North Carolina", 1), ("Oklahoma", 2), ("Syracuse", 10)],
        "notable_upsets": [
            ("Yale", 12, "Baylor", 5, 1),
            ("Stephen F Austin", 14, "West Virginia", 3, 1),
        ],
    },
    2015: {
        "champion": "Duke",       "champion_seed": 1,
        "runner_up": "Wisconsin", "runner_up_seed": 1,
        "final_four": [("Duke", 1), ("Wisconsin", 1), ("Michigan St", 7), ("Kentucky", 1)],
        "notable_upsets": [
            ("UAB", 14, "Iowa State", 3, 1),
            ("UCLA", 11, "SMU", 6, 1),
        ],
    },
}


# =============================================================================
# BRACKET SCORING (standard ESPN/Yahoo Tournament Challenge rules)
# Points double each round
# =============================================================================
ROUND_POINTS = {
    1: 1,    # Round of 64
    2: 2,    # Round of 32
    3: 4,    # Sweet 16
    4: 8,    # Elite 8
    5: 16,   # Final Four
    6: 32,   # Championship
}

ROUND_NAMES = {
    1: "Round of 64",
    2: "Round of 32 (Second Round)",
    3: "Sweet 16",
    4: "Elite 8",
    5: "Final Four",
    6: "National Championship",
}

# Final Four site: Lucas Oil Stadium, Indianapolis, Indiana
# Championship: April 6, 2026

# =============================================================================
# HOME COURT / VENUE ADJUSTMENTS
# Houston plays Sweet 16 and Elite 8 in Houston (South Region host)
# =============================================================================
VENUE_ADJUSTMENTS = {
    # team: adj_em_bonus for specific rounds
    "Houston": {"rounds": [3, 4], "bonus": 2.5,
                "note": "South Sweet 16/Elite 8 hosted in Houston"},
}
