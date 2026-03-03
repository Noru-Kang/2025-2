# 강화학습 — Value Iteration & Q-Learning

> **CSE 17182 인공지능, 2025년 2학기 · Project #2**  
> 중앙대학교 · UC Berkeley CS188 Pacman AI 기반 (강의 맞춤 수정본)

---

## 프로젝트 기본 정보

| 항목 | 내용 |
|------|------|
| **프로젝트 제목** | 강화학습 — Value Iteration & Q-Learning |
| **한 줄 요약** | Gridworld·Pacman 환경에서 모델 기반 Value Iteration과 모델 프리 Q-Learning / Approximate Q-Learning 에이전트를 직접 구현하여 Autograder **만점(21/21) 및 수업 최종 1등** 달성. |
| **프로젝트 유형** | ML / 강화학습 |
| **역할 / 핵심 기여** | Q1~Q6 전 문항 단독 구현 완료. Value Iteration의 Bellman 방정식 동기식 배치 업데이트 설계, 동점 랜덤 처리를 포함한 표 형식 Q-Learning 구현, ε-greedy 탐색 및 선형 Approximate Q-Learning 가중치 업데이트를 처음부터 직접 작성. Q2에서 5가지 서로 다른 최적 정책을 만들어내는 MDP 파라미터 조합을 직접 설계. **Autograder 최종 평가 수업 1등.** |

---

## TL;DR

| | |
|-|-|
| **문제** | Value Iteration, 표 형식 Q-Learning, Approximate Q-Learning 세 가지 RL 알고리즘을 구현하고, Gridworld → Crawler 로봇 → Pacman으로 점진적으로 난이도를 높이며 검증. |
| **접근 방법** | Value Iteration은 Bellman 최적 방정식의 동기식 배치 업데이트 적용. Q-Learning은 TD(0) 업데이트 + ε-greedy 탐색 + 동점 랜덤 처리. Approximate Q-Learning은 Q-테이블 대신 수작업 설계한 상태-행동 특징(bias, 유령 근접도, 음식 거리)에 대한 선형 함수로 대체. |
| **주요 결과** | 6개 문항 전부 **21 / 21점 만점**; Pacman Q-에이전트 `smallGrid` 테스트 승률 ≥ 70%; Approximate 에이전트는 훈련 50 에피소드만으로 `mediumGrid` 거의 전승. **수업 순위: 1등.** |
| **키워드** | `강화학습` · `MDP` · `Value Iteration` · `Bellman Equation` · `Q-Learning` · `Epsilon-Greedy` · `Approximate Q-Learning` · `Feature Extraction` |

---

## 동기 및 배경

### 배경
강화학습(RL)은 순차적 의사결정 문제를 마르코프 결정 과정(MDP) $\langle S, A, T, R, \gamma \rangle$으로 모형화한다. 에이전트는 기대 할인 누적 보상을 최대화하는 정책 $\pi^*: S \to A$를 학습해야 한다. 이 프로젝트는 두 가지 핵심 패러다임을 구현한다.

- **모델 기반 RL** (Value Iteration): 전이 모델 $T$와 보상 함수 $R$에 완전 접근을 가정하며, $V^*$에 수렴할 때까지 가치 추정 $V_k$를 반복 갱신.
- **모델 프리 RL** (Q-Learning): 모델 없이 환경 상호작용으로부터 직접 학습; TD 업데이트로 $Q^*(s,a)$를 온라인 추정.

### 왜 중요한가
MDP 풀기와 Q-Learning은 현대 심층 RL(DQN, AlphaGo 등)의 알고리즘적 토대다. 할인 계수·노이즈·생존 보상이 최적 정책에 미치는 영향을 이해하는 것은 실제 응용에서의 보상 설계에 필수적이다.

### 기존 방법의 한계
표 형식 Q-Learning은 *차원의 저주*를 겪는다. Q-테이블 크기가 $O(|S| \cdot |A|)$로 증가해 상태 공간이 크거나 연속적인 경우 사용이 불가능하다. Feature extractor를 이용한 Approximate Q-Learning은 공유 가중치 벡터로 상태 간 일반화를 가능하게 하여 정확성과 확장성을 맞바꾼다.

### 관련 연구
- Sutton & Barto, *Reinforcement Learning: An Introduction* (2nd ed., 2018) — RL 이론 및 Q-Learning 유도의 기초.
- Watkins & Dayan (1992), "Q-learning," *Machine Learning* — 표 형식 Q-Learning 수렴 증명.
- Mnih et al. (2015), "Human-level control through deep RL," *Nature* — 표 형식 Q-Learning을 심층 신경망 Q-네트워크(DQN)로 확장.
- UC Berkeley CS188 Pacman AI Projects (DeNero & Klein) — 이 프로젝트의 원본 코드베이스.

---

## 접근 방법 (Approach)

### Value Iteration (Q1) — 모델 기반

**Bellman 최적 업데이트 (동기식·배치):**

$$V_{k+1}(s) = \max_{a} \sum_{s'} T(s, a, s') \left[ R(s, a, s') + \gamma \, V_k(s') \right]$$

**값 함수로부터 Q-값 계산:**

$$Q(s, a) = \sum_{s'} T(s, a, s') \left[ R(s, a, s') + \gamma \, V(s') \right]$$

**구현 선택 사항:**
- 매 반복마다 임시 `util.Counter` (`temp_values`)를 생성하고, 모든 상태 처리 후에만 `self.values`를 교체(동기식/배치 업데이트). 이를 통해 $V_{k+1}$이 반드시 $V_k$에서만 계산되도록 보장.
- 단말 상태는 합법적 행동이 없음 → `computeActionFromValues`는 `None` 반환; `computeValueFromQValues`는 `0.0` 반환.
- `computeActionFromValues`의 동점 처리: `Counter.argMax()` 사용(결정론적).

**기본 하이퍼파라미터:** `discount γ = 0.9`, `iterations = 100`

---

### 정책 파라미터 분석 (Q2) — MDP 보상 설계

`DiscountGrid` MDP에서 `(discount γ, noise, livingReward)` 조정을 통해 다섯 가지 질적으로 다른 최적 정책을 유도:

| 소문항 | 정책 목표 | γ | noise | livingReward |
|--------|----------|---|-------|-------------|
| 2a | 가까운 출구(+1) 선호, **절벽 감수** (-10) | 0.1 | 0.0 | -1.0 |
| 2b | 가까운 출구(+1) 선호, **절벽 회피** (-10) | 0.1 | 0.1 | -1.0 |
| 2c | 먼 출구(+10) 선호, **절벽 감수** (-10) | 1.0 | 0.0 | -0.1 |
| 2d | 먼 출구(+10) 선호, **절벽 회피** (-10) | 1.0 | 0.1 | -0.1 |
| 2e | **종료하지 않음** (출구·절벽 모두 회피) | 0.0 | 0.0 | +11.0 |

**설계 근거:**
- 낮은 γ (0.1)는 에이전트를 근시안적으로 만들어 가까운 +1 출구를 선호.
- 높은 γ (1.0)는 에이전트를 인내심 있게 만들어 더 먼 경로를 통한 +10 획득 허용.
- `noise = 0`은 확률성을 제거 → 절벽 감수가 합리적(우연한 추락 없음).
- `noise > 0`은 임의성 추가 → 에이전트가 안전한 상단 절벽 회피 경로 선호.
- `livingReward = +11.0`에 `γ = 0` → 에이전트가 어떤 일회성 출구 보상보다 생존(+11/스텝)을 선호.

---

### Q-Learning (Q3 + Q4) — 모델 프리, 표 형식

**Q-테이블 저장:** `util.Counter` (기본값 `0.0`), `(state, action)` 쌍을 키로 사용.

**시간차 업데이트 (Q3):**

$$Q(s, a) \leftarrow (1 - \alpha)\,Q(s, a) + \alpha \left[ r + \gamma \max_{a'} Q(s', a') \right]$$

**Epsilon-Greedy 행동 선택 (Q4):**

$$\pi(s) = \begin{cases} \text{임의 행동} & \varepsilon \text{ 확률로} \\ \arg\max_{a} Q(s, a) & 1 - \varepsilon \text{ 확률로} \end{cases}$$

**구현 선택 사항:**
- `computeValueFromQValues`: 합법 행동에 대한 `max Q(s,a)` 반환; 단말 상태(합법 행동 없음)에서는 `0.0` 반환.
- `computeActionFromQValues`: 합법 행동 순회, 최고 값 추적, 동점 시 `random.choice`로 무작위 선택 — 대칭 환경에서의 탐색과 정확성에 필수.
- `computeValueFromQValues`를 포함한 모든 Q-값 읽기는 `getQValue()`를 통해 수행 → `ApproximateQAgent`의 다형성 오버라이드 지원.

**기본 하이퍼파라미터 (PacmanQAgent):** `ε = 0.05`, `α = 0.2`, `γ = 0.8`

---

### Pacman Q-Learning (Q5)

`PacmanQAgent`는 Pacman에 맞춘 기본값을 가진 `QLearningAgent`의 별칭.  
훈련: 2000 에피소드(무음) → 테스트: 100 에피소드(GUI 표시).  
테스트 시 `ε = 0`, `α = 0`으로 설정 (추가 학습 없음; 순수 활용).

**채점 기준:** `smallGrid` 테스트 100게임에서 ≥ 70승.

---

### Approximate Q-Learning (Q6) — 선형 함수 근사

**Q-함수 (특징에 대한 선형식):**

$$Q(s, a) = \mathbf{w} \cdot \mathbf{f}(s, a) = \sum_i w_i \, f_i(s, a)$$

**가중치 업데이트 (TD 오차에 대한 경사 하강):**

$$w_i \leftarrow w_i + \alpha \underbrace{\left[ r + \gamma \max_{a'} Q(s', a') - Q(s, a) \right]}_{\text{TD 오차 (difference)}} f_i(s, a)$$

**`SimpleExtractor` 특징 (Pacman용):**

| 특징 | 설명 |
|------|------|
| `bias` | 상수 1.0 — 기준값(baseline) 학습 |
| `#-of-ghosts-1-step-away` | 다음 위치에서 1스텝 내 도달 가능한 유령 수 |
| `eats-food` | 다음 위치에 음식이 있고 유령 위험이 없으면 1.0 |
| `closest-food` | 가장 가까운 음식까지의 BFS 거리 / (너비 × 높이) — (0,1]로 정규화 |

모든 특징은 수치 안정성을 위해 10.0으로 나눔.  
훈련 종료 시 학습된 가중치를 `final()`에서 콘솔 출력.

**핵심 장점:** `SimpleExtractor` 사용 시 단 **50 에피소드** 훈련만으로 `mediumGrid`에서 거의 전승. 표 형식 Q-Learning이 수천 에피소드를 필요로 하는 것과 대조됨.

---

## 데이터 및 실험

| 항목 | 내용 |
|------|------|
| **데이터셋 유형** | 합성 그리드 환경 (외부 데이터셋 없음) |
| **출처** | `layouts/` 폴더의 `.lay` 맵 파일(절차적 정의); UC Berkeley CS188 Pacman 프레임워크 |
| **환경** | Gridworld (tinygrid, bridge, discountgrid) · smallGrid · mediumGrid · Crawler 로봇 |
| **레이블 / 타깃** | 환경으로부터의 보상 신호 (스텝당 게임 점수 변화량) |
| **전처리** | 없음 (상태는 직접적인 게임 구성; `SimpleExtractor`에서 특징 정규화) |
| **데이터 누수 점검** | N/A (온라인 RL; 훈련·테스트 에피소드는 완전히 순차적) |
| **분할** | Q5: 훈련 2000게임 / 테스트 100게임 · Q6: 훈련 50 / 테스트 10 |
| **평가 방식** | Autograder가 Q-값/가중치를 참조 구현과 비교(결정론적 시드); Q5는 승률 기준값 확인 |
| **평가 지표** | Q1/Q3/Q6: Q-값·정책 일치(완전 일치) · Q2: 정책 유형 일치 · Q4: 행동 검증 · Q5: 승률 ≥ 70% |
| **실행 환경** | macOS · Python 3.9 (conda) |
| **프레임워크/라이브러리** | Python 표준 라이브러리 · `numpy` · `util.Counter` (커스텀) · `random` · `math` |
| **재현성** | Q5 Autograder는 `--fixRandomSeed` 사용; Q1~Q4/Q6는 동일 시드에서 완전 결정론적 |

---

## 결과

### Autograder 점수 요약

| 문항 | 주제 | 만점 | 획득 | 테스트 클래스 |
|------|------|-----:|-----:|--------------|
| Q1 | Value Iteration | 5 | **5** | `PassAllTestsQuestion` |
| Q2 | 정책 분석 | 5 | **5** | `NumberPassedQuestion` |
| Q3 | Q-Learning | 5 | **5** | `PassAllTestsQuestion` |
| Q4 | Epsilon-Greedy | 2 | **2** | `PassAllTestsQuestion` |
| Q5 | Q-Learning & Pacman | 1 | **1** | `PartialCreditQuestion` |
| Q6 | Approximate Q-Learning | 3 | **3** | `PassAllTestsQuestion` |
| **합계** | | **21** | **21** | |

### Q5 Pacman 승률 벤치마크

| 설정 | 훈련 에피소드 | 승률 (테스트 100게임) | 기준값 |
|------|:------------:|:-------------------:|:------:|
| `smallGrid`의 `PacmanQAgent` | 2000 | ≥ 70% | 70 / 100 |

### Q6 Approximate Q-Learning

| 설정 | 훈련 에피소드 | 결과 |
|------|:------------:|------|
| `smallGrid` + `ApproximateQAgent` + `IdentityExtractor` | 2000 | `PacmanQAgent`와 동일한 동작 |
| `mediumGrid` + `ApproximateQAgent` + `SimpleExtractor` | 50 | 거의 전승 |

### 통계적 유의성 / 신뢰도
Q1~Q4, Q6: 결과가 완전히 결정론적 (참조 Q-값과 정확히 일치).  
Q5: 승률은 확률적; Autograder가 재현성을 위해 고정 랜덤 시드 사용.

### 시각화 메모
- Value Iteration (Q1): $V_k$ 값의 그리드 히트맵 + 방향 정책 화살표, GUI에서 반복당 애니메이션 (`python gridworld.py -a value -i 5`).
- Q-Learning (Q3): 수동 플레이 중 Q-값 그리드 실시간 업데이트 (`python gridworld.py -a q -k 4 --noise 0.0 -m`).
- ε-Greedy (Q4): `ε → 0`에 따라 정책 화살표 안정성 증가; `-e 0.1` vs `-e 0.9` GUI 비교로 확인 가능.
- Approximate Q-Learning (Q6): 에피소드 종료 시 학습된 최종 가중치 콘솔 출력.

---

## 고찰

### 핵심 관찰 사항

1. **Value Iteration에서 동기식 업데이트가 정확성의 핵심.** `temp_values`(전체 가치 테이블 복사 후 업데이트)를 사용해야 $V_{k+1}$이 반드시 $V_k$에서만 계산됨. 그렇지 않으면 같은 반복 내에서 앞선 상태의 업데이트가 뒤의 상태 계산을 오염시킴.

2. **Q2에서 MDP 파라미터 상호작용은 단순하지 않다.** 할인율과 생존 보상이 함께 시간 선호도 vs. 위험 허용 범위를 결정함. `noise = 0.0`을 설정하는 것이 절벽 감수 정책에 필요조건이지만 충분조건은 아님; 즉각적인 +1 보상이 할인된 +10을 초과하도록 할인율도 충분히 낮아야 함.

3. **`computeActionFromQValues`의 동점 처리가 측정 가능한 차이를 만든다.** 대칭적인 그리드 상태에서 결정론적 동점 처리(항상 첫 번째 행동)는 탐색을 편향시킴; 동점 중 `random.choice`를 사용하면 더 균형 잡힌 Q-값 추정 생성.

4. **Approximate Q-Learning은 샘플 복잡도를 극적으로 감소시킨다.** `SimpleExtractor`의 4개 특징만으로 Pacman 상태 전반에 걸쳐 일반화; 50번의 훈련 게임으로 충분함 (표 형식 에이전트의 수천 에피소드 대비). 이는 함수 근사 RL에서 특징 엔지니어링의 힘과 설계 민감성을 보여줌.

5. **특징 정규화(`divideAll(10.0)`)가 가중치 업데이트를 안정화한다.** 정규화 없이는 원시 특징 크기(예: closest-food 거리)가 발산하는 가중치 업데이트를 유발함; 정규화된 특징은 경사 스텝을 제한된 범위 내로 유지.

### 해석
Value Iteration은 이론적으로 정확하지만 알려진 MDP 모델이 필요 — 대부분의 실제 문제에서는 비실용적. 표 형식 Q-Learning은 메모리($O(|S||A|)$) 비용과 대규모 공간에서의 느린 수렴을 댓가로 모델 요구사항을 제거. Approximate Q-Learning은 특징 기반 일반화로 확장성 문제를 해결하지만, 비선형 근사기에서는 수렴이 보장되지 않음.

### 트레이드오프

| 항목 | Value Iteration | 표형식 Q-Learning | Approximate Q-Learning |
|------|:--------------:|:-----------------:|:---------------------:|
| 모델 필요 | ✅ | ❌ | ❌ |
| 메모리 | $O(\|S\|)$ | $O(\|S\|\cdot\|A\|)$ | $O(\|\mathbf{w}\|)$ |
| 샘플 효율 | N/A (플래닝) | 낮음 | 높음 |
| 수렴 보장 | ✅ | ✅ (표 형식) | ⚠️ (선형만) |
| 대규모 $\|S\|$ 확장 | ❌ | ❌ | ✅ |

### 배운 점

1. **Bellman 방정식 메커니즘:** 동기식 vs. 비동기식 업데이트의 올바른 구현과, 정책 오프셋으로 인해 $k$-스텝 값이 $k+1$개의 보상을 반영하는 방식은 이론을 정확히 읽어야 이해 가능.
2. **하이퍼파라미터 민감도:** 할인율, 노이즈, 엡실론, 알파가 미묘하게 상호작용; Q2의 5가지 정책 목표를 통해 보상 설계와 정책 설계에 대한 강한 직관 형성.
3. **특징 엔지니어링이 함수 근사 RL의 병목:** `SimpleExtractor`의 신중하게 선택된 4개 특징이 수천 에피소드의 표 형식 Q-러닝을 능가함 — 특징에 내재된 도메인 지식이 알고리즘적 정교함보다 더 큰 영향력을 가질 수 있음을 확인.

---

## 한계 및 향후 연구

### 한계

1. **표 형식 Q-Learning의 확장성 문제**: $O(|S||A|)$ 메모리와 느린 수렴이 소형 그리드를 넘어서면 불가능하게 만듦.
2. **수작업 설계된 Feature extractor**: `SimpleExtractor`는 도메인 지식을 수동으로 인코딩; 재설계 없이는 새로운 Pacman 레이아웃으로 일반화 불가.
3. **ε-greedy는 약한 탐색 전략**: 모든 미지 상태를 균등하게 처리; 카운트 기반 또는 호기심 기반 탐색이 더 원칙적.
4. **함수 근사 수렴 보장 없음**: 선형 Approximate Q-Learning은 오프-정책 환경에서 발산 가능; 여기서의 결과는 비교적 양성적인 Pacman 환경의 혜택.
5. **분포 내(in-distribution) 평가**: 에이전트가 훈련한 것과 동일한 레이아웃에서 테스트; 미지 맵으로의 일반화는 평가하지 않음.

### 향후 방향

1. **Deep Q-Network (DQN)**: 선형 특징 근사기를 CNN/MLP로 교체; 안정적 훈련을 위한 경험 재플레이와 타깃 네트워크 적용; 원본 풀사이즈 Pacman 테스트.
2. **Policy Gradient (REINFORCE / PPO)**: Q-함수 대신 정책 $\pi_\theta$를 직접 최적화; 확률적 정책과 연속 행동 공간에 자연스럽게 적합.
3. **카운트 기반 / 내재적 탐색**: ε-greedy를 UCB 또는 호기심 기반 보너스로 교체하여 희소 보상 환경에서 더 효율적인 탐색.
4. **다중 레이아웃 일반화**: 여러 Pacman 레이아웃에서 에이전트를 훈련하고 제로샷 전이 평가.
5. **보상 설계(Reward shaping) 분석**: Q2의 (γ, noise, R) 파라미터 공간을 체계적으로 탐색하여 최적 정책 유형의 완전한 위상 도표(phase diagram) 생성.

### 시간이 더 있었다면
- 비동기식 Value Iteration을 구현하고 동기식과 수렴 속도 비교.
- `SimpleExtractor`의 각 특징을 개별 ablation 실험으로 기여도 정량화.
- 그리드 크기별로 표 형식 vs. Approximate Q-Learning의 샘플 효율성(에피소드-to-임계값) 프로파일링 및 비교.

---

## 프로젝트 구조

```
project2/
├── valueIterationAgents.py      # ★ Q1: Value Iteration 에이전트 (학생 구현)
├── qlearningAgents.py           # ★ Q3–Q6: QLearningAgent, PacmanQAgent, ApproximateQAgent (학생 구현)
├── analysis.py                  # ★ Q2: MDP 파라미터 분석 (학생 구현)
│
├── gridworld.py                 # Gridworld 환경 + CLI 진입점 (Q1–Q4)
├── pacman.py                    # Pacman 게임 + CLI 진입점 (Q5–Q6)
├── autograder.py                # 자동 채점 실행기 (python autograder.py -q q1)
├── crawler.py                   # Crawler 로봇 데모 (Q3 부가 데모)
│
├── learningAgents.py            # 기본 클래스: ValueEstimationAgent, ReinforcementAgent
├── mdp.py                       # 추상 MDP 인터페이스
├── featureExtractors.py         # IdentityExtractor, CoordinateExtractor, SimpleExtractor (Q6)
├── util.py                      # Counter, PriorityQueue, flipCoin 등 유틸리티
├── game.py                      # 게임 인프라: Actions, Directions, Agent
├── ghostAgents.py               # 유령 동작 (RandomGhost, DirectionalGhost)
├── environment.py               # 추상 Environment 기본 클래스
├── backend.py                   # ReplayMemory (확장 백엔드)
│
├── layouts/                     # 14개 맵 파일 (.lay)
│   ├── smallGrid.lay            # Q5 훈련/테스트 맵
│   ├── mediumGrid.lay           # Q6 테스트 맵 (SimpleExtractor)
│   ├── discountgrid.lay         # Q2 정책 분석 맵
│   └── ...
│
├── test_cases/                  # Autograder 테스트 케이스
│   ├── CONFIG                   # 문항 순서: q1 q2 q3 q4 q5 q6
│   ├── q1/  (4 테스트 · 5점 · PassAllTestsQuestion)
│   ├── q2/  (5 테스트 · 5점 · NumberPassedQuestion)
│   ├── q3/  (4 테스트 · 5점 · PassAllTestsQuestion)
│   ├── q4/  (4 테스트 · 2점 · PassAllTestsQuestion)
│   ├── q5/  (1 테스트 · 1점 · PartialCreditQuestion)
│   └── q6/  (5 테스트 · 3점 · PassAllTestsQuestion)
│
├── Project 2 Instruction.pdf    # 공식 과제 명세서 (13페이지)
└── submission.zip               # 최종 제출 아카이브 (valueIterationAgents.py,
                                 #   qlearningAgents.py, analysis.py)
```

---

## 실행 방법

```bash
# 환경 설정
conda create -n pacman python=3.9 -y
conda activate pacman

# Q1: Gridworld Value Iteration (100회 반복, 10 에피소드)
python gridworld.py -a value -i 100 -k 10

# Q2: 정책 분석 시각화 (예: 2a 파라미터)
python gridworld.py -g DiscountGrid -a value --discount 0.1 --noise 0.0 --livingReward -1.0

# Q3: Gridworld Q-Learning (Q-값 확인을 위한 수동 플레이)
python gridworld.py -a q -k 4 --noise 0.0 -m

# Q4: Epsilon-greedy 동작 확인
python gridworld.py -a q -k 100 -e 0.1

# Q5: Pacman Q-Learning (훈련 2000 + 테스트 10 표시)
python pacman.py -p PacmanQAgent -x 2000 -n 2010 -l smallGrid

# Q6: SimpleExtractor를 이용한 Approximate Q-Learning
python pacman.py -p ApproximateQAgent -a extractor=SimpleExtractor -x 50 -n 60 -l mediumGrid

# Autograder (전체 문항)
python autograder.py

# Autograder (단일 문항)
python autograder.py -q q1
```

---

## PDF / 강의자료 매핑

| 출처 | 내용 |
|------|------|
| `Project 2 Instruction.pdf` — p. 1 | 프로젝트 개요, 제출 규칙(`submission.zip` 3개 파일), 마감일(12월 12일 23:59), 환경(Python 3.9 conda) |
| pp. 2–3 | Autograder 사용법, Gridworld 시작 커맨드, 읽어야 할 파일 목록 |
| p. 4 | Q1 상세: Bellman 업데이트 방정식, $\pi_{k+1}$ / $Q_{k+1}$ 오프셋 주의사항, 테스트 커맨드, 채점 기준 |
| pp. 5–6 | Q2: DiscountGrid 레이아웃, 5가지 정책 목표, 파라미터 튜닝 지침 |
| pp. 7–8 | Q3: Q-Learning 업데이트 규칙, 동점 처리 주의사항; Q4: ε-greedy getAction |
| pp. 9–10 | Q5: Pacman 훈련/테스트 프로토콜, 70% 승률 기준값, `PacmanQAgent` 기본값 |
| pp. 11–12 | Q6: Approximate Q-함수 형태 $Q = \mathbf{w} \cdot \mathbf{f}$, 가중치 업데이트 규칙, `SimpleExtractor` 사용법 |
| p. 13 | 학문적 정직성 정책 (표절 → 자동 F 학점) |

**수치 출처:**
- 5/5/5/2/1/3점 배점 → `test_cases/q*/CONFIG`
- 70승 기준값 → `test_cases/q5/grade-agent.test`
- `ε=0.05, α=0.2, γ=0.8` → `qlearningAgents.py`의 `PacmanQAgent.__init__`

---

## 인용 및 라이선스

```
@misc{berkeley_cs188_p2,
  title        = {Project 2: Reinforcement Learning},
  author       = {DeNero, John and Klein, Dan and Miller, Brad and Hay, Nick and Abbeel, Pieter},
  institution  = {UC Berkeley CS188 Artificial Intelligence},
  url          = {https://ai.berkeley.edu/},
  note         = {Adapted for CSE 17182, Chung-Ang University, Fall 2025}
}
```

**라이선스:** 교육 목적 전용. 원본 Berkeley 저작권 고지 기준:
> *"교육 목적으로 이 프로젝트를 자유롭게 사용하거나 확장할 수 있으나, (1) 솔루션을 배포하거나 출판하지 말 것, (2) 이 고지를 유지할 것, (3) UC Berkeley에 명확한 저작권을 표시할 것."*

**참고 문헌:**
- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press. http://incompleteideas.net/book/the-book-2nd.html
- Watkins, C. J. C. H., & Dayan, P. (1992). Q-learning. *Machine Learning*, 8, 279–292.
- Mnih, V., et al. (2015). Human-level control through deep reinforcement learning. *Nature*, 518, 529–533.
- UC Berkeley CS188 Pacman AI Projects: https://ai.berkeley.edu/
