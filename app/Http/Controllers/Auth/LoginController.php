<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Auth;

class LoginController extends Controller
{
    public function showLoginForm()
    {
        return view('auth.login');
    }

    public function login(Request $request)
    {
        $request->validate([
            'email' => 'required|email',
            'password' => 'required',
        ]);

        $user = User::where('email', $request->email)->first();

        // Kiểm tra tài khoản đang bị khóa
        if ($user && $user->locked_until && now()->lt($user->locked_until)) {
    $minutes = (int) ceil(now()->diffInSeconds($user->locked_until) / 60);

    return back()->withErrors([
        'email' => "Tài khoản đang bị khóa. Vui lòng thử lại sau {$minutes} phút.",
    ])->withInput();
     }
        // Nếu hết thời gian khóa thì reset
        if ($user && $user->locked_until && now()->gte($user->locked_until)) {
            $user->failed_attempts = 0;
            $user->locked_until = null;
            $user->save();
        }

        // Kiểm tra mật khẩu
        if (!$user || !Hash::check($request->password, $user->password)) {

            if ($user) {
                $user->failed_attempts++;

                // Sai lần thứ 5 → khóa 15 phút
                if ($user->failed_attempts >= 5) {
                    $user->locked_until = now()->addMinutes(15);
                }

                $user->save();
            }

            return back()->withErrors([
                'email' => 'Email hoặc mật khẩu không đúng.',
            ])->withInput();
        }

        // Đăng nhập thành công → reset số lần sai
        $user->failed_attempts = 0;
        $user->locked_until = null;
        $user->save();

        Auth::login($user);
        $request->session()->regenerate();

        return redirect('/');
    }

    public function logout(Request $request)
    {
        Auth::logout();

        $request->session()->invalidate();
        $request->session()->regenerateToken();

        return redirect('/login');
    }
}