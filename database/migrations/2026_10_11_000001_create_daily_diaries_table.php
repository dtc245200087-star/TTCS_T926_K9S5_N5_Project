<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('daily_diaries', function (Blueprint $table): void {
            $table->id();
            $table->foreignId('project_id')->constrained()->cascadeOnDelete();
            $table->foreignId('recorded_by')->nullable()->constrained('users')->nullOnDelete();
            $table->date('diary_date');
            $table->unsignedSmallInteger('workforce_count')->nullable();
            $table->text('workforce_notes')->nullable();
            $table->text('equipment_notes')->nullable();
            $table->string('weather_condition', 32)->nullable();
            $table->text('weather_notes')->nullable();
            $table->timestamps();

            $table->unique(['project_id', 'diary_date']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('daily_diaries');
    }
};
