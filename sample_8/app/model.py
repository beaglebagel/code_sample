from collections import Counter
from typing import Any

from functools import total_ordering
from pydantic import BaseModel, Field, StrictInt, model_validator

from pydantic import AfterValidator, StringConstraints
from typing_extensions import Annotated


def validate_str(value: str) -> str:
    # common str validator method.
    if not value:
        raise ValueError(f'{value=} cannot be empty.')
    elif str.isspace(value):
        raise ValueError(f'{value=} cannot be all white-spaces.')
    elif '\n' in value:
        raise ValueError(f'{value=} cannot contain newline (\n) character.')
    return value


# Custom String type to validate & preprocess input step id info. Applied left -> right.
ValidatedStr = Annotated[str, AfterValidator(validate_str), StringConstraints(strip_whitespace=True)]


@total_ordering
class Step(BaseModel):
    '''
    Step class to represent each step block from input YAML
    e.g.
      - step: "create user 1"
        dependencies: ["prepare database"]
        precedence: 100
    Each Steps are orderable by 1. higher precedence (e.g. 100 > 10)
                                2. lower lexicographical order of step id (e.g. 'a' > 'b')
    Follows below spec.
    - Each step must have a `step` field
    - The ID of a step is the value of the `step` field, with the leading and trailing whitespace removed
    - Empty or all-whitespace step IDs are not allowed
    - Step IDs with newline characters are not allowed
    - Each step must have a `precedence` field
    - The precedence of a step is the value of the `precedence` field
    - Precedence must be a **positive nonzero integer**
    - Each step may (but is not required to) have a `dependencies` field containing an array of step IDs
    - A step without the `dependencies` key is assumed to have no dependencies
    - The dependency IDs are the values of the `dependencies`, field with leading and trailing whitespace removed
    - An empty or whitespace dependency ID is not allowed

    '''
    id: ValidatedStr = Field(alias='step')
    dependencies: list[ValidatedStr] = Field(default_factory=list)
    precedence: StrictInt = Field(gt=0)

    def __lt__(self, other: 'Step') -> bool:
        # precedence 100 > precedence 50
        # id 'a' > id 'b'
        if self.precedence == other.precedence:
            # lexicographic order 'a' > 'b' & 'A' > 'B'.
            return self.id > other.id
        return self.precedence < other.precedence

    def __eq__(self, other: 'Step') -> bool:
        return (self.id, self.dependencies, self.precedence) == (other.id, other.dependencies, other.precedence)


class Job(BaseModel):
    '''
    Job class represents step blocks defined in input YAML, and provides functions to generate step schedule.

    Follows below spec.
    - A job is a list of steps defined in YAML
    - A job must have at least one step
    - Multiple steps with the same ID are not allowed
    - Dependencies on nonexistent step IDs are not allowed
    - Steps with cyclic dependency is not allowed
    - @NOTE: cyclic dependency detection is not part of requirement but is assumed as possible case of unprocessed input.
    '''
    steps: list[Step]
    step_map: dict[str, Step] = Field(default_factory=dict)
    starters: set = Field(default_factory=set)

    # Below are set of checks that validate Job Step's validity in entirety.
    @staticmethod
    def validate_step_uniqueness(steps: list[Step]) -> None:
        # check for any duplicate step ids.
        step_counter = Counter([step.id for step in steps])
        duplicate_steps = list(filter(lambda x: x[1] > 1, step_counter.items()))
        if duplicate_steps:
            raise ValueError(f'Duplicate Step IDs not allowed - {duplicate_steps=}')

    @staticmethod
    def validate_step_existence(steps: list[Step]) -> None:
        # check steps referred as dependency exists.
        all_steps = set([step.id for step in steps])
        all_dependencies = set([dep for step in steps for dep in step.dependencies])
        missing_dependencies = all_dependencies.difference(all_steps)
        if missing_dependencies:
            raise ValueError(f'Invalid Dependency IDs - {missing_dependencies=}')

    @staticmethod
    def validate_non_cyclic(steps: list[Step]) -> None:
        # check if any cycle exists within given steps through DFS.

        def _search(step: Step, path: set, step_map: dict[str, Step]) -> None:
            if step.id in path:
                raise ValueError(f'Circular dependency detected on {step.id=}, invalid workflow.')
            path.add(step.id)
            # recursively check for each dependencies.
            for dep in [step_map[dep] for dep in step.dependencies]:
                _search(step=dep, path=path, step_map=step_map)
            path.remove(step.id)

        for step in steps:
            _search(step=step, path=set(), step_map={step.id: step for step in steps})

    @model_validator(mode='after')
    def validate_steps(self) -> 'Job':
        '''
        Main validator method that triggers individual validation of set categories
            - step uniquess
            - dependency existence
            - non-cyclic dependency

        This validation is executed after class is instantiated.

        Returns
        -------
        this instance
        '''
        if not self.steps:
            raise ValueError('Job: Requires at least one step.')

        self.validate_step_existence(steps=self.steps)
        self.validate_step_existence(steps=self.steps)
        self.validate_non_cyclic(steps=self.steps)
        return self

    def model_post_init(self, __context: Any) -> None:
        # build step value -> Step mapping.
        self.step_map = {step.id: step for step in self.steps}
        all_dependencies = set([dep for step in self.steps for dep in step.dependencies])
        # find possible starting points that do not.
        self.starters = set(self.step_map.keys()).difference(all_dependencies)

    def _topological_sort(self, step: Step, visited: set[str], orders: list[str]) -> None:

        if step.id in visited:
            return
        visited.add(step.id)

        deps = [self.step_map[dep] for dep in step.dependencies]
        for dep in sorted(deps, reverse=True):
            self._topological_sort(step=dep, visited=visited, orders=orders)
            # clear from current path.
        orders.append(step.id)

    def generate_schedule(self) -> list[str]:
        '''
        Perform topological search / sort through Job's steps.

        Returns
        -------
        list of sorted steps id.
        '''
        visited, orders = set(), []
        for step in sorted([self.step_map[step_id] for step_id in self.starters], reverse=True):
            self._topological_sort(step=step, visited=visited, orders=orders)
        return orders
