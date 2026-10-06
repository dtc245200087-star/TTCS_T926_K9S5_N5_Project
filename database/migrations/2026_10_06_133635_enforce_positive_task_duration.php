<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        DB::unprepared(<<<'SQL'
            CREATE TRIGGER tasks_duration_positive_insert
            BEFORE INSERT ON tasks
            FOR EACH ROW
            WHEN NEW.duration <= 0 OR typeof(NEW.duration) != 'integer'
            BEGIN
                SELECT RAISE(ABORT, 'tasks.duration must be a positive integer');
            END;
        SQL);

        DB::unprepared(<<<'SQL'
            CREATE TRIGGER tasks_duration_positive_update
            BEFORE UPDATE OF duration ON tasks
            FOR EACH ROW
            WHEN NEW.duration <= 0 OR typeof(NEW.duration) != 'integer'
            BEGIN
                SELECT RAISE(ABORT, 'tasks.duration must be a positive integer');
            END;
        SQL);
    }

    public function down(): void
    {
        DB::unprepared('DROP TRIGGER IF EXISTS tasks_duration_positive_insert');
        DB::unprepared('DROP TRIGGER IF EXISTS tasks_duration_positive_update');
    }
};