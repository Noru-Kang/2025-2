USE UNIVERSITY_DB;
# 쿼리를 작성 목표 : 질의1. 모든 학생의 ID, 이름, 학과명을 이름 오름차순으로 조회하시오.
# 쿼리 계산 방법 : 없음
# 데이터의 기간 : 전체
# 사용할 테이블 : UNIVERSITY_DB.student
# 컬럼 : ID, name, dept_name
# Join KEY : 없음
# 조건 : name ASC

SELECT 
    ID, 
    IFNULL(name, 0) as name, 
    dept_name
FROM student
ORDER BY name ASC;

# 쿼리를 작성 목표 : 질의2. 학점(course 테이블의 credits 기준)이 3 이상인 과목의 과목코드, 제목, 학점을 학점 내림차순, 제목 오름차순으로 조회하시오. 
# 쿼리 계산 방법 : credits >= 3
# 데이터의 기간 : 전체
# 사용할 테이블 : UNIVERSITY_DB.course
# 컬럼 : course_id, title, dept_name, credits
# Join KEY : 없음
# 조건 : credits DESC, title ASC

SELECT 
	course_id,
    IFNULL(title, 0) as title,
    dept_name,
    credits
FROM course
WHERE credits >= 3
ORDER BY credits DESC, title ASC;
    
# 쿼리를 작성 목표 : 질의3. 총 100학점(student 테이블의 tot_cred 기준) 이상 이수한 학생들의 이름과 총 이수 학점을 학점이 높은 순으로 조회하시오.
# 쿼리 계산 방법 : tot_cred >= 100
# 데이터의 기간 : 전체
# 사용할 테이블 : student
# 컬럼 : name, tot_cred
# Join KEY : ID-ID(takes), (takes)course_id-course_id(section), (section)course_id-course_id(course)
# 조건 : 

SELECT 
	name,
    tot_cred
FROM student
WHERE tot_cred >= 100
ORDER BY tot_cred DESC;

# 쿼리를 작성 목표 : 질의4. 학점(course 테이블의 credits 기준)이 3 이상인 과목의 과목코드, 제목, 학점을 학점 내림차순, 제목 오름차순으로 조회하시오.
# 쿼리 계산 방법 : credits >= 3
# 데이터의 기간 : 전체
# 사용할 테이블 : course
# 컬럼 : course_id, title, credits
# Join KEY : 없음
# 조건 : credits DESC, title ASC

SELECT 
	course_id,
    title,
    credits
FROM course
WHERE credits >= 3
ORDER BY credits DESC, title ASC;

# 쿼리를 작성 목표 : 질의5. 소속 학생이 100명 이상인 학과와 그 학생 수를 조회하시오.
# 쿼리 계산 방법 : GROUP BY dept_name, count(ID) >= 100
# 데이터의 기간 : 전체
# 사용할 테이블 : student
# 컬럼 : dept_name, count(ID)
# Join KEY : 없음
# 조건 : 없음

SELECT 
	dept_name,
    count(ID) as count
FROM student
GROUP BY dept_name
HAVING count >= 100;

# 쿼리를 작성 목표 : 질의6. 개설 과목 수가 10개 이상인 학과만 학과명, 과목수를 조회하시오.
# 쿼리 계산 방법 : GROUP BY dept_name, count(course_id) >= 10
# 데이터의 기간 : 전쳉
# 사용할 테이블 : course
# 컬럼 : dept_name, count(course_id)
# Join KEY : 없음
# 조건 : 없음

SELECT 
	dept_name,
    count(course_id) as count
FROM course
GROUP BY dept_name
HAVING count >= 10;

# 쿼리를 작성 목표 : 질의7. 수용 인원(capacity)이 100명 이상인 강의실의 건물, 호실, 수용인원을 수용인원 내림차순으로 조회하시오.
# 쿼리 계산 방법 : capacity >= 100
# 데이터의 기간 : 전체
# 사용할 테이블 : classroom
# 컬럼 : building, room_number, capacity
# Join KEY : 없음
# 조건 : capacity <= 100;

SELECT 
	building,
    room_number,
    IFNULL(capacity, 0) as capacity
FROM classroom
WHERE capacity >= 100;

# 쿼리를 작성 목표 : 질의8. 2009년에 열린 강의가 각 학기(semester)별로 몇 개인지 조회하시오.
# 쿼리 계산 방법 : GROUP BY semester
# 데이터의 기간 : year = 2009
# 사용할 테이블 : semester, section
# 컬럼 : count(course_id)
# Join KEY : 없음
# 조건 : 없음

SELECT
	semester,
    count(course_id)
FROM section
WHERE year=2009
GROUP BY semester;

# 쿼리를 작성 목표 : 질의9. (takes 테이블 기준) 한 학생이 특정 과목을 3번 이상 수강한 경우를 찾아 해당 학생의 ID와 과목 ID, 수강 횟수를 조회하시오.
# 쿼리 계산 방법 : GROUP BY ID, course_id, count(ID) >= 3
# 데이터의 기간 : 전체
# 사용할 테이블 : takes
# 컬럼 : ID, course_id,
# Join KEY : 없음
# 조건 : 없음

SELECT
    ID,
    course_id,
    count(course_id) as count
FROM takes
GROUP BY ID, course_id
HAVING count >= 3;

# 쿼리를 작성 목표 : 질의10. ‘A+’ 또는 ‘A’학점을 10번 이상 받은 학생의 ID와 해당 우수 학점(’A+’, ’A’)의 총 횟수를 조회하시오.
# 쿼리 계산 방법 : GROUP BY ID, grade / count(grade = "A+" and grade = "A") >= 10
# 데이터의 기간 : 전체
# 사용할 테이블 : takes
# 컬럼 : ID, grade
# Join KEY : 없음
# 조건 : 없음
# 와 공백이 있

SELECT 
	ID,
	COUNT(grade) AS count
FROM takes
WHERE grade='A+' OR grade='A '
GROUP BY ID
HAVING count >= 10;

# 쿼리를 작성 목표 : 질의11. 2007년에 2번 이상 사용된 강의실(건물과 호수 기준)과 그 사용 횟수를 조회하시오.
# 쿼리 계산 방법 : count
# 데이터의 기간 : year="2007"
# 사용할 테이블 : section
# 컬럼 : building, room_number, count(room_number) as count
# Join KEY : 없음
# 조건 : 

SELECT
	building,
	room_number,
    count(room_number) as count
FROM section
WHERE year="2007"
GROUP BY building, room_number
HAVING count >= 2;

# 쿼리를 작성 목표 : 질의12. 각 학과별 소속 교강사 수가 3명 이상인 학과와 그들의 총 연봉 합계를 조회하시오.
# 쿼리 계산 방법 : GROUP BY dept_name / count(ID) >= 3 / sum(salary)
# 데이터의 기간 : 전체
# 사용할 테이블 : instructor
# 컬럼 : dept_name, sum(salary)
# Join KEY : 없음
# 조건 : 없음

SELECT 
	dept_name,
    sum(salary)
FROM instructor
GROUP BY dept_name
HAVING count(ID) >= 3;





