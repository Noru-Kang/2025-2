"""
grid_search.py

Performs single-parameter grid sweeps across 0..100 with step 0.1 (default)
for the ReflexAgent-style evaluation parameters from `multiAgents.py`.

By default this script will sweep each parameter one at a time (sequentially),
running one game per grid value and writing the results to CSV. This avoids
combinatorial explosion while allowing you to inspect sensitivity per-parameter.

Usage examples:
  # Sweep w1 from 0.0 to 100.0 step 0.1
  python grid_search.py --param w1

  # Sweep each parameter sequentially (all eight weights + GAP)
  python grid_search.py --param all

  # Sweep w1 but only 101 values (step=1.0)
  python grid_search.py --param w1 --start 0 --stop 100 --step 1.0

Notes:
  - Sweeping 0..100 step 0.1 yields 1001 values per parameter (1001 games).
    Sweeping all 8 params sequentially means ~8008 games (plus GAP) — might
    take a long time. Use --step to coarsen if you want fewer games.
  - GAP is treated as integer; when param==GAP the step will be rounded to int
    and the values coerced to int.
"""

import argparse
import csv
import math
import time

import types
import pacman
import layout
import textDisplay
import ghostAgents
from multiAgents import ReflexAgent

# Base/default parameter values copied from multiAgents.py
BASE_PARAMS = {
    'w1': 1.0,
    'w2': 0.1,
    'w3': 0.5,
    'w4': 1.0,
    'w5': 2.0,
    'w6': 200.0,
    'w7': 2.0,
    'w8': 0.0,
    'GAP': 2,
}

E = 1e-05

from util import manhattanDist


def make_eval_fn(weights):
    w1 = weights['w1']
    w2 = weights['w2']
    w3 = weights['w3']
    w4 = weights['w4']
    w5 = weights['w5']
    w6 = weights['w6']
    w7 = weights['w7']
    w8 = weights['w8']
    GAP = int(weights['GAP'])

    def evaluation(self, currentGameState, action):
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()

        # Food
        foodPos = successorGameState.getFood().asList()
        foodDists = [manhattanDist(newPos, i_foodPos) for i_foodPos in foodPos]
        if foodDists:
            f1_score = 1.0 / (min(foodDists) + E)
        else:
            f1_score = 0.0
        f2_score = -1.0 * len(foodPos)
        f_score = w1 * f1_score + w2 * f2_score

        # Capsule
        capsulePos = successorGameState.getCapsules()
        if capsulePos:
            capDists = [manhattanDist(newPos, c) for c in capsulePos]
            c1_score = 1.0 / (min(capDists) + E)
        else:
            c1_score = 0.0
        c2_score = -1.0 * len(capsulePos)
        c_score = w3 * c1_score + w4 * c2_score

        # Ghosts
        ghostStates = successorGameState.getGhostStates()
        ghostPos = successorGameState.getGhostPositions()
        g1_score = g2_score = g3_score = 0.0
        for i, pos in enumerate(ghostPos):
            dist = manhattanDist(newPos, pos)
            scaredTimer = ghostStates[i].scaredTimer
            if scaredTimer > 0:
                g1_score += 1.0 / (dist + E)
            else:
                if dist <= GAP:
                    g2_score += -1.0
                else:
                    g3_score += (-1.0) / (dist + E)
        g_score = w5 * g1_score + w6 * g2_score + w7 * g3_score

        # Action penalty
        a1_score = -1.0 if action == 'Stop' or action == 'STOP' else 0.0
        a_score = w8 * a1_score

        score = successorGameState.getScore() + f_score + c_score + g_score + a_score
        return score

    return evaluation


def run_game_with_weights(weights, layout_name='testClassic', numGhosts=4, timeout=30):
    pac_agent = ReflexAgent()
    eval_func = make_eval_fn(weights)
    pac_agent.evaluationFunction = types.MethodType(eval_func, pac_agent)

    ghosts = [ghostAgents.RandomGhost(i + 1) for i in range(numGhosts)]
    display = textDisplay.NullGraphics()
    L = layout.getLayout(layout_name)
    games = pacman.runGames(L, pac_agent, ghosts, display, numGames=1, record=False, numTraining=0, catchExceptions=False, timeout=timeout)
    if len(games) > 0:
        return games[0].state.getScore(), games[0].state.isWin()
    return 0.0, False


def frange(start, stop, step):
    """Floating range inclusive of stop if (stop-start) is multiple of step."""
    values = []
    x = start
    # guard against floating point rounding problems
    n = int(math.floor((stop - start) / step + 0.5))
    for i in range(n + 1):
        values.append(start + i * step)
    # maybe include stop exactly
    if abs(values[-1] - stop) > 1e-9 and values[-1] < stop:
        values.append(stop)
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--param', type=str, default='w1',
                        help='Parameter to sweep (w1,w2,w3,w4,w5,w6,w7,w8,GAP or all)')
    parser.add_argument('--start', type=float, default=0.0)
    parser.add_argument('--stop', type=float, default=100.0)
    parser.add_argument('--step', type=float, default=0.1)
    parser.add_argument('--layout', type=str, default='testClassic')
    parser.add_argument('--out', type=str, default='grid_search_results.csv')
    parser.add_argument('--numGhosts', type=int, default=4)
    parser.add_argument('--timeout', type=int, default=30)
    args = parser.parse_args()

    params_to_sweep = [args.param]
    if args.param == 'all':
        params_to_sweep = ['w1','w2','w3','w4','w5','w6','w7','w8','GAP']

    total_runs = 0
    for p in params_to_sweep:
        if p == 'GAP':
            # integer sweep
            start = int(round(args.start))
            stop = int(round(args.stop))
            step = max(1, int(round(args.step)))
            count = ((stop - start) // step) + 1
        else:
            start = args.start
            stop = args.stop
            step = args.step
            count = int(math.floor((stop - start) / step + 0.5)) + 1
        total_runs += count

    print(f"Planned runs (sequential): {total_runs} games. This may take a long time.")
    confirm = input('Proceed? (y/N): ')
    if confirm.lower() != 'y':
        print('Aborted by user.')
        return

    fieldnames = ['param','value','score','win'] + list(BASE_PARAMS.keys())
    # Track best result across all runs
    best = None  # tuple: (score, param, value, weights, win, run_idx)

    with open(args.out, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        run_idx = 0
        start_time = time.time()
        for p in params_to_sweep:
            print('\nSweeping param:', p)
            if p == 'GAP':
                values = list(range(int(args.start), int(args.stop) + 1, max(1, int(round(args.step)))))
            else:
                values = frange(args.start, args.stop, args.step)

            for v in values:
                weights = BASE_PARAMS.copy()
                # cast appropriately
                if p == 'GAP':
                    weights[p] = int(v)
                else:
                    weights[p] = float(v)

                score, win = run_game_with_weights(weights, layout_name=args.layout, numGhosts=args.numGhosts, timeout=args.timeout)
                row = {'param': p, 'value': v, 'score': score, 'win': win}
                row.update(weights)
                writer.writerow(row)

                # update best
                run_idx += 1
                if best is None or score > best[0]:
                    best = (score, p, v, weights.copy(), win, run_idx)

                if run_idx % 10 == 0:
                    elapsed = time.time() - start_time
                    print(f"{run_idx}/{total_runs} runs done, elapsed {elapsed:.1f}s")

    print('Grid search finished. Results written to', args.out)

    # Print concise best-summary at the end
    if best is not None:
        best_score, best_param, best_value, best_weights, best_win, best_run = best
        print('\nBest result:')
        print(f"  run #{best_run}: param={best_param}, value={best_value}, score={best_score}, win={best_win}")
        print('  weights:')
        # pretty print a few key weights
        for k in sorted(best_weights.keys()):
            print(f"    {k}: {best_weights[k]}")


if __name__ == '__main__':
    import argparse
    main()
