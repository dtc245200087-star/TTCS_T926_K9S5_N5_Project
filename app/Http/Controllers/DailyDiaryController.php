<?php

namespace App\Http\Controllers;

use App\Models\DailyDiary;
use App\Models\Project;
use App\Models\User;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Query\Builder as QueryBuilder;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\Rule;
use Illuminate\View\View;

class DailyDiaryController extends Controller
{
    public function index(Request $request): View
    {
        $user = $request->user();
        abort_unless($user instanceof User, 401);

        $filters = $request->validate([
            'project' => ['nullable', 'integer'],
            'date' => ['nullable', 'date_format:Y-m-d'],
            'work_item' => ['nullable', 'integer'],
        ]);

        $projects = $this->accessibleProjects($user)
            ->orderBy('name')
            ->get();

        $selectedProject = isset($filters['project'])
            ? $projects->firstWhere('id', (int) $filters['project'])
            : $projects->first();

        if (isset($filters['project'])) {
            abort_unless($selectedProject instanceof Project, 404);
        }

        $selectedDate = $filters['date'] ?? now()->toDateString();
        $workItems = $selectedProject?->workItems()
            ->orderBy('name')
            ->get() ?? collect();

        $selectedWorkItemId = isset($filters['work_item'])
            ? (int) $filters['work_item']
            : null;

        if ($selectedWorkItemId !== null) {
            abort_unless(
                $workItems->contains('id', $selectedWorkItemId),
                404
            );
        }

        $dailyDiary = $selectedProject?->dailyDiaries()
            ->where('diary_date', $selectedDate)
            ->with('recordedBy')
            ->first();

        $entries = $dailyDiary?->entries()
            ->with(['workItem', 'recordedBy'])
            ->when(
                $selectedWorkItemId !== null,
                fn (Builder $query): Builder => $query->where('work_item_id', $selectedWorkItemId),
            )
            ->orderBy('entry_time')
            ->orderBy('id')
            ->get() ?? collect();

        return view('diaries.index', [
            'projects' => $projects,
            'selectedProject' => $selectedProject,
            'selectedDate' => $selectedDate,
            'workItems' => $workItems,
            'selectedWorkItemId' => $selectedWorkItemId,
            'dailyDiary' => $dailyDiary,
            'entries' => $entries,
            'weatherLabels' => [
                'sunny' => 'Nắng',
                'cloudy' => 'Nhiều mây',
                'rainy' => 'Mưa',
                'stormy' => 'Mưa dông',
                'windy' => 'Gió lớn',
                'other' => 'Khác',
            ],
        ]);
    }

    public function storeEntry(Request $request): RedirectResponse
    {
        $validated = $request->validate([
            'project_id' => ['required', 'integer', 'exists:projects,id'],
            'diary_date' => ['required', 'date_format:Y-m-d'],
            'work_item_id' => [
                'required',
                'integer',
                Rule::exists('work_items', 'id')->where(
                    fn (QueryBuilder $query): QueryBuilder => $query->where('project_id', $request->input('project_id')),
                ),
            ],
            'entry_time' => ['required', 'date_format:H:i'],
            'work_description' => ['required', 'string', 'max:5000'],
        ], [
            'work_item_id.required' => 'Mỗi mục nhật ký phải gắn với một hạng mục.',
            'work_item_id.exists' => 'Hạng mục không thuộc dự án đã chọn.',
        ]);

        $user = $request->user();
        abort_unless($user instanceof User, 401);

        $project = $this->accessibleProjects($user)
            ->whereKey($validated['project_id'])
            ->firstOrFail();

        DB::transaction(function () use ($validated, $project, $user): void {
            $dailyDiary = DailyDiary::query()->firstOrCreate(
                [
                    'project_id' => $project->id,
                    'diary_date' => $validated['diary_date'],
                ],
                [
                    'recorded_by' => $user->id,
                ],
            );

            $dailyDiary->entries()->create([
                'work_item_id' => $validated['work_item_id'],
                'recorded_by' => $user->id,
                'entry_time' => $validated['entry_time'],
                'work_description' => $validated['work_description'],
            ]);
        });

        return redirect()->route('diaries.index', [
            'project' => $project->id,
            'date' => $validated['diary_date'],
        ])->with('status', 'Đã thêm mục nhật ký vào ngày đã chọn.');
    }

    public function updateDailySummary(Request $request): RedirectResponse
    {
        $validated = $request->validate([
            'project_id' => ['required', 'integer', 'exists:projects,id'],
            'diary_date' => ['required', 'date_format:Y-m-d'],
            'workforce_count' => ['nullable', 'integer', 'min:0', 'max:10000'],
            'workforce_notes' => ['nullable', 'string', 'max:4000'],
            'equipment_notes' => ['nullable', 'string', 'max:4000'],
            'weather_condition' => [
                'nullable',
                Rule::in(['sunny', 'cloudy', 'rainy', 'stormy', 'windy', 'other']),
            ],
            'weather_notes' => ['nullable', 'string', 'max:4000'],
        ]);

        $user = $request->user();
        abort_unless($user instanceof User, 401);

        $project = $this->accessibleProjects($user)
            ->whereKey($validated['project_id'])
            ->firstOrFail();

        DB::transaction(function () use ($validated, $project, $user): void {
            $dailyDiary = DailyDiary::query()->firstOrNew([
                'project_id' => $project->id,
                'diary_date' => $validated['diary_date'],
            ]);

            if (! $dailyDiary->exists) {
                $dailyDiary->recorded_by = $user->id;
            }

            $dailyDiary->fill([
                'workforce_count' => $validated['workforce_count'] ?? null,
                'workforce_notes' => $validated['workforce_notes'] ?? null,
                'equipment_notes' => $validated['equipment_notes'] ?? null,
                'weather_condition' => $validated['weather_condition'] ?? null,
                'weather_notes' => $validated['weather_notes'] ?? null,
            ]);
            $dailyDiary->save();
        });

        return redirect()->route('diaries.index', [
            'project' => $project->id,
            'date' => $validated['diary_date'],
        ])->with('status', 'Đã lưu nhân lực, thiết bị và thời tiết trong ngày.');
    }

    /**
     * @return Builder<Project>
     */
    private function accessibleProjects(User $user): Builder
    {
        return Project::query()
            ->where('owner_id', $user->id)
            ->orWhereHas('members', fn (Builder $query): Builder => $query->where('users.id', $user->id));
    }
}
