<?php

namespace Database\Seeders;

use App\Models\DailyDiary;
use App\Models\Project;
use App\Models\Task;
use App\Models\User;
use App\Models\WorkItem;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class WorkItemDemoSeeder extends Seeder
{
    public function run(): void
    {
        if (! app()->environment(['local', 'testing'])) {
            throw new \RuntimeException('Demo data is only available in local/testing environments.');
        }
        $user = User::factory()->create(['email' => 'issue15-'.fake()->uuid().'@example.test']);
        $project = Project::factory()->create(['name' => 'Dự án kiểm tra T-10', 'owner_id' => $user->id]);
        DB::table('roles')->updateOrInsert(
            ['name' => 'project_manager'],
            ['description' => 'Quản lý dự án'],
        );
        $project->members()->attach($user->id, [
            'role_id' => DB::table('roles')->where('name', 'project_manager')->value('id'),
        ]);
        $root = WorkItem::factory()->create(['name' => 'Phần móng', 'project_id' => $project->id]);
        $child = WorkItem::factory()->create(['name' => 'Cốt thép', 'project_id' => $project->id, 'parent_id' => $root->id]);
        $leaf = WorkItem::factory()->create(['name' => 'Lắp dựng', 'project_id' => $project->id, 'parent_id' => $child->id]);
        Task::factory()->create(['name' => 'Kiểm tra cốt thép', 'work_item_id' => $child->id]);
        $diary = DailyDiary::factory()->create([
            'project_id' => $project->id,
            'recorded_by' => $user->id,
            'diary_date' => now()->toDateString(),
            'workforce_count' => 10,
            'workforce_notes' => '8 thợ xây, 2 thợ điện',
            'equipment_notes' => '1 máy trộn bê tông, 2 máy cắt',
            'weather_condition' => 'sunny',
            'weather_notes' => 'Trời nắng, thi công bình thường',
        ]);
        $diary->entries()->create([
            'work_item_id' => $leaf->id,
            'recorded_by' => $user->id,
            'entry_time' => '09:00',
            'work_description' => 'Lắp dựng cốt thép phần móng và kiểm tra kích thước trước khi nghiệm thu.',
        ]);
        $this->command?->line(json_encode([
            'email' => $user->email, 'password' => 'password',
            'project' => $project->id, 'root' => $root->id, 'child' => $child->id, 'leaf' => $leaf->id,
        ], JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR));
    }
}
