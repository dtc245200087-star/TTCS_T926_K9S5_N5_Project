<?php

namespace App\Http\Middleware;

use App\Models\Project;
use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Symfony\Component\HttpFoundation\Response;

class EnsureProjectMember
{
    /**
     * Handle an incoming request.
     *
     * @param  Closure(Request): (Response)  $next
     */
    public function handle(Request $request, Closure $next, string ...$roles): Response
    {
        $allowedRoles = array_values(array_filter(array_map(
            fn (string $role): string => trim($role),
            $roles,
        )));

        abort_if($allowedRoles === [], 403);

        $project = $request->route('project');
        $user = $request->user();

        abort_unless($project instanceof Project && $user !== null, 403);

        $hasAllowedRole = DB::table('project_members')
            ->join('roles', 'roles.id', '=', 'project_members.role_id')
            ->where('project_members.project_id', $project->getKey())
            ->where('project_members.user_id', $user->getAuthIdentifier())
            ->whereIn('roles.name', $allowedRoles)
            ->exists();

        abort_unless($hasAllowedRole, 403);

        return $next($request);
    }
}
