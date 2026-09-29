<?php

namespace Database\Factories;

use App\Models\Project;
use Illuminate\Database\Eloquent\Factories\Factory;

class WorkItemFactory extends Factory
{
    public function definition(): array
    {
        return ['name' => fake()->words(3, true), 'project_id' => Project::factory(), 'parent_id' => null];
    }
}
