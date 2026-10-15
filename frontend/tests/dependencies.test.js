import assert from "node:assert/strict";
import test from "node:test";
import { sortTasksByDependencies } from "../src/dependencies.js";

test("sorts tasks by prerequisite and exposes relationships in both directions", () => {
  const tasks = [
    { id: 1, ten: "A" },
    { id: 2, ten: "B" },
    { id: 3, ten: "C" },
    { id: 4, ten: "D" },
  ];
  const dependencies = [
    { task_id: 1, depends_on_task_id: 2 },
    { task_id: 1, depends_on_task_id: 3 },
    { task_id: 2, depends_on_task_id: 4 },
    { task_id: 3, depends_on_task_id: 4 },
  ];

  const result = sortTasksByDependencies(tasks, dependencies);

  assert.deepEqual(result.orderedTasks.map(task => task.id), [4, 2, 3, 1]);
  assert.deepEqual(result.relationships[0].prerequisites.map(task => task.id), [2, 3]);
  assert.deepEqual(result.relationships[3].dependents.map(task => task.id), [2, 3]);
  assert.deepEqual(result.blockedTasks, []);
  assert.equal(result.hasCycle, false);
});

test("distinguishes tasks in a cycle from tasks blocked by it", () => {
  const tasks = [{ id: 1 }, { id: 2 }, { id: 3 }, { id: 4 }];
  const dependencies = [
    { task_id: 1, depends_on_task_id: 2 },
    { task_id: 2, depends_on_task_id: 1 },
    { task_id: 3, depends_on_task_id: 2 },
  ];

  const result = sortTasksByDependencies(tasks, dependencies);

  assert.deepEqual(result.orderedTasks.map(task => task.id), [4]);
  assert.deepEqual(result.blockedTasks.map(task => task.id), [1, 2, 3]);
  assert.deepEqual(result.cycleTasks.map(task => task.id), [1, 2]);
  assert.equal(result.hasCycle, true);
});

test("handles self-cycles, duplicate relationships, and deep graphs iteratively", () => {
  const selfCycle = sortTasksByDependencies(
    [{ id: 1 }],
    [{ task_id: 1, depends_on_task_id: 1 }]
  );
  assert.deepEqual(selfCycle.cycleTasks.map(task => task.id), [1]);

  const duplicate = sortTasksByDependencies(
    [{ id: 1 }, { id: 2 }],
    [
      { task_id: 2, depends_on_task_id: 1 },
      { task_id: 2, depends_on_task_id: 1 },
    ]
  );
  assert.deepEqual(duplicate.orderedTasks.map(task => task.id), [1, 2]);

  const tasks = Array.from({ length: 10000 }, (_, id) => ({ id }));
  const dependencies = tasks.slice(1).map(task => ({
    task_id: task.id,
    depends_on_task_id: task.id - 1,
  }));
  const deep = sortTasksByDependencies(tasks, dependencies);
  assert.equal(deep.orderedTasks.length, tasks.length);
  assert.equal(deep.orderedTasks.at(-1).id, tasks.length - 1);
});

test("rejects dependency edges with unknown task ids", () => {
  assert.throws(
    () => sortTasksByDependencies([{ id: 1 }], [{ task_id: 1, depends_on_task_id: 2 }]),
    /không tồn tại/
  );
});
