<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\UpdateWorkItemRequest;
use App\Http\Resources\WorkItemResource;
use App\Models\Project;
use App\Models\WorkItem;
use App\Services\WorkItemTree;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\ValidationException;

class WorkItemController extends Controller
{
    public function index(Request $request, Project $project)
    {
        // Chỉ chủ dự án mới được xem cây hạng mục
        abort_unless(
            (int) $project->owner_id === (int) $request->user()->id,
            403
        );

        $workItems = $project->workItems()
            ->with('tasks')
            ->orderBy('parent_id')
            ->orderBy('id')
            ->get();

        return response()->json($workItems);
    }

    public function update(
        UpdateWorkItemRequest $request,
        Project $project,
        WorkItem $workItem,
        WorkItemTree $tree
    ): WorkItemResource {
        abort_unless(
            (int) $workItem->project_id === (int) $project->id,
            404
        );

        return DB::transaction(function () use (
            $request,
            $project,
            $workItem,
            $tree
        ): WorkItemResource {
            // Serialize tree mutations so concurrent reparenting cannot create a cycle.
            Project::whereKey($project->id)
                ->lockForUpdate()
                ->firstOrFail();

            $item = $project->workItems()
                ->whereKey($workItem->id)
                ->lockForUpdate()
                ->firstOrFail();

            $parentId = $request->validated('parent_id');

            if ($parentId !== null) {
                $parent = $project->workItems()->find($parentId);

                if ($parent === null) {
                    throw ValidationException::withMessages([
                        'parent_id' => "Hạng mục cha của «{$item->name}» không tồn tại trong dự án này.",
                    ]);
                }

                if (
                    $tree->wouldCreateCycle(
                        $project->id,
                        $item->id,
                        $parent->id
                    )
                ) {
                    throw ValidationException::withMessages([
                        'parent_id' => "Không thể đặt hạng mục «{$item->name}» làm con của «{$parent->name}»: hạng mục cha là chính nó hoặc hậu duệ của nó.",
                    ]);
                }
            }

            $item->update([
                'parent_id' => $parentId,
            ]);

            return new WorkItemResource($item);
        }, 3);
    }

    public function destroy(
        Request $request,
        Project $project,
        WorkItem $workItem
    ): Response {
        abort_unless(
            (int) $project->owner_id === (int) $request->user()->id,
            403
        );

        abort_unless(
            (int) $workItem->project_id === (int) $project->id,
            404
        );

        return DB::transaction(function () use (
            $project,
            $workItem
        ): Response {
            Project::whereKey($project->id)
                ->lockForUpdate()
                ->firstOrFail();

            $item = $project->workItems()
                ->whereKey($workItem->id)
                ->lockForUpdate()
                ->firstOrFail();

            abort_if(
                $item->tasks()->count() > 0,
                409,
                "Không thể xoá hạng mục «{$item->name}» vì đã có công việc."
            );

            abort_if(
                $item->children()->exists(),
                409,
                "Không thể xoá hạng mục «{$item->name}» vì còn hạng mục con."
            );

            $item->delete();

            return response()->noContent();
        }, 3);
    }
}
