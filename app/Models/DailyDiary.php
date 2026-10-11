<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class DailyDiary extends Model
{
    use HasFactory;

    protected $fillable = [
        'project_id',
        'recorded_by',
        'diary_date',
        'workforce_count',
        'workforce_notes',
        'equipment_notes',
        'weather_condition',
        'weather_notes',
    ];

    protected function casts(): array
    {
        return [
            'diary_date' => 'date',
            'workforce_count' => 'integer',
        ];
    }

    public function project(): BelongsTo
    {
        return $this->belongsTo(Project::class);
    }

    public function recordedBy(): BelongsTo
    {
        return $this->belongsTo(User::class, 'recorded_by');
    }

    public function entries(): HasMany
    {
        return $this->hasMany(DailyDiaryEntry::class);
    }
}
