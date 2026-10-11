<?php

namespace Database\Factories;

use App\Models\Project;
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

class DailyDiaryFactory extends Factory
{
    public function definition(): array
    {
        return [
            'project_id' => Project::factory(),
            'recorded_by' => User::factory(),
            'diary_date' => fake()->date(),
            'workforce_count' => fake()->numberBetween(1, 30),
            'workforce_notes' => fake()->optional()->sentence(),
            'equipment_notes' => fake()->optional()->sentence(),
            'weather_condition' => fake()->randomElement(['sunny', 'cloudy', 'rainy', 'stormy', 'windy', 'other']),
            'weather_notes' => fake()->optional()->sentence(),
        ];
    }
}
