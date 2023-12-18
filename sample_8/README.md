Project CI Scheduler
=====================
Welcome to the take-home interview question. We find that interview questions that don't match the work, require implementing algorithms that should be Google'd, or rely on knowing The Trick don't give good signal. We've therefore designed this question to be a close match to day-to-day work. You'll have the same freedoms and constraints that a dev will have, with only a few caveats due to the artificial nature of the interview format:

- Google as much as you like
- Use any language you like
- Use whatever IDEs and tools you like
- Put the problem down, take walks, mull it over in the shower - whatever you need
- You'll have 48 hours from receipt of this package to return a solution, to match the real-world case where we have an external-facing deadline
- **We need a Prod-ready working solution at the end; write your code like it's going to Prod**

Lastly, we understand that your time is precious. We've targeted this problem to take 3-4 hours so that we're not making unreasonable demands on your time.

Problem Overview
----------------
Imagine that you're a dev on the team, and we need to write the scheduling logic of a single-threaded build system. Our users will submit job YAMLs which consist of build steps with precedence, like this:

```yaml
- step: "create user 1"
  dependencies: ["prepare database"]
  precedence: 100
- step: "create user 2"
  dependencies: ["prepare database"]
  precedence: 50
- step: "prepare database"
  dependencies: []
  precedence: 10
```

The scheduling logic you write will process the input and produce an ordering the steps should be executed in. Dependencies must be taken into account: a step must not run until all its dependencies have run. Precedence must also be taken into account: a higher-precedence steps beat lower-precedence steps when both are available for running.

For instance, the only ordering possible for the above example job is:

```
prepare database
create user 1
create user 2
```

Inputs are assumed to come directly from users; no pre-processing or sanitization has been done.

### Input Job Specification

- A job is a list of steps defined in YAML
- A job must have at least one step
- Each step must have a `step` field
- The ID of a step is the value of the `step` field, with the leading and trailing whitespace removed
- Empty or all-whitespace step IDs are not allowed
- Step IDs with newline characters are not allowed
- Multiple steps with the same ID are not allowed
- Each step must have a `precedence` field
- The precedence of a step is the value of the `precedence` field
- Precedence must be a **positive nonzero integer**
- Each step may (but is not required to) have a `dependencies` field containing an array of step IDs
- A step without the `dependencies` key is assumed to have no dependencies
- The dependency IDs are the values of the `dependencies`, field with leading and trailing whitespace removed
- An empty or whitespace dependency ID is not allowed
- Dependencies on nonexistent step IDs are not allowed

### Output Ordering Specification

- An output ordering is a newline-separated list of step IDs (no leading or trailing whitespace)
- **An output ordering is always terminated by a newline**
- All steps in the job must be used exactly once
- A step's dependencies must come before it in the output ordering
- Higher-precedence steps must come before lower-precedence steps when both are available for running
- When two ready-to-run steps have the same precedence, lexicographical ordering is used: step `A` comes before step `B`, etc.

Your Solution
-------------
At a code level, your solution will be a Docker image capable of taking in a user's job YAML and 
producing an output ordering. We've provided you with `scripts/build.sh` infra to build the 
(currently-empty) `Dockerfile` in the root of this repository; you can use this as you develop your solution. 
Your Docker image will be run with two arguments - the filepath on the container of the user's job YAML, 
and the filepath on the container where output should be produced.

For example, this invocation of your image:

```
docker run --volume ${PWD}/input/job.yml:/job.yml --volume ${PWD}/output/output.txt:/output.txt build-ci-scheduler /job.yml /output.txt
```

will use your input file at `${PWD}/job.yml` and write an output ordering to `${PWD}/output.txt` (if one could be produced).

WARNING: make sure `${PWD}/job.yml` and `${PWD/output.txt` exist on your local machine when running the command, 
else you'll get an empty directory inside the Docker container which will cause an error.

At an interview level, your final deliverable submitted back to us should be a `.tgz` of this directory 
containing all your work. Running `scripts/build.sh` in the directory you give us should 
produce a container image that solves the problem. You may add whatever other infra you need, 
but the `scripts/build.sh` in your submitted version must remain identical to the one we give you.

### Solution Specification
- Your solution must be packaged inside a Docker container image via `scripts/build.sh`
- The command your image runs must accept two positional arguments:
    1. The input filepath within the container where the user's job YAML resides
    1. The output filepath within the container where the output ordering should be written to
- Your container must return a `0` exit code if an output ordering was successfully produced
- If an output ordering was successfully produced, the contents of the output file must contain the output ordering
- Your container must return a non-`0` exit code in any case where an output ordering couldn't be produced (e.g. the job is invalid)
- The STDIN/STDOUT of the container are yours to use and log to as you please

### Post Solution Note
- Added a requirement to detect cyclic dependency input and treat as invalid job.
- Used `Pydantic` for its data parsing/validation/adjustment feature. It's possible that the implementation around `Step,Job` class a bit messy with a few abstraction required for using it.
- The alternative was custom implement individual input validation + adjustment logic with plain python class constructs, but I chose former approach for the interest of time.
- I prioritized separation of individual validation logic vs. performance, and there are a few duplicate codes in `Job` class.
- Unit test was added using `pytest`.
- From the directory containing `Dockerfile` run below
```
./scripts/build.sh
docker run --rm --name build -v ./input:/build/input -v ./output:/build/output build-ci-scheduler ./input/test_input.yaml ./output/test_output.txt 
```
- input is expected to be kept at `/build/input/`.
- output is expected to be kept at `/build/output/`.
