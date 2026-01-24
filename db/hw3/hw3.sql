USE UNIVERSITY_DB;

# 쿼리를 작성 목표 : 질의1. 모든 학생에 대해 학생 ID와 F를 포함한 총 수강 학점(takes 테이블 기준)을 조회하시오. 
# (팁: takes 테이블과 student 테이블 간 학생 ID 불일치는 존재하지 않음)
# 쿼리 계산 방법 : GROUP BY 활용
# 데이터의 기간 : 전체
# 사용할 테이블 : takes as t, stduent as s
# 컬럼 : t.ID, s.tot_cred
# Join KEY : ID
# 조건 : 

SELECT
	ID,
    SUM(c.credits) as "SUM"
FROM takes as t
JOIN student as s USING(ID)
JOIN course as c USING(course_id)
GROUP BY ID;

# 쿼리를 작성 목표 : 질의2. 최소 3번 이상 선수과목(prerequisite course)을 가르친 교강사에 대해 ID와 이름, 학과명, 가르친 선수과목 개수를 조회하시오. 
# (힌트: 3개 이상의 선수과목(course)을 가르친 교강사를 조회하는 것이 아니라 선수과목을 3번 이상 가르친(section) 교강사를 조회하는 것)
# 데이터의 기간 : 전체
# 사용할 테이블 : instructor as i / prereq as p, teaches as t
# 컬럼 : i.ID, i.name, i.dept_name, COUNT(course_id)
# Join KEY : 
# 조건 : p.course_id >= 3 / HAVING 

SELECT
	t.ID,
    i.name,
    i.dept_name,
    COUNT(t.course_id)
FROM teaches as t
JOIN prereq as p USING(course_id)
JOIN instructor as i USING(ID)
GROUP BY t.ID
HAVING COUNT(t.course_id) >= 3;
# INNERJOIN은 컬럼을 떨굼

# 쿼리를 작성 목표 : 질의3. 총 100학점(student 테이블의 tot_cred 기준) 이상을 듣고 A+학점이 5개 이상 있는 학생에 대해 
# ID와 이름, 학과명, A+학점 개수를 조회하시오.
# 쿼리 계산 방법 : 
# 데이터의 기간 : 전체
# 사용할 테이블 : student as s / takes as t
# 컬럼 : s.ID, s.name, s.dept_name
# Join KEY : s.ID = t.ID
# 조건 : s.tot_cred >= 100 and COUNT(t.grade = "A+") >= 5

SELECT
	s.ID,
    s.name,
    s.dept_name,
    COUNT(t.ID) as "#A+"
FROM student as s
JOIN takes as t USING(ID)
WHERE s.tot_cred >= 100 AND t.grade = "A+"
GROUP BY s.ID
HAVING COUNT(s.ID) >= 5;

# 쿼리를 작성 목표 : 질의4. 50명 이상의 학생을 지도한 교수자에 대해 ID, 이름, 학과명, 연봉(salary), 지도학생 수를 조회하시오.
# 쿼리 계산 방법 :
# 데이터의 기간 : 
# 사용할 테이블 : instructor as i / advisor as a
# 컬럼 : i.*
# Join KEY : i.ID = a.i_id
# 조건 : 

SELECT
	i.*,
    COUNT(a.s_id) as num_student
FROM instructor as i
JOIN advisor as a on i.ID = a.i_id
GROUP BY i.ID, i.name, i.dept_name, i.salary
HAVING COUNT(a.s_id) >= 50;

# 쿼리를 작성 목표 : 질의5. 한 교강사로부터 재수강을 포함하여 강의를 6번 이상 들은 학생에 대해 ID, 이름, 학과명, 해당 교강사로부터 들은 강의 개수를 조회하 시오.
# 데이터의 기간 : 
# 사용할 테이블 : takes as ta / teaches as te, studnet as s
# 컬럼 : s.ID, s.name, s.dept_name, 
# Join KEY : ta.course_id = te.course_id, ta.ID = s.ID
# 조건
# 1.
# 2.
# 3.
# 

SELECT 
    s.ID,
    s.name,
    s.dept_name,
    COUNT(te.ID)
FROM takes as ta
JOIN teaches as te USING(course_id, sec_id, year, semester)
JOIN student as s ON ta.ID = s.ID
GROUP BY s.ID, s.name, s.dept_name, te.ID
HAVING COUNT(te.ID) >= 6;

# 쿼리를 작성 목표 : 질의6. 2010년도의 모든 강의에 대해 섹션 ID, 코스 ID, 교강사명, 교강사 ID, 교강사 학과명, 수강인원을 조회하시오.
# 데이터의 기간 : year = 2010
# 사용할 테이블 : teaches as te / insturctor as i, takes as ta
# 컬럼 : te.sec_id, se.course_id, i.name, i.ID, i.dept_name, 수강인원
# Join KEY : ta=te USING(course_id, sec_ic, semester, year) / te.ID = i.ID
# 조건
# 1. 
# 2.
# 3.
# 

SELECT 
    te.sec_id, 
    te.course_id, 
    i.name, 
    i.ID, 
    i.dept_name,
    COUNT(ta.ID)
FROM teaches as te
JOIN instructor as i ON te.ID = i.ID
JOIN takes as ta USING(course_id, sec_id, semester, year)
WHERE year = 2010
GROUP BY te.sec_id, te.course_id, i.name, i.ID, i.dept_name;

# 쿼리를 작성 목표 : 질의7. 모든 학과마다 학과명과 선수과목(prerequisite course) 총 학점을 조회하시오.
# (팁: 선수과목이 없는 학과는 존재하지 않음)
# 데이터의 기간 : 없음
# 사용할 테이블 : course as c / prereq as p, department as dept
# 컬럼 : c.dept_name, 선수과목 총 학점
# Join KEY : c.course_id = p.course_id
# 조건
# 1. 
# 2. 
# 3. 
# 

SELECT
    c.dept_name,
    SUM(pc.credits) AS pre_credits
FROM course AS c
JOIN prereq AS p ON c.course_id = p.course_id
JOIN course AS pc ON p.prereq_id = pc.course_id
GROUP BY c.dept_name;


# 쿼리를 작성 목표 : 질의8. 한 과목을 2번 이상 재수강(retaken)한 학생에 대해 ID, 이름, 학과명을 조회하시오.
# 데이터의 기간 : 전체
# 사용할 테이블 : takes as ta / student as s
# 컬럼 : ta.ID, s.name, s.dept_name
# Join KEY : ta.ID = s.ID
# 조건
# 1.
# 2.
# 3.
# 

SELECT 
    s.ID, 
    s.name, 
    s.dept_name
FROM student as s
JOIN (
	SELECT
		ID,
        course_id
	FROM takes
	GROUP BY ID, course_id
    HAVING COUNT(course_id) >= 2
) as temp1 USING(ID)
GROUP BY s.ID, s.name, s.dept_name;

SELECT 
    s.ID, 
    s.name, 
    s.dept_name
FROM student as s
JOIN (
SELECT
	ID,
        course_id
FROM takes
GROUP BY ID, course_id
    HAVING COUNT(course_id) >= 3
) as temp1 USING(ID)
GROUP BY s.ID, s.name, s.dept_name;


# 쿼리를 작성 목표 : 질의9. F를 제외한 총 수강 학점(takes 테이블 기준)과 student 테이블의 총 학점(tot_cred)이 다른 학생의 ID와 이름, 학과명을 조회하시오. 
# (팁: 질의1의 확장 질의이며 대부분의 학생들이 조회되는 것이 정상임)
# 데이터의 기간 : 전체
# 사용할 테이블 : student as s / (SELECT ID, course_id, sec_id, sememster, year, grade FROM takes WHERE grade <> "F ") as t
# 컬럼 : s.ID, s.name, s.dept_name
# Join KEY : s.ID = t.ID
# 조건
# 1. 
# 2.
# 3.
# 

SELECT 
    s.ID,
    s.name,
    s.dept_name
FROM student as s
JOIN (
	SELECT 
		t.ID,
        SUM(c.credits) as tot_grade
	FROM takes as t
    JOIN course as c USING(course_id)
	WHERE (grade <> "F " AND grade <> "F")
    GROUP BY t.ID
) as t ON t.ID = s.ID
WHERE s.tot_cred <> t.tot_grade;

# 쿼리를 작성 목표 : 질의10. F학점을 제외하고 평점이 3.3 이상인 학생들에 대해 ID, 이름, 학과명, F학점을 제외한 평점을 조회하시오.
# (A+: 4, A: 3.666, A-: 3.333, B+: 3, …, C-: 1.333)
# 데이터의 기간 : 전체
# 사용할 테이블 : student as s / takes as t
# 컬럼 : 
# Join KEY : s.ID = t.ID
# 조건
# 1. WHERE grad <> "F "
# 2.
# 3.
# 
CREATE FUNCTION scoring_grade (grade VARCHAR(5))
	RETURNS FLOAT DETERMINISTIC
    RETURN
		CASE grade
			WHEN "A+" THEN 4
            WHEN "A" THEN 3.666
            WHEN "A " THEN 3.666
            WHEN "A-" THEN 3.333
            WHEN "B+" THEN 3
            WHEN "B " THEN 2.666
            WHEN "B" THEN 2.666
            WHEN "B-" THEN 2.333
            WHEN "C+" THEN 2
            WHEN "C" THEN 1.666
            WHEN "C " THEN 1.666
            WHEN "C-" THEN 1.333
		END;
-- DROP FUNCTION scoring_grade;
SELECT 
    s.ID,
    s.name,
    s.dept_name,
    AVG(scoring_grade(t.grade))
FROM student as s
JOIN takes as t USING(ID)
WHERE t.grade <> "F" AND t.grade <> "F "
GROUP BY s.ID, s.name, s.dept_name
HAVING AVG(scoring_grade(t.grade)) >= 3.3;



# 쿼리를 작성 목표 : 질의11. 100명 이상을 수용할 수 있는 강의실에 대해 2006년부터 2010년까지 연도마다의 강의실별 사용횟수를 조회하시오.
# 데이터의 기간 : 2006-2010
# 사용할 테이블 : classroom as room / section as s
# 컬럼 : room.building, room.room_number, year
# Join KEY : room.building = s.building AND room.room_number = s.room_number
# 조건
# 1.WHERE room.capacity >= 100;
# 2.GROUP BY year
# 3.
# 

SELECT 
	s.year,
    room.building,
    room.room_number,
    COUNT(course_id)
FROM section as s
JOIN classroom as room USING(building, room_number)
WHERE year >= 2006 AND year <= 2010 AND room.capacity >= 100
GROUP BY s.year, room.building, room.room_number;

# 쿼리를 작성 목표 : 질의12. 학과마다 학과명, 학생수, 교강사수, 교강사 전체 연봉을 조회하시오. (팁: 교강사가 없는 학과가 존재함 : 수학)
# 데이터의 기간 : 전체
# 사용할 테이블 : department as dept / instructor as i, stduent as s, 
# 컬럼 : dept.dept_name, COUNT(s.ID) as num_student, COUNT(i.ID) as num_instructor, SUM(i.salary)
# Join KEY : dept.dept_name = i.dept_name, dept.dept_name = s.dept_name
# 조건
# 1. GROUP BY dept_name
# 2.
# 3.
# 

SELECT 
    dept.dept_name,
    COUNT(s.ID) as num_student,
    IFNULL(COUNT(DISTINCT i.ID), 0) as num_instructor,
    IFNULL(SUM(i.salary), 0) as num_salary
FROM department as dept
LEFT JOIN student as s USING(dept_name)
LEFT JOIN instructor as i USING(dept_name)
GROUP BY dept.dept_name;


ALTER USER 'root'@'localhost' IDENTIFIED BY '0527';
FLUSH PRIVILEGES;












