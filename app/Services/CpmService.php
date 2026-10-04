<?php

namespace App\Services;

class TaskDTO
{
    public string $id;
    public int $duration;
    public array $predecessors;
    public int $es = 0; // Early Start (Khởi sớm)
    public int $ef = 0; // Early Finish (Kết thúc sớm)

    public function __construct(string $id, int $duration, array $predecessors = [])
    {
        $this->id = $id;
        $this->duration = $duration;
        $this->predecessors = $predecessors;
    }
}

class CpmService
{
    /**
     * Tính ES và EF cho các công việc (Forward Pass)
     *
     * @param array<string, TaskDTO> $tasks
     * @param array<string> $sortedIds
     * @return array<string, TaskDTO>
     */
    public function calculateForwardPass(array $tasks, array $sortedIds): array
    {
        foreach ($sortedIds as $taskId) {
            if (!isset($tasks[$taskId])) {
                continue;
            }

            $task = $tasks[$taskId];

            // 1. Nếu không có công việc đứng trước -> ES = 0
            if (empty($task->predecessors)) {
                $task->es = 0;
            } else {
                // 2. Lấy max(EF) của các công việc đứng trước
                $maxEf = 0;
                foreach ($task->predecessors as $predId) {
                    if (isset($tasks[$predId]) && $tasks[$predId]->ef > $maxEf) {
                        $maxEf = $tasks[$predId]->ef;
                    }
                }
                $task->es = $maxEf;
            }

            // 3. EF = ES + Duration
            $task->ef = $task->es + $task->duration;
        }

        return $tasks;
    }
}