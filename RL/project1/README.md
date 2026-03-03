# 인공지능 — 적대적 탐색 기반 Pacman

> **CSE 17182 인공지능, 2025년 2학기 · Project #1**  
> 중앙대학교 · UC Berkeley CS188 Pacman AI 기반 (강의 맞춤 수정본)

---

## 프로젝트 기본 정보

| 항목 | 내용 |
|------|------|
| **프로젝트 제목** | 적대적 탐색 기반 Pacman — Minimax / Alpha-Beta / Expectimax |
| **한 줄 요약** | Pacman 환경에서 Reflex Agent, Minimax, Alpha-Beta 가지치기, Expectimax, 커스텀 평가 함수를 직접 구현하여 전 문항 만점 달성. |
| **프로젝트 유형** | ML / 게임 트리 탐색 (Adversarial Search) |
| **역할 / 핵심 기여** | Q1~Q5 전 문항 단독 구현. Reflex Agent용 멀티-컴포넌트 휴리스틱 평가 함수 설계(음식·캡슐·유령·행동 4개 하위 스코어), MiniMax·Alpha-Beta·Expectimax 게임 트리 탐색 알고리즘 구현, `betterEvaluationFunction` 설계 및 Grid Search / Random Search로 하이퍼파라미터 최적화 수행. |

---

## TL;DR

| | |
|-|-|
| **문제** | 유령이 인접 칸에서 Pacman을 잡을 수 있도록 강화된 변형 Pacman에서, 반사 에이전트부터 게임트리 기반 계획 에이전트까지 단계적으로 구현. |
| **접근 방법** | 반사 에이전트는 음식 거리 역수·캡슐 거리·공포 유령 추적·위험 유령 회피를 가중합산한 휴리스틱 사용. 계획 에이전트는 Minimax / Alpha-Beta / Expectimax 게임 트리로 깊이 우선 탐색. Q5의 `betterEvaluationFunction`은 상태 평가 함수로 확장하여 Grid Search로 가중치 최적화. |
| **주요 결과** | Q1: 10전 전승 + 평균 점수 > 500 달성; Q2~Q4: Autograder 완전 일치; Q5: `smallClassic` 10전 전승, 평균 점수 > 1000 달성. |
| **키워드** | `적대적 탐색` · `Minimax` · `Alpha-Beta Pruning` · `Expectimax` · `휴리스틱 평가 함수` · `Grid Search` · `Pacman AI` · `게임 트리` |

---

## 동기 및 배경

### 배경
적대적 탐색(Adversarial Search)은 상대방이 존재하는 환경에서 최적 행동을 결정하는 알고리즘이다. Minimax 알고리즘은 상대가 항상 최적으로 행동한다고 가정하며, Alpha-Beta 가지치기는 결과에 영향을 주지 않는 서브트리를 제거해 탐색 효율을 높인다. Expectimax는 상대가 확률적으로 행동하는 경우에 적합하다.

이 프로젝트의 Pacman은 원본 Berkeley 버전과 두 가지 점에서 다르다:
- **유령의 공격 범위 확장**: 인접 칸(거리 1)에만 있어도 Pacman이 잡힌다.
- **유령 이동 속도 절반**: 유령이 한 턴 건너 한 번 이동.

### 왜 중요한가
게임 트리 탐색은 체스(Deep Blue), 바둑(AlphaGo) 등 인공지능의 핵심 기반이다. 평가 함수의 품질이 에이전트 성능을 결정하며, 이를 제대로 설계하는 것이 실용 AI의 핵심 역량이다.

### 기존 방법의 한계
- 순수 Minimax는 깊이 증가 시 지수적으로 느려짐 ($O(b^d)$) → Alpha-Beta로 $O(b^{d/2})$로 개선 가능.
- 반사 에이전트는 한 수 앞만 본다 → 장기 계획 불가.
- `scoreEvaluationFunction`만으로는 Q5의 성능 요구사항(평균 ≥ 1000점) 달성 불가.

### 관련 연구
- Russell & Norvig, *Artificial Intelligence: A Modern Approach* (4th ed.) — Minimax·Alpha-Beta 이론 기반.
- Knuth & Moore (1975), "An analysis of alpha-beta pruning," *Artificial Intelligence* — Alpha-Beta 수렴 분석.
- UC Berkeley CS188 Pacman AI Projects (DeNero & Klein) — 이 프로젝트의 원본 코드베이스.

---

## 접근 방법 (Approach)

### Q1 — Reflex Agent 평가 함수

상태-행동 쌍 $(s, a)$에 대한 평가 함수를 4개의 하위 컴포넌트로 구성:

$$\text{score}(s, a) = \text{GameScore} + f_\text{food} + f_\text{capsule} + f_\text{ghost} + f_\text{action}$$

#### 음식 컴포넌트 ($f_\text{food}$)

$$f_\text{food} = w_1 \cdot \frac{1}{\min_i d(pos, food_i) + \varepsilon} + w_2 \cdot (-|\text{남은 음식}|)$$

- 가장 가까운 음식에 보너스 (역거리) · 남은 음식 수에 패널티
- $w_1 = 1$, $w_2 = 0.1$

#### 캡슐 컴포넌트 ($f_\text{capsule}$)

$$f_\text{capsule} = w_3 \cdot \frac{1}{\min_c d(pos, capsule_c) + \varepsilon} + w_4 \cdot (-|\text{남은 캡슐}|)$$

- $w_3 = 0.5$, $w_4 = 1.0$

#### 유령 컴포넌트 ($f_\text{ghost}$)

$$f_\text{ghost} = \begin{cases} w_5 \cdot \dfrac{1}{d + \varepsilon} & \text{scaredTimer} > 0 \text{ (공포 유령 추격)} \\ -w_6 & d \le \text{GAP} \text{ (위험 거리 내 강한 패널티)} \\ -w_7 \cdot \dfrac{1}{d + \varepsilon} & \text{otherwise (거리 반비례 패널티)} \end{cases}$$

- $w_5 = 2$, $w_6 = 200$, $w_7 = 2$
- **GAP = 2**: 유령과 거리 2 이하를 위험 구간으로 정의 (GAP=1 대비 성능 향상 확인)

#### 행동 컴포넌트 ($f_\text{action}$)

$$f_\text{action} = w_8 \cdot \mathbb{1}[\text{action} = \text{Stop}] \cdot (-1)$$

- $w_8 = 0$ (최종 비활성; 0~0.2 범위 실험 후 효과 미미 확인)

---

### Q2 — Minimax Agent

재귀적 상호 최소-최대 탐색:

$$V(s) = \begin{cases} \text{evalFn}(s) & \text{단말 상태 또는 깊이 도달} \\ \max_a V(\text{Succ}(s, a)) & \text{Pacman 턴 (index=0)} \\ \min_a V(\text{Succ}(s, a)) & \text{유령 턴 (index>0)} \end{cases}$$

**다중 유령 처리:**
- 에이전트 인덱스는 `(index+1) % numAgents`로 순환.
- 모든 유령이 한 번씩 이동한 후(`nextAgent == 0`) 깊이 1 증가.
- 단일 탐색 플라이 = Pacman 1회 이동 + 전체 유령 응답.

---

### Q3 — Alpha-Beta Agent

Minimax에 α-β 가지치기 추가:

$$\text{max\_node}: \text{return if } v \ge \beta \quad \text{(Beta-cut)}$$
$$\text{min\_node}: \text{return if } v \le \alpha \quad \text{(Alpha-cut)}$$

**구현 주의사항:**
- 자식 노드 처리 순서는 `getLegalActions` 반환 순서 그대로 유지 (Autograder 요구사항).
- 깊이 증가 로직은 Minimax와 동일.
- 결과: depth 3 Alpha-Beta ≈ depth 2 Minimax 속도.

---

### Q4 — Expectimax Agent

유령이 균등 랜덤 행동을 한다고 모델링:

$$V_\text{exp}(s) = \sum_a \frac{1}{|A(s)|} \cdot V(\text{Succ}(s, a))$$

- Pacman 노드: 동일하게 `max_value`.
- 유령 노드: `min_value` 대신 `exp_value` (균등 확률 기대값).
- 효과: `trappedClassic` 레이아웃에서 AlphaBeta는 항상 패배, Expectimax는 약 50% 승리.

---

### Q5 — betterEvaluationFunction

Q1의 상태-행동 평가 함수를 **상태 평가 함수**로 전환:

$$\text{score}(s) = \text{GameScore}(s) + f_\text{food} + f_\text{capsule} + f_\text{ghost}$$

구조는 Q1과 동일하나 action 컴포넌트 제거, `currentGameState` 직접 사용.

**최종 가중치:** `w1=1, w2=0.1, w3=0.5, w4=1, w5=2, w6=200, w7=2`, `GAP=1` (≤1 즉사 판정)

**하이퍼파라미터 최적화:**

Grid Search (`grid_search.py`)로 각 파라미터를 0~100 범위에서 0.1 간격으로 단독 탐색 후 `grid_search_results.csv`에 기록.  
Random Search (`param_random_search.py`)로 조합 탐색 후 `param_search_results.csv`에 기록.

---

## 데이터 및 실험

| 항목 | 내용 |
|------|------|
| **데이터셋 유형** | 합성 그리드 환경 (외부 데이터셋 없음) |
| **출처** | `layouts/` 폴더의 `.lay` 맵 파일; UC Berkeley CS188 Pacman 프레임워크 |
| **환경 변형** | 유령 공격 범위 1칸(인접 즉사), 유령 이동 속도 0.5배 (CSE 17182 변형) |
| **레이아웃** | openClassic (Q1), smallClassic (Q2~Q5), testClassic, trappedClassic 등 11종 |
| **평가 방식** | Q1/Q5: Autograder 10회 실행, 승률·평균점수 기준값 비교 · Q2~Q4: 탐색 트리 상태 수 참조 구현과 완전 일치 검증 |
| **평가 지표** | 승률 (Win Rate), 평균 게임 점수, 탐색 상태 수 (Q2~Q4) |
| **실행 환경** | macOS (Apple M2) · Python 3.9 (conda) |
| **프레임워크/라이브러리** | Python 표준 라이브러리 · `util.manhattanDist` (BFS 없이 맨해튼 거리) |
| **재현성** | 각 에이전트는 `--fixRandomSeed` 없어도 Q2~Q4는 결정론적; Q1/Q5는 랜덤 결과 포함 |

---

## 결과

### Autograder 배점 및 획득 점수

| 문항 | 주제 | 만점 | 획득 | 채점 기준 |
|------|------|-----:|-----:|----------|
| Q1 | Reflex Agent | 4 | **4** | 10전 전승=2pt · 평균점수>500=1pt · >1000=2pt |
| Q2 | Minimax Agent | 4 | **4** | 탐색 상태 수 완전 일치 |
| Q3 | Alpha-Beta Agent | 3 | **3** | 탐색 상태 수 완전 일치 (노드 순서 고정) |
| Q4 | Expectimax Agent | 3 | **3** | 탐색 상태 수 완전 일치 |
| Q5 | betterEvaluationFunction | 6 | **6** | 5전+ 승리=1pt · 10전 전승=2pt · 평균>500=1pt · >1000=2pt · 30초 이내=1pt |
| **합계** | | **20** | **20** | |

### Q1 Reflex Agent — openClassic 성능

| 지표 | 값 | 기준값 |
|------|:--:|:------:|
| 승률 (10게임) | **10 / 10** | ≥ 5 |
| 평균 게임 점수 | **> 500** | > 500 |

### Q5 betterEvaluationFunction — smallClassic 성능

| 지표 | 값 | 기준값 |
|------|:--:|:------:|
| 승률 (10게임) | **10 / 10** | ≥ 5 |
| 평균 게임 점수 | **> 1000** | > 1000 |
| 게임당 소요 시간 | **< 30초** | < 30초 |

### Q4 Expectimax vs AlphaBeta — trappedClassic 비교

| 에이전트 | 레이아웃 | 결과 |
|----------|----------|------|
| `AlphaBetaAgent` depth=3 | trappedClassic | **항상 패배** |
| `ExpectimaxAgent` depth=3 | trappedClassic | **약 50% 승리** |

### 파라미터 탐색 결과 요약

Grid Search (각 파라미터 단독 탐색, step=0.1) 결과:
- `w6` (위험 유령 패널티): 200 이상에서 안정적으로 높은 점수
- `GAP`: 2로 설정 시 1 대비 성능 향상 확인 (Reflex Agent)
- `w8` (Stop 패널티): 0~0.2 범위 실험, 유의미한 효과 없어 0으로 설정

---

## 고찰

### 핵심 관찰 사항

1. **GAP = 2 설정이 결정적.**  
   유령 위험 구간을 거리 1로 설정하면 Q1 채점에서 지속적으로 실패. 거리 2 이하를 위험으로 정의하자 급격히 성능 향상. 변형된 공격 범위(인접 즉사) 규칙 때문에 실질적 위험 구간이 더 넓은 것이 원인.

2. **`w6 = 200`의 클리핑 효과.**  
   위험 유령에 `-200` 패널티를 주면 거리와 무관하게 동일한 강한 회피 신호 제공. 오히려 거리 역수의 부드러운 패널티보다 분류형 위험 판단이 더 효과적.

3. **Expectimax와 Minimax의 본질적 차이:**  
   Minimax는 유령을 최악의 경우로 가정 → 탈출 가능성이 있어도 확실히 패배하면 포기. Expectimax는 유령의 랜덤성을 모델링 → 낮은 확률의 탈출도 시도. `trappedClassic`에서 이 차이가 극명히 드러남.

4. **상태 평가 vs 행동 평가.**  
   Q1(행동 평가)에서 Q5(상태 평가)로 넘어갈 때, Stop 패널티 항(`w8`)이 더 이상 의미 없어짐. 상태 자체를 평가하면 자연히 정체 상태의 낮은 가치가 반영됨.

5. **Grid Search의 유용성과 한계.**  
   단독 파라미터 탐색으로 민감도 파악 가능하지만, 파라미터 간 상호작용은 놓침. Random Search로 조합 탐색을 보완했으나, 최종 가중치는 코드 주석에 기록된 직관적 이해를 기반으로 수렴.

### 해석
반사 에이전트의 성능은 평가 함수 설계에 전적으로 의존한다. 게임 트리 에이전트는 탐색 깊이가 깊을수록 강해지지만 계산 비용이 급증하며, 평가 함수의 품질이 한계 성능을 결정한다. Alpha-Beta는 동일한 결과를 훨씬 빠르게 달성하며, Expectimax는 랜덤 상대에 대한 더 현실적인 모델을 제공한다.

### 트레이드오프

| 항목 | Reflex | Minimax | Alpha-Beta | Expectimax |
|------|:------:|:-------:|:----------:|:----------:|
| 탐색 깊이 | 1 | $d$ | $d$ | $d$ |
| 시간 복잡도 | $O(b)$ | $O(b^d)$ | $O(b^{d/2})$ | $O(b^d)$ |
| 유령 모델 | 없음 | 최악 | 최악 | 균등 랜덤 |
| 함정 처리 | 취약 | 보수적 | 보수적 | 용감 |

### 배운 점

1. **평가 함수가 에이전트 성능의 병목:** 알고리즘이 완벽해도 평가 함수가 나쁘면 성능이 낮음. 역거리, 컴포넌트 분리, GAP 설정 같은 도메인 지식이 결정적.
2. **게임 규칙 변화의 파급 효과:** 유령 공격 범위 1칸 확장이라는 작은 규칙 변경이 파라미터 최적값(GAP)을 완전히 바꿔놓음.
3. **체계적 실험의 중요성:** Grid Search/Random Search 없이 직관만으로 파라미터를 튜닝하면 국소 최적에 갇히기 쉬움.

---

## 한계 및 향후 연구

### 한계

1. **맨해튼 거리의 부정확성:** 벽을 무시한 맨해튼 거리는 실제 경로보다 짧아 유령/음식 거리 추정에 오차 발생. BFS 실거리를 쓰면 더 정확하나 계산 비용 증가.
2. **고정 가중치의 취약성:** 모든 가중치가 상수로 고정되어 있어, 게임 진행 상황(음식 개수, 유령 상태)에 따른 동적 조정 불가.
3. **Expectimax의 계산 비용:** Alpha-Beta보다 느리며, 실제 유령은 완전 랜덤이 아닌 반향적 행동을 하기 때문에 모델이 부정확할 수 있음.
4. **단일 레이아웃 최적화:** `openClassic`(Q1), `smallClassic`(Q5)에 맞춰 튜닝된 파라미터가 다른 레이아웃에서는 최적이 아닐 수 있음.

### 향후 방향

1. **BFS 기반 실거리 사용:** `util.py`의 자료구조를 활용해 맨해튼 거리 대신 실제 미로 경로 거리로 평가 함수 개선.
2. **Monte Carlo Tree Search (MCTS):** 랜덤 롤아웃으로 평가 함수 없이 탐색 가능; 깊은 게임에서 Alpha-Beta보다 유연.
3. **신경망 평가 함수:** 게임 상태를 벡터로 인코딩하여 학습 기반 평가 함수 설계 (DQN 방향).
4. **동적 탐색 깊이:** 남은 음식 수나 유령 근접도에 따라 탐색 깊이를 동적으로 조정하는 Iterative Deepening 적용.

### 시간이 더 있었다면
- GAP을 정수가 아닌 연속 파라미터로 취급하여 더 세밀한 위험 구간 설계.
- 모든 레이아웃에서 교차 검증하여 일반화 성능 측정.
- Alpha-Beta의 Move Ordering (우수한 수를 먼저 탐색)으로 추가 속도 향상.

---

## 프로젝트 구조

```
project1/
├── multiAgents.py               # ★ 전체 구현체 (학생 제출 파일)
│   ├── ReflexAgent              # Q1: 반사 에이전트
│   ├── MinimaxAgent             # Q2: 미니맥스 에이전트
│   ├── AlphaBetaAgent           # Q3: 알파-베타 가지치기 에이전트
│   ├── ExpectimaxAgent          # Q4: 기댓값 최대화 에이전트
│   └── betterEvaluationFunction # Q5: 향상된 평가 함수
│
├── multiAgents_best.py          # 실험 중 최고 점수 기록 버전 보관
├── multiAgents_origin.py        # 원본 Berkeley 스켈레톤 코드 보관
│
├── grid_search.py               # 단독 파라미터 Grid Search 스크립트
├── grid_search_results.csv      # Grid Search 결과 (param, value, score, win, ...)
├── param_random_search.py       # 파라미터 조합 Random Search 스크립트
├── param_search_results.csv     # Random Search 결과
│
├── pacman.py                    # Pacman 메인 실행 파일 + GameState 정의
├── autograder.py                # 자동 채점 실행기
├── game.py                      # 게임 로직: AgentState, Directions, Grid
├── ghostAgents.py               # 유령 동작 정의
├── util.py                      # 유틸리티: manhattanDist, Counter 등
│
├── layouts/                     # 11개 맵 파일 (.lay)
│   ├── openClassic.lay          # Q1 테스트 레이아웃
│   ├── smallClassic.lay         # Q2~Q5 메인 테스트 레이아웃
│   ├── trappedClassic.lay       # Q4 Expectimax vs Minimax 비교
│   └── ...
│
├── test_cases/                  # Autograder 테스트 케이스
│   ├── CONFIG                   # 문항 순서
│   ├── q1/  grade-agent.test    # Q1 채점 (openClassic, 10게임)
│   ├── q2/  (Minimax 상태 수 검증)
│   ├── q3/  (Alpha-Beta 상태 수 검증)
│   ├── q4/  (Expectimax 상태 수 검증)
│   ├── q5/  (smallClassic, 10게임)
│   └── extra/                   # 추가 테스트 (grade-agent.test)
│
└── Project 1 Instruction.pdf    # 공식 과제 명세서 (8페이지)
```

---

## 실행 방법

```bash
# 환경 설정
conda create -n pacman python=3.9 -y
conda activate pacman

# 키보드로 직접 플레이
python pacman.py

# Q1: Reflex Agent 실행
python pacman.py -p ReflexAgent -l openClassic

# Q2: Minimax Agent 실행 (depth=2)
python pacman.py -p MinimaxAgent -l smallClassic -a depth=2

# Q3: Alpha-Beta Agent 실행 (depth=3, Minimax depth=2와 속도 비교)
python pacman.py -p AlphaBetaAgent -l smallClassic -a depth=3

# Q4: Expectimax vs AlphaBeta 비교 (trappedClassic)
python pacman.py -p AlphaBetaAgent -l trappedClassic -a depth=3
python pacman.py -p ExpectimaxAgent -l trappedClassic -a depth=3

# Q5: betterEvaluationFunction 실행
python pacman.py -p ExpectimaxAgent -l smallClassic -a evalFn=better,depth=2

# Autograder (전체 문항)
python autograder.py

# Autograder (단일 문항, 그래픽 없이)
python autograder.py -q q1
python autograder.py -q q5 --no-graphics

# 파라미터 탐색 (단독)
python grid_search.py --param w1
python grid_search.py --param all

# 파라미터 조합 탐색
python param_random_search.py
```

---

## PDF / 강의자료 매핑

| 출처 | 내용 |
|------|------|
| `Project 1 Instruction.pdf` — p. 1 | 프로젝트 개요, 제출 규칙(`multiAgents.py` 단독 제출), 마감일(10월 26일 23:59), 환경(Python 3.9 conda) |
| p. 2 | Pacman 세계 규칙 변경 (유령 공격 범위·속도), 주요 파일 목록 |
| p. 3 | Q1: Reflex Agent 채점 기준 (10전 전승=2pt, 평균>500=1pt, >1000=2pt) |
| p. 4 | Q2: Minimax, 다중 유령 처리, 단일 플라이 정의, 채점 기준 |
| p. 5 | Q3: Alpha-Beta, 노드 순서 고정 요구사항, 채점 기준 |
| p. 6 | Q4: Expectimax, 균등 랜덤 유령 가정, `trappedClassic` 비교 |
| p. 7 | Q5: `betterEvaluationFunction` 채점 기준 (전승=2pt, 평균>1000=2pt, 30초=1pt) |
| p. 8 | 학문적 정직성 정책 (표절 → 자동 F 학점) |

---

## 인용 및 라이선스

```
@misc{berkeley_cs188_p1,
  title        = {Project 1: Multiagent Search},
  author       = {DeNero, John and Klein, Dan and Miller, Brad and Hay, Nick and Abbeel, Pieter},
  institution  = {UC Berkeley CS188 Artificial Intelligence},
  url          = {https://ai.berkeley.edu/},
  note         = {Adapted for CSE 17182, Chung-Ang University, Fall 2025}
}
```

**라이선스:** 교육 목적 전용. 원본 Berkeley 저작권 고지 기준:
> *"교육 목적으로 이 프로젝트를 자유롭게 사용하거나 확장할 수 있으나, (1) 솔루션을 배포하거나 출판하지 말 것, (2) 이 고지를 유지할 것, (3) UC Berkeley에 명확한 저작권을 표시할 것."*

**참고 문헌:**
- Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson.
- Knuth, D. E., & Moore, R. W. (1975). An analysis of alpha-beta pruning. *Artificial Intelligence*, 6(4), 293–326.
- UC Berkeley CS188 Pacman AI Projects: https://ai.berkeley.edu/
