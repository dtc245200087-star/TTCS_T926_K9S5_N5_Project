<?php

namespace Database\Factories;

use App\Models\WorkItem;
use Illuminate\Database\Eloquent\Factories\Factory;

class TaskFactory extends Factory
{
    public function definition(): array
    {
        return [
            'name' => fake()->words(3, true),
            'work_item_id' => WorkItem::factory(),
            'duration' => fake()->numberBetween(1, 8),
        ];
    }
}
