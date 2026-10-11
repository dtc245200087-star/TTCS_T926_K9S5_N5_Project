<?php

namespace Database\Factories;

use App\Models\DailyDiary;
use App\Models\User;
use App\Models\WorkItem;
use Illuminate\Database\Eloquent\Factories\Factory;

class DailyDiaryEntryFactory extends Factory
{
    public function definition(): array
    {
        return [
            'daily_diary_id' => DailyDiary::factory(),
            'work_item_id' => WorkItem::factory(),
            'recorded_by' => User::factory(),
            'entry_time' => fake()->time('H:i'),
            'work_description' => fake()->paragraph(),
        ];
    }
}
