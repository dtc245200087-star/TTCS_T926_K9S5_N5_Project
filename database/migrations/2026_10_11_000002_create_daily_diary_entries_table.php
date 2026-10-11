<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('daily_diary_entries', function (Blueprint $table): void {
            $table->id();
            $table->foreignId('daily_diary_id')->constrained()->cascadeOnDelete();
            $table->foreignId('work_item_id')->constrained()->restrictOnDelete();
            $table->foreignId('recorded_by')->nullable()->constrained('users')->nullOnDelete();
            $table->time('entry_time');
            $table->text('work_description');
            $table->timestamps();

            $table->index(['daily_diary_id', 'entry_time']);
            $table->index('work_item_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('daily_diary_entries');
    }
};
