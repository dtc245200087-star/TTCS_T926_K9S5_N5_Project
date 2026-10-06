<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class RoleSeeder extends Seeder
{
    public function run(): void
    {
        $roles = [
            ['name' => 'admin',           'description' => 'Quản trị hệ thống'],
            ['name' => 'project_manager', 'description' => 'Quản lý dự án'],
            ['name' => 'team_lead',       'description' => 'Trưởng nhóm'],
            ['name' => 'member',          'description' => 'Thành viên'],
            ['name' => 'viewer',          'description' => 'Chỉ xem'],
            ['name' => 'guest',           'description' => 'Khách'],
        ];

        DB::table('roles')->insert($roles);
    }
}