# 영화산업 DB 설계 — 영화 예매 시스템

---

## 프로젝트 기본

- **Project Title:** 영화산업 DB 설계
- **One-line summary:** CGV·롯데시네마 등 실제 운영 서비스를 벤치마크하여 산업 수준에 최대한 근접한 영화 예매 DB를 설계하고, Java JDBC(DAO 패턴)로 직접 구현하여 DB 설계와 실제 시스템 적용 역량을 심화한다.
- **Project Type:** System / Pipeline
- **My Role / Key Contribution:**
  - 조장 — DB 전체 설계 최종 검토·통합 (팀원별 부분 설계를 하나의 스키마로 합침)
  - ERD 작성 (IE Notation, drawio 기반)
  - 더미 데이터 생성 스크립트(`generate_dummy_data.py`) 전량 작성
  - 보고서 전 버전(v1–v7) 및 발표자료(PPT) 전량 작성·발표

---

## TL;DR

- **Problem:** 영화관 예매 시스템의 핵심 업무 흐름(회원·좌석·예매·결제·환불)을 정규화된 RDBMS로 모델링하고, Java JDBC로 연동하는 시스템을 팀 협력으로 설계·구현한다.
- **Approach:** **CGV·롯데시네마 등 실제 운영 서비스를 벤치마크**하여 테이블 구조·가격 정책·좌석 유형·회원 등급·쿠폰·간식 스토어 등 실서비스에 존재하는 도메인을 최대한 반영한 스키마를 수립한다. Supabase(PostgreSQL)로 초안 ERD를 설계한 뒤 MySQL 8.x로 이관하고, A-role(조회)·B-role(상태 변경)으로 역할을 분리하여 구현한다. 함수·프로시저·트리거로 DB 내부 비즈니스 로직을 보완한다.
- **Main Result:** 46개 테이블로 구성된 완전한 영화 예매 DB 스키마를 설계·구현하고, 두 역할의 Java 애플리케이션(콘솔 기반 CRUD + 좌석 홀드/예매/결제/환불 플로우)을 정상 구동하였다.
- **Keywords:** `RDBMS`, `MySQL`, `JDBC`, `DAO 패턴`, `ERD`, `정규화`, `트리거/프로시저`, `영화 예매`, `벤치마크 설계`

---

## Motivation & Background

- **Background:** 관계형 데이터베이스 수업의 팀 프로젝트로, CGV·롯데시네마·메가박스 등 국내 주요 멀티플렉스 서비스를 직접 벤치마크하여 실제 운영 수준에 최대한 근접한 DB를 설계하는 것을 핵심 목표로 삼았다.
- **Why this problem matters:** 영화 예매 시스템은 동시성(좌석 홀드), 상태 전이(PENDING → CONFIRMED → CANCELLED), 복합 가격 정책(요일/시간대/좌석 유형별 할인·인상), 환불 정책, 회원 등급 관리 등 다양한 DB 설계 패턴이 응집된 실질적 사례로, 이를 산업 수준으로 설계하면 실무 역량을 직접 체득할 수 있다.
- **Gap in existing work:** 강의에서 다루는 단순 CRUD 수준의 예시 대비, 실서비스 수준의 복합 관계(46개 테이블, 복수 FK, 복합 PK)와 트랜잭션 안전성(트리거·프로시저)을 직접 설계·검증하는 경험이 부족하다. 특히 실서비스 벤치마크 없이는 간식 스토어(`snack_store`), 추천(`recommendation`), 감사 로그(`audit_log`) 같은 운영 필수 도메인이 설계에서 누락되기 쉽다.
- **Related work:** CGV(cgv.co.kr), 롯데시네마(lottecinema.co.kr), 메가박스(megabox.co.kr) 서비스 흐름 직접 분석 (회원가입·좌석 선택·결제·취소 플로우 및 가격 정책 UI 기준). 수업 교재: 추가 필요.

---

## Approach

### System / Pipeline

#### 설계 최우선 원칙: 실서비스 벤치마크

> CGV·롯데시네마·메가박스 등 실제 운영 멀티플렉스 서비스를 기준으로 벤치마크하여,
> 학습용 예시 수준이 아닌 **실서비스 도메인을 최대한 반영**하는 것을 설계의 최우선 목표로 삼았다.

실서비스 분석을 통해 설계에 반영한 주요 도메인:

| 도메인 | 반영 테이블 | 실서비스 근거 |
|--------|------------|-------------|
| 영화·배급·관람등급 | `movie`, `distributor`, `age_rating` | CGV/롯데의 배급사 정보, 등급 분류 |
| 포맷(2D/3D/4DX 등) | `movie_version` (format 컬럼) | 실서비스의 상영 포맷 다변화 |
| 좌석 유형별 차등 가격 | `seat_type`, `price_rule`, `price` | CGV 프리미엄/커플/장애인석 등 |
| 요일·시간대 가격 규칙 | `price_rule_applies` (day_of_week, time_from/to) | 조조·심야·주말 할인 정책 |
| 회원 등급 | `member_tier` (BRONZE/SILVER/GOLD/PLATINUM) | CGV 멤버십 등급 |
| 쿠폰·프로모션 | `coupon`, `coupon_redeem`, `promotion` | 할인 쿠폰·이벤트 |
| 간식 스토어 | `snack_store`, `menu`, `snack_order` | CGV/롯데 팝콘 패키지 주문 |
| 추천 시스템 | `recommendation`, `movie_similarity` | 실서비스의 "이런 영화는 어때요?" |
| 감사 로그 | `audit_log` | 운영 시스템의 변경 이력 추적 |
| 티켓·QR | `ticket` (qr_code 컬럼) | 모바일 티켓 발권 |
| 알림 | `notification` | 예매 확인 푸시/이메일 알림 |

- **System architecture (컴포넌트):**

  ```
  [콘솔 UI (Scanner 기반)]
        ↓
  [Service Layer]  ← 비즈니스 로직 (BookingService, SeatService 등)
        ↓
  [DAO Layer]      ← SQL 실행 (BookingDao, SeatDao 등)
        ↓
  [DBUtil]         ← JDBC 커넥션 (환경변수 DB_URL / DB_USERNAME / DB_PASSWORD)
        ↓
  [MySQL 8.x DB]   ← 46개 테이블, 함수 3개, 프로시저 3개, 트리거 4개
  ```

- **Data flow (역할 분리):**

  | 역할 | 담당 테이블 | 주요 흐름 |
  |------|------------|-----------|
  | **A-role** (조회 중심) | `movie`, `movie_version`, `theater`, `screen`, `seat`, `showtime`, `price` | 영화·상영관·좌석 조회 → 좌석 상태 계산(`hold_seat` + `booking_seat` 합산) |
  | **B-role** (상태 변경 중심) | `member`, `hold_seat`, `booking`, `booking_seat`, `payment` | 회원 가입/로그인 → 좌석 홀드 → 예매 생성 → 결제 → 취소/환불 |

- **Control flow (B-role 메인 예매 흐름):**

  ```
  로그인 / 회원가입
    → 영화·상영시간 선택
    → 좌석 홀드 (hold_seat, 만료시간 설정)
    → 예매 생성 (booking + booking_seat, status=PENDING)
    → 결제 (payment, status=APPROVED)
    → 트리거 자동 실행: booking.status → CONFIRMED, total_amount 산출
    → 취소 시: sp_cancel_booking_with_refund 프로시저 호출 → refund 레코드 생성
  ```

- **DB 내장 비즈니스 로직:**

  | 종류 | 이름 | 기능 |
  |------|------|------|
  | 함수 | `fn_get_final_price` | 상영 ID + 좌석 ID → 최종 가격 계산 |
  | 함수 | `fn_apply_price_rule` | 가격 규칙(할인/인상, 고정/비율) 적용 |
  | 함수 | `fn_calc_refund_amount` | 환불 금액 계산 (상영 20분 전 기준 100%/0%) |
  | 프로시저 | `sp_cleanup_expired_hold_seat` | 만료된 홀드 좌석 일괄 삭제 |
  | 프로시저 | `sp_recalc_member_tier` | 누적 결제액 기준 회원 등급 재계산 |
  | 프로시저 | `sp_cancel_booking_with_refund` | 예매 취소 + 환불 레코드 생성 |
  | 트리거 | `trg_hold_seat_after_insert` | hold_seat 삽입 시 만료 홀드 자동 정리 |
  | 트리거 | `trg_payment_after_insert` | 결제 승인 시 booking 상태/금액 자동 갱신 + audit_log |
  | 트리거 | `trg_booking_insert_audit` | 신규 예매 시 audit_log 기록 |
  | 트리거 | `trg_booking_update_audit` | 예매 상태/금액 변경 시 audit_log 기록 |

- **Deployment / Serving:** 로컬 콘솔 애플리케이션. DB 접속 정보는 환경변수(`DB_URL`, `DB_USERNAME`, `DB_PASSWORD`)로 분리 관리.
- **Monitoring / Logging:** `audit_log` 테이블로 예매 생성·변경·결제 이벤트를 DB 레벨에서 자동 기록.
- **Scaling / Performance:** 추가 필요: 인덱스 전략 및 커넥션 풀 설정

---

## Data & Experiment

- **Dataset type:** 정형 데이터 (관계형 DB 더미 데이터)
- **Source:** `notebook_ty/generate_dummy_data.py`로 생성한 합성 데이터 (`random.seed(42)`)
- **Size (더미 데이터 레코드 수):**

  | 테이블 | 레코드 수 |
  |--------|---------|
  | movie | 80 |
  | member | 250 |
  | showtime | 200 |
  | seat | 600 |
  | booking | 250 |
  | payment | 230 |
  | booking_seat | 400 |
  | hold_seat | 60 |
  | theater | 15 |
  | screen | 30 |
  | review | 200 |
  | coupon | 80 |
  | refund | 40 |
  | 기타 (전체 46개 테이블) | 추가 필요 |

- **Label / Target definition:** 해당 없음 (지도학습 아님). 예매 상태 컬럼(`booking.status`: PENDING / CONFIRMED / CANCELLED)이 핵심 상태값.
- **Preprocessing:** Python 스크립트로 INSERT SQL 직접 생성. 날짜 범위 기준일: `2023-01-01`.
- **Leakage checks:** 해당 없음 (ML 데이터셋 아님).
- **Split:** Train/Val/Test 없음. 기능 검증 목적의 더미 데이터.
- **Evaluation protocol:** 각 역할(A/B)별 Java 실행 시 콘솔 출력 결과 육안 검증.
- **Metrics:** 정량 지표 없음. 기능 정상 동작 여부(CRUD 성공, 예매 상태 전이, 트리거 자동 실행) 확인.
- **Environment:**
  - OS: macOS
  - DB: MySQL 8.x (`jdbc:mysql://localhost:3306`)
  - Java: 추가 필요 (Gradle 빌드, IDEA 프로젝트)
  - ERD 설계 보조: Supabase (PostgreSQL) → 실제 구현은 MySQL로 이관
- **Frameworks / Libraries:**
  - Java JDBC (`com.mysql.cj.jdbc.Driver`, MySQL Connector/J)
  - Gradle (빌드 도구, B-role)
  - Python 3 (`random`, `datetime` — 더미 데이터 생성용)
  - drawio (ERD 작성)
- **Reproducibility:** 더미 데이터 생성 시 `random.seed(42)` 고정.

---

## Results

- **Baseline method:** 해당 없음 (비교 대상 ML 모델 없음).
- **This Work:** 46개 테이블 스키마 완전 구현, A-role 6개 조회 API·B-role 7개 상태 변경 API 정상 구동, 트리거 4개·프로시저 3개·함수 3개 MySQL 배포 완료.
- **Additional results:** 추가 필요: 쿼리 실행 시간 측정값, 좌석 동시성 충돌 테스트 결과
- **Statistical significance:** 해당 없음.
- **Visualization notes:**
  - `notebook_ty/ERD.png` — 최종 ERD 다이어그램 (IE Notation)
  - `notebook_ty/IE_Notation.png` — ERD drawio 렌더 결과
  - `kyuhyun_File/영화관 예매 테이블 erd_diagram.png` — A-role 테이블 ERD
  - `kyuhyun_File/영화관 예매 테이블-절충안(ERD_Diagram).png` — 절충안 ERD
  - `notebook_ty/그림1~7.png` — 보고서 삽입용 스크린샷/다이어그램

---

## Discussion

- **Key observations:**
  1. 좌석 상태 계산을 DB에서 직접 쿼리하는 방식(hold_seat + booking_seat 조인)은 A-role의 핵심 설계 포인트로, 애플리케이션 레이어 부담을 줄인다.
  2. ERD 초안을 Supabase(PostgreSQL)로 작성한 뒤 MySQL로 이관하는 과정에서 문법 차이(`nextval` vs `AUTO_INCREMENT`, `jsonb` vs `json`)를 직접 해결하며 이기종 DB 차이를 학습했다.
  3. 트리거를 활용하여 결제 승인 시 예매 상태 자동 갱신과 audit_log 기록을 DB 레벨에서 처리함으로써 애플리케이션 코드 단순화와 데이터 일관성을 동시에 달성했다.
  4. 팀원 간 A/B 역할로 테이블을 분리한 설계가 협업 충돌을 최소화하는 데 효과적이었다.
- **Interpretation:** 단순 CRUD를 넘어 가격 규칙, 등급 재계산, 환불 정책 등을 DB 내장 로직으로 구현함으로써 비즈니스 규칙이 어플리케이션이 아닌 DB 계층에 종속될 때의 장단점을 체득했다.
- **Trade-offs:** DB 내장 로직(트리거·프로시저)은 일관성 보장에 유리하지만, 테스트·디버깅·이식성이 취약해진다. 반대로 애플리케이션 레이어에서 처리하면 유연성은 높아지나 중복 구현 위험이 생긴다.
- **Failure cases / Surprising results:** 좌석 동시 홀드 시 중복 방지 처리가 애플리케이션 레벨에서만 이루어져 DB 레벨 유니크 제약 또는 비관적 락이 부재하다는 점이 한계로 식별되었다.
- **What I learned:**
  1. ERD 설계 시 정규화 수준(3NF)과 반정규화(성능) 사이의 균형 결정 방법
  2. 트리거·프로시저를 통한 DB 내장 비즈니스 로직 구현 및 실제 적용 경험
  3. 팀 협업에서의 역할 분리(A/B role) 설계가 코드 충돌을 줄이는 실질적 방법

---

## Limitations & Future Work

- **Limitations:**
  1. 콘솔 기반 UI로 제한되어 실사용자 시나리오(동시 접속, 대량 요청)를 검증하지 못함
  2. 좌석 동시성 처리를 DB 레벨(SELECT FOR UPDATE, 유니크 제약)에서 보장하지 않아 레이스 컨디션 취약
  3. DB 접속 정보를 환경변수로만 관리하며 커넥션 풀(HikariCP 등) 미도입
  4. 트리거·프로시저가 MySQL 전용 문법으로 작성되어 타 RDBMS 이식 어려움
  5. 더미 데이터가 단일 스크립트 생성 기반으로 실제 영업 패턴(피크타임 집중, 인기 영화 쏠림 등)을 반영하지 못함
- **Future directions:**
  1. Spring Boot + JPA 전환을 통한 ORM 기반 구조로 리팩토링
  2. 좌석 선점 로직에 SELECT FOR UPDATE 또는 Redis 기반 분산 락 도입
  3. REST API 서버로 확장하여 프론트엔드(예: React)와 연동
  4. 테스트 자동화 (JUnit + Testcontainers로 DB 통합 테스트)
- **If I had more time:** 실제 결제 PG 연동 모킹, 추천 로직(`movie_similarity`, `recommendation` 테이블 활용)의 쿼리 구현, 성능 테스트(대량 동시 예매 시나리오)

---

## Project Structure

```
Database_05-_03-/
├── README.md
├── AandB_role_API                        # A/B 역할 분담 및 API 명세
├── movie_reservation_doc_v5.docx         # 합본 보고서 (루트 최신본)
│
├── king_file/                            # B-role (상태 변경 중심)
│   ├── ERD.pdf                           # ERD 다이어그램 PDF
│   ├── erd_query                         # Supabase(PostgreSQL) ERD 초안 쿼리
│   ├── 영화 예매 시스템 테이블 설계.docx
│   ├── movie_reservation_doc_king.docx
│   └── MovieReservation/                 # B-role Java 프로젝트 (Gradle)
│       ├── Main.java                     # ★ B-role 엔트리포인트 (콘솔 전체 흐름)
│       ├── schema.sql                    # ★ MySQL 최종 스키마 (46개 테이블)
│       ├── dummy_data.sql                # 더미 데이터 INSERT (스크립트 생성 결과)
│       ├── SQL(함수, 프로시저, 트리거)   # ★ DB 내장 로직 (함수 3, 프로시저 3, 트리거 4)
│       ├── dao/   (BookingDao, MemberDao, PaymentDao 등 12개)
│       ├── model/ (Booking, Member, Payment 등 13개)
│       ├── service/ (BookingService, MemberService 등 10개)
│       └── util/DBUtil.java              # JDBC 커넥션 (환경변수 기반)
│
├── kyuhyun_File/                         # A-role (조회 중심)
│   ├── 영화관 예매 테이블 erd_diagram.png
│   ├── 영화관 예매 테이블-절충안(ERD_Diagram).png
│   └── A_roll_source_code/              # A-role Java 소스코드
│       ├── ServiceAll.java              # ★ A-role 통합 실행 엔트리포인트
│       ├── MovieMain.java / SeatMain.java 등 (엔티티별 단독 실행)
│       ├── Readme_md                    # A-role 기능 설명
│       ├── dao/ model/ service/ db/
│
└── notebook_ty/                          # 강태영 (조장) — 문서/ERD/더미데이터
    ├── README.md                         # 작업 현황 메모
    ├── ERD.png / IE_Notation.png         # ★ ERD 시각화 결과물
    ├── IE_Notation.drawio                # ★ ERD drawio 원본
    ├── generate_dummy_data.py            # ★ 더미 데이터 생성 스크립트
    ├── ppt.py                            # PPT 생성 보조 스크립트
    ├── movie_reservation_doc_v1~v7.*     # 보고서 버전 이력
    ├── Movie Reservation_ppt.pdf/.pptx  # ★ 최종 발표자료
    └── 그림1~7.png, table_sketch.png    # 보고서/발표용 다이어그램
```

---

## 실행 방법

### 사전 조건

1. MySQL 8.x 설치 및 실행 (기본 포트 `3306`)
2. 데이터베이스 생성 후 스키마 및 더미 데이터 적용:

```bash
# 1. 스키마 생성
mysql -u <user> -p <dbname> < king_file/MovieReservation/schema.sql

# 2. 더미 데이터 생성 (SQL 파일 출력)
python3 notebook_ty/generate_dummy_data.py > dummy_insert.sql

# 3. 더미 데이터 적재
mysql -u <user> -p <dbname> < dummy_insert.sql
```

3. 환경변수 설정:

```bash
export DB_URL="jdbc:mysql://localhost:3306/<dbname>"
export DB_USERNAME="<user>"
export DB_PASSWORD="<password>"
```

### B-role 실행 (전체 예매 시스템 콘솔)

```bash
cd king_file/MovieReservation
./gradlew run          # 또는 IntelliJ IDEA에서 Main.java 실행
```

### A-role 실행 (조회 기능 통합 테스트)

```bash
# ServiceAll.java 컴파일 후 실행
javac -cp . ServiceAll.java
java ServiceAll
```

---

## PDF / Slides Mapping

- **Main slide deck(s):** `notebook_ty/Movie Reservation_ppt.pdf` / `Movie Reservation_ppt.pptx` (최종 발표자료)
- **Slide-to-README mapping:**
  - Problem statement slide(s): 추가 필요 (PDF 미열람)
  - Method/Architecture slide(s): 추가 필요
  - Experiment setup slide(s): 추가 필요
  - Results/Comparison slide(s): 추가 필요
  - Ablation/Analysis slide(s): 해당 없음
  - Conclusion/Future work slide(s): 추가 필요
- **Numbers provenance:** 추가 필요 (PDF 내용 확인 후 기입)
- **Any missing slides / gaps:** PDF 미열람 상태. `notebook_ty/Movie Reservation_ppt.pdf` 열람 후 위 항목 보완 필요.

---

## Citation & License

- **Citation info:** 추가 필요 (수업명, 교수명, 제출일)
- **License:** 추가 필요
- **Papers / links:** 추가 필요