<?php

namespace App\Services;

use Illuminate\Support\Facades\DB;

class WorkItemTree
{
    /** UNION also terminates traversal if legacy data already contains a cycle. */
    public function wouldCreateCycle(int $projectId, int $itemId, int $parentId): bool
    {
        return DB::selectOne(<<<'SQL'
            WITH RECURSIVE ancestors AS (
                SELECT id, parent_id FROM work_items WHERE id = ? AND project_id = ?
                UNION
                SELECT item.id, item.parent_id
                FROM work_items item
                INNER JOIN ancestors ON item.id = ancestors.parent_id
                WHERE item.project_id = ?
            )
            SELECT id FROM ancestors WHERE id = ?
            SQL, [$parentId, $projectId, $projectId, $itemId]) !== null;
    }
}
