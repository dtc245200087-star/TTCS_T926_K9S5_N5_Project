<?php

use App\Http\Controllers\Api\WorkItemController;
use Illuminate\Support\Facades\Route;

Route::prefix('v1/projects/{project}/work-items')->middleware('auth.basic')->group(function (): void {
    Route::patch('{workItem}', [WorkItemController::class, 'update'])->name('work-items.update');
    Route::delete('{workItem}', [WorkItemController::class, 'destroy'])->name('work-items.destroy');
});
