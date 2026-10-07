<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Auth\LoginController;

Route::get('/login', [LoginController::class, 'showLoginForm'])->name('login');
Route::post('/login', [LoginController::class, 'login']);

Route::post('/logout', [LoginController::class, 'logout'])->middleware('auth');

Route::get('/', function () {
    return view('dashboard');
})->middleware('auth');

Route::get('/work-items', function () {
    return view('welcome');
})->middleware('auth');

Route::get('/projects', function () {
    return view('projects.index');
})->middleware('auth');

Route::get('/materials', function () {
    return view('materials.index');
})->middleware('auth');

Route::get('/personnel', function () {
    return view('personnel.index');
})->middleware('auth');

Route::get('/work-items/tree', function () {
    return view('work-items.tree');
})->middleware('auth');

Route::get('/safety', function () {
    return view('safety.index');
})->middleware('auth');

Route::get('/diaries', function () {
    return view('diaries.index');
})->middleware('auth');