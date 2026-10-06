<?php

use App\Http\Controllers\Api\TaskController;
use App\Http\Controllers\Api\WorkItemController;
use Illuminate\Support\Facades\Route;

Route::prefix('v1/projects/{project}/work-items')->middleware(['web', 'auth'])->group(function (): void {
    Route::get('', [WorkItemController::class, 'index'])->name('work-items.index');
    Route::patch('{workItem}', [WorkItemController::class, 'update'])->name('work-items.update');

    Route::post('{workItem}/tasks', [TaskController::class, 'store'])->name('tasks.store');

    Route::patch('{workItem}/tasks/{task}', [TaskController::class, 'update'])->name('tasks.update');
    Route::delete('{workItem}/tasks/{task}', [TaskController::class, 'destroy'])->name('tasks.destroy');
    Route::delete('{workItem}', [WorkItemController::class, 'destroy'])->name('work-items.destroy');
});
