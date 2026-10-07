```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Đăng nhập | SITEPRO BUILD</title>

    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: 'Inter', Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 25px;

           background:
                  linear-gradient(
        135deg,
        rgba(15, 23, 42, 0.88),
        rgba(30, 41, 59, 0.72)
      ),
       url('{{ asset('images/construction-bg.jpg') }}');

            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }

        .login-container {
            width: 100%;
            max-width: 430px;
        }

        .brand {
            text-align: center;
            margin-bottom: 22px;
        }

        .logo {
            width: 70px;
            height: 70px;
            margin: 0 auto 12px;

            display: flex;
            justify-content: center;
            align-items: center;

            border-radius: 18px;

            background: linear-gradient(135deg, #fbbf24, #ea580c);

            color: #0f172a;
            font-size: 32px;
            font-weight: 800;

            box-shadow: 0 10px 30px rgba(245, 158, 11, 0.35);

            border: 2px solid rgba(255, 255, 255, 0.25);
        }

        .brand h1 {
            margin: 0;
            color: white;
            font-size: 27px;
            font-weight: 800;
            letter-spacing: 1px;
        }

        .brand h1 span {
            color: #f59e0b;
        }

        .brand p {
            margin: 7px 0 0;
            color: #cbd5e1;
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.8px;
        }

        .login-box {
            width: 100%;
            padding: 31px;

            background: rgba(15, 23, 42, 0.78);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);

            border: 1px solid rgba(255, 255, 255, 0.14);
            border-radius: 20px;

            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.4);
        }

        .login-title {
            margin-bottom: 23px;
        }

        .login-title h2 {
            margin: 0 0 6px;
            color: white;
            font-size: 22px;
        }

        .login-title p {
            margin: 0;
            color: #94a3b8;
            font-size: 13px;
        }

        .error {
            display: flex;
            align-items: flex-start;
            gap: 10px;

            padding: 13px 14px;
            margin-bottom: 20px;

            border-radius: 12px;

            background: rgba(244, 63, 94, 0.12);
            border: 1px solid rgba(244, 63, 94, 0.35);

            color: #fda4af;
            font-size: 13px;
            line-height: 1.5;
        }

        .error-icon {
            font-size: 16px;
            margin-top: 1px;
        }

        .form-group {
            margin-bottom: 18px;
        }

        label {
            display: block;
            margin-bottom: 8px;

            color: #cbd5e1;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.7px;
        }

        .input-wrapper {
            position: relative;
        }

        .input-icon {
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);

            color: #94a3b8;
            font-size: 14px;
            z-index: 2;
        }

        input {
            width: 100%;
            padding: 13px 45px 13px 42px;

            border: 1px solid rgba(255, 255, 255, 0.14);
            border-radius: 11px;

            background: rgba(255, 255, 255, 0.07);

            color: white;
            font-size: 14px;

            outline: none;
            transition: all 0.25s ease;
        }

        input::placeholder {
            color: #64748b;
        }

        input:focus {
            background: rgba(255, 255, 255, 0.1);
            border-color: #f59e0b;

            box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.12);
        }

        .password-toggle {
            position: absolute;
            right: 13px;
            top: 50%;
            transform: translateY(-50%);

            width: auto;
            margin: 0;
            padding: 3px;

            background: transparent;
            color: #94a3b8;

            border: none;
            box-shadow: none;

            cursor: pointer;
            font-size: 15px;
        }

        .password-toggle:hover {
            background: transparent;
            color: #fbbf24;
            transform: translateY(-50%);
            box-shadow: none;
        }

        .form-options {
            display: flex;
            justify-content: flex-end;
            margin-top: -5px;
            margin-bottom: 20px;
        }

        .forgot-link {
            color: #fbbf24;
            text-decoration: none;
            font-size: 12px;
            font-weight: 600;
        }

        .forgot-link:hover {
            color: #fcd34d;
            text-decoration: underline;
        }

        .login-button {
            width: 100%;
            padding: 14px;

            margin-top: 3px;

            border: none;
            border-radius: 11px;

            background: linear-gradient(135deg, #f59e0b, #ea580c);

            color: #0f172a;
            font-size: 14px;
            font-weight: 800;
            letter-spacing: 0.5px;

            cursor: pointer;
            transition: all 0.25s ease;

            box-shadow: 0 8px 20px rgba(234, 88, 12, 0.25);
        }

        .login-button:hover {
            transform: translateY(-1px);

            background: linear-gradient(135deg, #fbbf24, #f97316);

            box-shadow: 0 12px 25px rgba(234, 88, 12, 0.35);
        }

        .login-button:active {
            transform: translateY(0);
        }

        .register {
            text-align: center;
            margin-top: 20px;
            padding-top: 18px;

            border-top: 1px solid rgba(255, 255, 255, 0.1);

            color: #94a3b8;
            font-size: 12px;
        }

        .register a {
            color: #fbbf24;
            font-weight: 700;
            text-decoration: none;
        }

        .register a:hover {
            text-decoration: underline;
        }

        .security {
            display: flex;
            justify-content: space-between;
            align-items: center;

            margin-top: 17px;
            padding-top: 16px;

            border-top: 1px solid rgba(255, 255, 255, 0.08);

            color: #94a3b8;
            font-size: 10px;
        }

        .status {
            display: flex;
            align-items: center;
            gap: 7px;
        }

        .status-dot {
            width: 7px;
            height: 7px;

            border-radius: 50%;
            background: #22c55e;

            box-shadow: 0 0 8px rgba(34, 197, 94, 0.7);
        }

        .security strong {
            color: #e2e8f0;
        }

        .copyright {
            text-align: center;
            margin-top: 16px;

            color: #cbd5e1;
            font-size: 10px;
        }

        @media (max-width: 480px) {
            body {
                padding: 18px;
            }

            .login-box {
                padding: 25px 21px;
            }

            .brand h1 {
                font-size: 24px;
            }

            .logo {
                width: 64px;
                height: 64px;
                font-size: 28px;
            }
        }
    </style>
</head>

<body>

<div class="login-container">

    <div class="brand">
        <div class="logo">🏗</div>

        <h1>
            SITE<span>PRO</span> BUILD
        </h1>

        <p>
            HỆ THỐNG QUẢN LÝ THI CÔNG CÔNG TRÌNH
        </p>
    </div>

    <div class="login-box">

        <div class="login-title">
            <h2>Đăng nhập hệ thống</h2>
            <p>Nhập thông tin tài khoản để tiếp tục</p>
        </div>

        @if ($errors->any())
            <div class="error">
                <div class="error-icon">⚠</div>
                <div>{{ $errors->first() }}</div>
            </div>
        @endif

        <form method="POST" action="/login">
            @csrf

            <div class="form-group">
                <label for="email">Email</label>

                <div class="input-wrapper">
                    <span class="input-icon">✉</span>

                    <input
                        type="email"
                        id="email"
                        name="email"
                        value="{{ old('email') }}"
                        placeholder="Nhập email của bạn"
                        required
                        autocomplete="email"
                    >
                </div>
            </div>

            <div class="form-group">
                <label for="password">Mật khẩu</label>

                <div class="input-wrapper">
                    <span class="input-icon">🔒</span>

                    <input
                        type="password"
                        id="password"
                        name="password"
                        placeholder="Nhập mật khẩu"
                        required
                        autocomplete="current-password"
                    >

                    <button
                        type="button"
                        class="password-toggle"
                        onclick="togglePassword()"
                        aria-label="Hiện hoặc ẩn mật khẩu"
                    >
                        👁
                    </button>
                </div>
            </div>

            <div class="form-options">
                <a href="#" class="forgot-link">
                    Quên mật khẩu?
                </a>
            </div>

            <button type="submit" class="login-button">
                ĐĂNG NHẬP HỆ THỐNG
            </button>

        </form>

        <div class="register">
            Chưa có tài khoản?
            <a href="#">
                Đăng ký tài khoản
            </a>
        </div>

        <div class="security">

            <div class="status">
                <span class="status-dot"></span>
                <span>Hệ thống: <strong>Hoạt động</strong></span>
            </div>

            <div>
                🔐 Bảo mật
            </div>

        </div>

    </div>

    <div class="copyright">
        © 2026 Construction Site Management System
    </div>

</div>

<script>
    function togglePassword() {
        const password = document.getElementById('password');
        const toggle = document.querySelector('.password-toggle');

        if (password.type === 'password') {
            password.type = 'text';
            toggle.textContent = '🙈';
        } else {
            password.type = 'password';
            toggle.textContent = '👁';
        }
    }
</script>

</body>
</html>
```
