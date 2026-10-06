<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Project;
use App\Models\Task;
use App\Models\WorkItem;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class TaskController extends Controller
{
    public function store(Request $request, Project $project, WorkItem $workItem): JsonResponse
    {
        // Chỉ chủ dự án mới được thêm công việc
        abort_unless(
            (int) $project->owner_id === (int) $request->user()->id,
            403
        );

        // Kiểm tra hạng mục thuộc đúng dự án
        abort_unless(
            (int) $workItem->project_id === (int) $project->id,
            404
        );

        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'duration' => 'required|integer|min:1',
        ]);

        // Không cho thêm công việc vào hạng mục còn hạng mục con
        abort_if(
            $workItem->children()->exists(),
            422,
            'Không thể thêm công việc vào hạng mục còn có hạng mục con.'
        );

        $task = $workItem->tasks()->create($validated);

        return response()->json($task, 201);
    }

    public function update(
        Request $request,
        Project $project,
        WorkItem $workItem,
        Task $task
    ): JsonResponse {
        // Chỉ chủ dự án mới được sửa công việc
        abort_unless(
            (int) $project->owner_id === (int) $request->user()->id,
            403
        );

        // Kiểm tra hạng mục thuộc đúng dự án
        abort_unless(
            (int) $workItem->project_id === (int) $project->id,
            404
        );

        // Kiểm tra task thuộc đúng hạng mục
        abort_unless(
            (int) $task->work_item_id === (int) $workItem->id,
            404
        );

        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'duration' => 'required|integer|min:1',
        ]);

        $task->update($validated);

        return response()->json($task);
    }

    public function destroy(
        Request $request,
        Project $project,
        WorkItem $workItem,
        Task $task
    ): JsonResponse {
        // Chỉ chủ dự án mới được xóa công việc
        abort_unless(
            (int) $project->owner_id === (int) $request->user()->id,
            403
        );

        // Kiểm tra hạng mục thuộc đúng dự án
        abort_unless(
            (int) $workItem->project_id === (int) $project->id,
            404
        );

        // Kiểm tra task thuộc đúng hạng mục
        abort_unless(
            (int) $task->work_item_id === (int) $workItem->id,
            404
        );

        $task->delete();

        return response()->json([
            'message' => 'Xóa công việc thành công.'
        ]);
    }
}