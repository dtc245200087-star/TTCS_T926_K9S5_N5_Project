<?php

namespace Tests\Feature;

use App\Models\Project;
use App\Models\User;
use App\Models\WorkItem;
use Illuminate\Database\QueryException;
use Illuminate\Foundation\Testing\LazilyRefreshDatabase;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Schema;
use Tests\TestCase;

class ProjectAccessTest extends TestCase
{
    use LazilyRefreshDatabase;

    public function test_a_project_member_with_an_allowed_role_can_reach_the_handler(): void
    {
        $user = User::factory()->create();
        $project = Project::factory()->create(['owner_id' => $user->id]);
        $item = WorkItem::factory()->create(['project_id' => $project->id]);
        $this->addProjectMember($project, $user, 'team_lead');

        $this->actingAs($user)
            ->patchJson($this->url($item), ['parent_id' => null])
            ->assertOk();
    }

    public function test_a_user_who_is_not_a_project_member_receives_403(): void
    {
        $user = User::factory()->create();
        $project = Project::factory()->create();
        $item = WorkItem::factory()->create(['project_id' => $project->id]);

        $this->actingAs($user)
            ->patchJson($this->url($item), ['parent_id' => null])
            ->assertForbidden();
    }

    public function test_a_member_without_an_allowed_role_receives_403(): void
    {
        $user = User::factory()->create();
        $project = Project::factory()->create(['owner_id' => $user->id]);
        $item = WorkItem::factory()->create(['project_id' => $project->id]);
        $this->addProjectMember($project, $user, 'viewer');

        $this->actingAs($user)
            ->deleteJson($this->url($item))
            ->assertForbidden();

        $this->assertModelExists($item);
    }

    public function test_a_route_without_declared_roles_is_denied_by_default(): void
    {
        Route::get('/api/project-access-probe', fn (): array => ['ok' => true])
            ->middleware(['auth', 'project.member']);

        $this->actingAs(User::factory()->create())
            ->getJson('/api/project-access-probe')
            ->assertForbidden();
    }

    public function test_each_user_can_have_only_one_membership_per_project(): void
    {
        $user = User::factory()->create();
        $project = Project::factory()->create();
        $roleId = $this->roleId('member');

        DB::table('project_members')->insert([
            'project_id' => $project->id,
            'user_id' => $user->id,
            'role_id' => $roleId,
        ]);

        try {
            DB::table('project_members')->insert([
                'project_id' => $project->id,
                'user_id' => $user->id,
                'role_id' => $roleId,
            ]);
            $this->fail('A duplicate project membership was accepted.');
        } catch (QueryException) {
            $this->assertDatabaseCount('project_members', 1);
        }
    }

    public function test_project_members_has_a_dedicated_project_index(): void
    {
        $hasProjectIndex = collect(Schema::getIndexes('project_members'))
            ->contains(fn (array $index): bool => $index['columns'] === ['project_id']);

        $this->assertTrue($hasProjectIndex);
    }

    private function addProjectMember(Project $project, User $user, string $role): void
    {
        $project->members()->attach($user->id, ['role_id' => $this->roleId($role)]);
    }

    private function roleId(string $role): int
    {
        DB::table('roles')->insertOrIgnore([
            'name' => $role,
            'description' => $role,
        ]);

        return (int) DB::table('roles')->where('name', $role)->value('id');
    }

    private function url(WorkItem $item): string
    {
        return "/api/v1/projects/{$item->project_id}/work-items/{$item->id}";
    }
}
