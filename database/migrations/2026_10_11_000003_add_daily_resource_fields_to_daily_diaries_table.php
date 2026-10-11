<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('daily_diaries', function (Blueprint $table): void {
            $table->unsignedSmallInteger('workforce_count')->nullable();
            $table->text('workforce_notes')->nullable();
            $table->text('equipment_notes')->nullable();
            $table->string('weather_condition', 32)->nullable();
            $table->text('weather_notes')->nullable();
        });
    }

    public function down(): void
    {
        Schema::table('daily_diaries', function (Blueprint $table): void {
            $table->dropColumn([
                'workforce_count',
                'workforce_notes',
                'equipment_notes',
                'weather_condition',
                'weather_notes',
            ]);
        });
    }
};
