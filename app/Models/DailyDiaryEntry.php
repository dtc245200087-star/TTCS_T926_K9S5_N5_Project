<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class DailyDiaryEntry extends Model
{
    use HasFactory;

    protected $fillable = [
        'daily_diary_id',
        'work_item_id',
        'recorded_by',
        'entry_time',
        'work_description',
    ];

    public function dailyDiary(): BelongsTo
    {
        return $this->belongsTo(DailyDiary::class);
    }

    public function workItem(): BelongsTo
    {
        return $this->belongsTo(WorkItem::class);
    }

    public function recordedBy(): BelongsTo
    {
        return $this->belongsTo(User::class, 'recorded_by');
    }
}
