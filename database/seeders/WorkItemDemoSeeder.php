<?php

namespace Database\Seeders;

use App\Models\Project;
use App\Models\Task;
use App\Models\User;
use App\Models\WorkItem;
use Illuminate\Database\Seeder;

class WorkItemDemoSeeder extends Seeder
{
    public function run(): void
    {
        if (! app()->environment(['local', 'testing'])) {
            throw new \RuntimeException('Demo data is only available in local/testing environments.');
        }
        $user = User::factory()->create(['email' => 'issue15-'.fake()->uuid().'@example.test']);
        $project = Project::factory()->create(['name' => 'Dự án kiểm tra T-10', 'owner_id' => $user->id]);
        $root = WorkItem::factory()->create(['name' => 'Phần móng', 'project_id' => $project->id]);
        $child = WorkItem::factory()->create(['name' => 'Cốt thép', 'project_id' => $project->id, 'parent_id' => $root->id]);
        $leaf = WorkItem::factory()->create(['name' => 'Lắp dựng', 'project_id' => $project->id, 'parent_id' => $child->id]);
        Task::factory()->create(['name' => 'Kiểm tra cốt thép', 'work_item_id' => $child->id]);
        $this->command?->line(json_encode([
            'email' => $user->email, 'password' => 'password',
            'project' => $project->id, 'root' => $root->id, 'child' => $child->id, 'leaf' => $leaf->id,
        ], JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR));
    }
}
