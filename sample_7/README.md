## Project

At `https://live-test-scores.herokuapp.com/scores` you'll find a service that follows the [Server-Sent Events](https://html.spec.whatwg.org/multipage/server-sent-events.html#server-sent-events) protocol. You can connect to the service using cURL:

        curl https://live-test-scores.herokuapp.com/scores

Periodically, you'll receive a JSON payload that represents a student's test score (a JavaScript number between 0 and 1), the exam number, and a student ID that uniquely identifies a student. For example:

        event: score
        data: {"exam": 3, "studentId": "foo", score: .991}

This represents that student foo received a score of `.991` on exam #3. 

Build an application that consumes this data, processes it, and provides a simple REST API that exposes the processed results. 

 REST API we want you to build:

1. A REST API `/students` that lists all users that have received at least one test score
2. A REST API `/students/{id}` that lists the test results for the specified student, and provides the student's average score across all exams
3. A REST API `/exams` that lists all the exams that have been recorded
4. A REST API `/exams/{number}` that lists all the results for the specified exam, and provides the average score across all students

Coding tests are often contrived, and this exercise is no exception. To the best of your ability, make your solution reflect the kind of code you'd want shipped to production. A few things we're specifically looking for:

* Well-structured, well-written, idiomatic, safe, performant code.
* Tests, reflecting the level of testing you'd expect in a production service.
* Good RESTful API design. Whatever that means to you, make sure your implementation reflects it, and be able to defend your design.
* Ecosystem understanding. Your code should demonstrate that you understand whatever ecosystem you're coding against— including project layout and organization, use of third party libraries, and build tools.
* Store the results in memory instead of a persistent store. In production code, you'd never do this, of course.

That said, we'd like you to cut some corners so we can focus on certain aspects of the problem:

We're looking for a functional REST API that meets the criteria above, but there are no "gotchas," and there is no single "right" solution. Please use your best judgment and be prepared to explain your decisions in the on-site review.

## *** Instruction to run ***

The solution is based on **Python (Ver 3.10)**
Please ensure there is docker daemon running on the host machine.

Within root directory, please run the following.
1. `docker build -t <image name> .`
2. W/ Plain Docker: `docker run --rm --name <image name> -d -v ./app:/ld/app -p 8000:8000 <container name>`
3. Or W/ Docker Compose `docker compose up --build` 

FastAPI server should be running with port 8000 open at this point.
3. Access apis under `localhost:8000/`
   1. `localhost:8000/students/` -> returns received student info in realtime.
   2. `localhost:8000/students/{student_id}` -> returns all student info + average score of all students.
   3. `localhost:8000/exams/` -> returns received exam info in realtime.
   4. `localhost:8000/exams/{exam_id}` -> returns all exam info + average scores of all students.
   5. API Doc: `localhost:8000/docs`

To stream the logs, run `docker logs -f <container_name>`