export function sortTasksByDependencies(tasks, dependencies) {
  const tasksById = new Map();
  const successors = new Map();
  const predecessors = new Map();

  for (const task of tasks) {
    if (tasksById.has(task.id)) {
      throw new Error(`Id công việc bị trùng: ${task.id}`);
    }
    tasksById.set(task.id, task);
    successors.set(task.id, new Set());
    predecessors.set(task.id, new Set());
  }

  for (const relation of dependencies) {
    const { task_id: taskId, depends_on_task_id: prerequisiteId } = relation;
    if (!tasksById.has(taskId) || !tasksById.has(prerequisiteId)) {
      throw new Error("Quan hệ phụ thuộc tham chiếu đến công việc không tồn tại.");
    }

    successors.get(prerequisiteId).add(taskId);
    predecessors.get(taskId).add(prerequisiteId);
  }

  const indegree = new Map(
    tasks.map(task => [task.id, predecessors.get(task.id).size])
  );
  const queue = tasks
    .filter(task => indegree.get(task.id) === 0)
    .map(task => task.id);
  const orderedIds = [];

  for (let cursor = 0; cursor < queue.length; cursor += 1) {
    const currentId = queue[cursor];
    orderedIds.push(currentId);
    for (const successorId of successors.get(currentId)) {
      const remaining = indegree.get(successorId) - 1;
      indegree.set(successorId, remaining);
      if (remaining === 0) queue.push(successorId);
    }
  }

  const orderedSet = new Set(orderedIds);
  const blockedTasks = tasks.filter(task => !orderedSet.has(task.id));
  const blockedIds = new Set(blockedTasks.map(task => task.id));
  const visited = new Set();
  const finished = [];

  for (const task of blockedTasks) {
    if (visited.has(task.id)) continue;
    visited.add(task.id);
    const stack = [[task.id, successors.get(task.id).values()]];

    while (stack.length > 0) {
      const frame = stack[stack.length - 1];
      const next = frame[1].next();
      if (!next.done) {
        const nextId = next.value;
        if (blockedIds.has(nextId) && !visited.has(nextId)) {
          visited.add(nextId);
          stack.push([nextId, successors.get(nextId).values()]);
        }
      } else {
        finished.push(frame[0]);
        stack.pop();
      }
    }
  }

  const assigned = new Set();
  const cycleIds = new Set();
  for (let index = finished.length - 1; index >= 0; index -= 1) {
    const taskId = finished[index];
    if (assigned.has(taskId)) continue;

    const component = [];
    const stack = [taskId];
    assigned.add(taskId);
    while (stack.length > 0) {
      const currentId = stack.pop();
      component.push(currentId);
      for (const predecessorId of predecessors.get(currentId)) {
        if (blockedIds.has(predecessorId) && !assigned.has(predecessorId)) {
          assigned.add(predecessorId);
          stack.push(predecessorId);
        }
      }
    }

    if (
      component.length > 1 ||
      successors.get(taskId).has(taskId)
    ) {
      for (const id of component) cycleIds.add(id);
    }
  }

  const relationships = tasks.map(task => ({
    task,
    prerequisites: [...predecessors.get(task.id)].map(id => tasksById.get(id)),
    dependents: [...successors.get(task.id)].map(id => tasksById.get(id)),
  }));

  return {
    orderedTasks: orderedIds.map(id => tasksById.get(id)),
    blockedTasks,
    cycleTasks: tasks.filter(task => cycleIds.has(task.id)),
    relationships,
    hasCycle: cycleIds.size > 0,
  };
}
