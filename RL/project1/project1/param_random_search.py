"""
param_random_search.py

Run a random search over ReflexAgent-like evaluation parameters.
For each trial we create a Pacman agent whose evaluation function uses the
parameter block you provided (w1..w8, GAP). We run one game per trial and
record the final score. Results are saved to `param_search_results.csv`.

Usage (from project root):
  python param_random_search.py        # runs 200 random trials on testClassic
  python param_random_search.py --trials 50 --layout testClassic

Be aware: running 200 full Pacman games may take several minutes depending on
layout and machine speed.
"""

import argparse
import csv
import random
import time
import types

import pacman
import layout
import textDisplay
import ghostAgents
from multiAgents import ReflexAgent


def make_eval_fn(weights):
    """Return an evaluation function that mirrors your ReflexAgent's logic
    but uses the passed weights dict."""
    w1 = weights['w1']
    w2 = weights['w2']
    w3 = weights['w3']
    w4 = weights['w4']
    w5 = weights['w5']
    w6 = weights['w6']
    w7 = weights['w7']
    w8 = weights['w8']
    GAP = weights['GAP']
    E = 1e-05

    from util import manhattanDist

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
        # (optional alternative: sum of inverse distances)
        # foodDists_inv = [1.0/(x+E) for x in foodDists]
        f2_score = -1 * len(foodPos)
        f_score = w1 * f1_score + w2 * f2_score

        # Capsule
        capsulePos = successorGameState.getCapsules()
        if capsulePos:
            capDists = [manhattanDist(newPos, c) for c in capsulePos]
            c1_score = 1.0 / (min(capDists) + E)
        else:
            c1_score = 0.0
        c2_score = -1 * len(capsulePos)
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


def sample_weights(rng):
    """Sample a random parameter set from reasonable ranges."""
    return {
        'w1': rng.uniform(0.0, 5.0),    # food closeness weight
        'w2': rng.uniform(0.0, 0.5),    # food count penalty scale
        'w3': rng.uniform(0.0, 2.0),    # capsule closeness weight
        'w4': rng.uniform(0.0, 5.0),    # capsule count penalty scale
        'w5': rng.uniform(0.0, 5.0),    # scared ghost reward
        'w6': rng.uniform(0.0, 500.0),  # near-ghost huge penalty
        'w7': rng.uniform(0.0, 5.0),    # ghost distance penalty scale
        'w8': rng.uniform(0.0, 2.0),    # stop penalty scale
        'GAP': rng.randint(1, 4),       # threshold distance for immediate danger
    }


def run_trial(weights, layout_name='testClassic', numGhosts=4, timeout=30):
    # instantiate pacman agent and monkeypatch its evaluation function
    pac = ReflexAgent()
    eval_fn = make_eval_fn(weights)
    pac.evaluationFunction = types.MethodType(eval_fn, pac)

    # ghosts
    ghosts = [ghostAgents.RandomGhost(i + 1) for i in range(numGhosts)]

    # display: null graphics to suppress output
    display = textDisplay.NullGraphics()

    # run a single game
    L = layout.getLayout(layout_name)
    games = pacman.runGames(L, pac, ghosts, display, numGames=1, record=False, numTraining=0, catchExceptions=False, timeout=timeout)
    if len(games) > 0:
        score = games[0].state.getScore()
        win = games[0].state.isWin()
    else:
        # If runGames suppressed away games (shouldn't happen), fallback
        score = 0.0
        win = False
    return score, win


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trials', type=int, default=200)
    parser.add_argument('--layout', type=str, default='testClassic')
    parser.add_argument('--out', type=str, default='param_search_results.csv')
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--numGhosts', type=int, default=4)
    parser.add_argument('--timeout', type=int, default=30)
    args = parser.parse_args()

    rng = random.Random(args.seed)

    fieldnames = ['trial', 'score', 'win'] + ['w1','w2','w3','w4','w5','w6','w7','w8','GAP']
    with open(args.out, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        best = None
        start = time.time()
        for t in range(1, args.trials + 1):
            weights = sample_weights(rng)
            score, win = run_trial(weights, layout_name=args.layout, numGhosts=args.numGhosts, timeout=args.timeout)
            row = {'trial': t, 'score': score, 'win': win}
            row.update(weights)
            writer.writerow(row)
            print(f"Trial {t}/{args.trials}: score={score:.1f}, win={win}, params={weights}")

            if best is None or score > best[0]:
                best = (score, weights, win, t)

        elapsed = time.time() - start

    print('\nRandom search finished in %.1fs' % elapsed)
    if best:
        print('Best score: %.1f (trial %d) win=%s' % (best[0], best[3], best[2]))
        print('Best params:', best[1])
    print('Results written to', args.out)


if __name__ == '__main__':
    main()
