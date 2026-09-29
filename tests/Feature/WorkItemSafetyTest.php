<?php

namespace Tests\Feature;

use App\Models\Project;
use App\Models\Task;
use App\Models\User;
use App\Models\WorkItem;
use Illuminate\Foundation\Testing\LazilyRefreshDatabase;
use PHPUnit\Framework\Attributes\TestWith;
use Tests\TestCase;

class WorkItemSafetyTest extends TestCase
{
    use LazilyRefreshDatabase;

    #[TestWith([0])]
    #[TestWith([1])]
    #[TestWith([4])]
    public function test_reparenting_to_self_or_a_descendant_returns_422(int $depth): void
    {
        $project = $this->ownedProject();
        $root = WorkItem::factory()->create(['project_id' => $project->id, 'name' => 'Phần móng']);
        $descendant = $root;
        for ($i = 0; $i < $depth; $i++) {
            $descendant = WorkItem::factory()->create(['project_id' => $project->id, 'parent_id' => $descendant->id, 'name' => 'Cốt thép']);
        }

        $response = $this->patchJson($this->url($root), ['parent_id' => $descendant->id]);

        $response->assertUnprocessable()->assertJsonValidationErrors('parent_id')
            ->assertJsonPath('errors.parent_id.0', "Không thể đặt hạng mục «{$root->name}» làm con của «{$descendant->name}»: hạng mục cha là chính nó hoặc hậu duệ của nó.");
        $this->assertDatabaseHas('work_items', ['id' => $root->id, 'parent_id' => null]);
        $this->assertDatabaseCount('work_items', $depth + 1);
    }

    public function test_a_task_blocks_deletion_with_409_and_preserves_both_records(): void
    {
        $project = $this->ownedProject();
        $item = WorkItem::factory()->create(['project_id' => $project->id, 'name' => 'Phần móng']);
        $task = Task::factory()->create(['work_item_id' => $item->id]);

        $response = $this->deleteJson($this->url($item));

        $response->assertConflict()->assertJsonPath('message', 'Không thể xoá hạng mục «Phần móng» vì đã có công việc.');
        $this->assertModelExists($item);
        $this->assertModelExists($task);
    }

    public function test_an_empty_leaf_can_be_deleted(): void
    {
        $project = $this->ownedProject();
        $item = WorkItem::factory()->create(['project_id' => $project->id]);
        $other = WorkItem::factory()->create(['project_id' => $project->id]);
        $task = Task::factory()->create(['work_item_id' => $other->id]);

        $this->deleteJson($this->url($item))->assertNoContent();

        $this->assertModelMissing($item);
        $this->assertModelExists($other);
        $this->assertModelExists($task);
    }

    public function test_deleting_a_parent_returns_409_without_orphaning_children(): void
    {
        $project = $this->ownedProject();
        $parent = WorkItem::factory()->create(['project_id' => $project->id, 'name' => 'Phần thân']);
        $child = WorkItem::factory()->create(['project_id' => $project->id, 'parent_id' => $parent->id]);

        $this->deleteJson($this->url($parent))->assertConflict()
            ->assertJsonPath('message', 'Không thể xoá hạng mục «Phần thân» vì còn hạng mục con.');

        $this->assertModelExists($parent);
        $this->assertDatabaseHas('work_items', ['id' => $child->id, 'parent_id' => $parent->id]);
    }

    public function test_a_valid_move_is_persisted_and_unexpected_attributes_are_ignored(): void
    {
        $project = $this->ownedProject();
        $item = WorkItem::factory()->create(['project_id' => $project->id, 'name' => 'Phần móng']);
        $parent = WorkItem::factory()->create(['project_id' => $project->id]);

        $this->patchJson($this->url($item), ['parent_id' => $parent->id, 'name' => 'Injected', 'project_id' => 99999])
            ->assertOk()->assertJsonPath('data.parent_id', $parent->id);

        $this->assertDatabaseHas('work_items', ['id' => $item->id, 'parent_id' => $parent->id, 'name' => 'Phần móng', 'project_id' => $project->id]);
    }

    public function test_a_child_can_be_moved_to_the_root(): void
    {
        $project = $this->ownedProject();
        $parent = WorkItem::factory()->create(['project_id' => $project->id]);
        $child = WorkItem::factory()->create(['project_id' => $project->id, 'parent_id' => $parent->id]);

        $this->patchJson($this->url($child), ['parent_id' => null])->assertOk()->assertJsonPath('data.parent_id', null);

        $this->assertDatabaseHas('work_items', ['id' => $child->id, 'parent_id' => null]);
    }

    public function test_keeping_the_current_parent_is_allowed(): void
    {
        $project = $this->ownedProject();
        $parent = WorkItem::factory()->create(['project_id' => $project->id]);
        $child = WorkItem::factory()->create(['project_id' => $project->id, 'parent_id' => $parent->id]);

        $this->patchJson($this->url($child), ['parent_id' => $parent->id])->assertOk();

        $this->assertDatabaseHas('work_items', ['id' => $child->id, 'parent_id' => $parent->id]);
    }

    #[TestWith([false])]
    #[TestWith([true])]
    public function test_a_missing_or_foreign_parent_returns_422(bool $foreign): void
    {
        $project = $this->ownedProject();
        $item = WorkItem::factory()->create(['project_id' => $project->id, 'name' => 'Phần móng']);
        $parentId = $foreign ? WorkItem::factory()->create()->id : 99999;

        $this->patchJson($this->url($item), ['parent_id' => $parentId])->assertUnprocessable()
            ->assertJsonPath('errors.parent_id.0', 'Hạng mục cha của «Phần móng» không tồn tại trong dự án này.');

        $this->assertDatabaseHas('work_items', ['id' => $item->id, 'parent_id' => null]);
    }

    #[TestWith([[], 'Vui lòng chọn cha cho hạng mục «Phần móng» hoặc để trống để chuyển thành hạng mục gốc.'])]
    #[TestWith([['parent_id' => 'invalid'], 'Hạng mục cha của «Phần móng» không hợp lệ.'])]
    #[TestWith([['parent_id' => 0], 'Hạng mục cha của «Phần móng» không hợp lệ.'])]
    public function test_invalid_input_returns_422(array $payload, string $message): void
    {
        $project = $this->ownedProject();
        $item = WorkItem::factory()->create(['project_id' => $project->id, 'name' => 'Phần móng']);

        $this->patchJson($this->url($item), $payload)->assertUnprocessable()->assertJsonPath('errors.parent_id.0', $message);

        $this->assertDatabaseHas('work_items', ['id' => $item->id, 'parent_id' => null]);
    }

    #[TestWith(['PATCH'])]
    #[TestWith(['DELETE'])]
    public function test_guests_receive_401(string $method): void
    {
        $item = WorkItem::factory()->create();

        $this->json($method, $this->url($item), ['parent_id' => null])->assertUnauthorized();

        $this->assertModelExists($item);
    }

    #[TestWith(['PATCH'])]
    #[TestWith(['DELETE'])]
    public function test_non_owners_receive_403(string $method): void
    {
        $item = WorkItem::factory()->create();
        $this->actingAs(User::factory()->create());

        $this->json($method, $this->url($item), ['parent_id' => null])->assertForbidden();

        $this->assertModelExists($item);
    }

    #[TestWith(['PATCH'])]
    #[TestWith(['DELETE'])]
    public function test_a_work_item_from_another_project_returns_404(string $method): void
    {
        $project = $this->ownedProject();
        $item = WorkItem::factory()->create();

        $this->json($method, "/api/v1/projects/{$project->id}/work-items/{$item->id}", ['parent_id' => null])->assertNotFound();

        $this->assertModelExists($item);
    }

    public function test_http_basic_credentials_can_authenticate_an_api_request(): void
    {
        $user = User::factory()->create();
        $project = Project::factory()->create(['owner_id' => $user->id]);
        $item = WorkItem::factory()->create(['project_id' => $project->id]);

        $this->withServerVariables(['PHP_AUTH_USER' => $user->email, 'PHP_AUTH_PW' => 'password'])
            ->deleteJson($this->url($item))->assertNoContent();

        $this->assertModelMissing($item);
    }

    private function ownedProject(): Project
    {
        $user = User::factory()->create();
        $this->actingAs($user);

        return Project::factory()->create(['owner_id' => $user->id]);
    }

    private function url(WorkItem $item): string
    {
        return "/api/v1/projects/{$item->project_id}/work-items/{$item->id}";
    }
}
