<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Đăng nhập</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            min-height: 100vh;

            display: flex;
            justify-content: center;
            align-items: center;

            background: linear-gradient(
                135deg,
                #eaf2ff,
                #f3edff
            );
        }

        .login-box {
            width: 400px;
            background: #ffffff;
            padding: 40px;

            border-radius: 18px;

            box-shadow:
                0 10px 30px rgba(120, 130, 160, 0.15);
        }

        .logo {
            width: 65px;
            height: 65px;
            margin: 0 auto 15px;

            display: flex;
            justify-content: center;
            align-items: center;

            border-radius: 50%;
            background: #b8c9f5;

            color: white;
            font-size: 28px;
            font-weight: bold;
        }

        h2 {
            text-align: center;
            margin: 0 0 8px;
            color: #3f4654;
        }

        .subtitle {
            text-align: center;
            color: #9299a8;
            font-size: 14px;
            margin-bottom: 28px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;

            color: #555d6d;
            font-weight: bold;
        }

        input {
            width: 100%;
            padding: 13px 14px;

            border: 1px solid #dfe4ee;
            border-radius: 8px;

            font-size: 15px;
            outline: none;

            transition: 0.2s;
        }

        input::placeholder {
            color: #b5bac5;
        }

        input:focus {
            border-color: #a9bce8;

            box-shadow:
                0 0 0 3px rgba(169, 188, 232, 0.2);
        }

        button {
            width: 100%;
            padding: 13px;

            border: none;
            border-radius: 8px;

            background: #a9bce8;

            color: white;
            font-size: 16px;
            font-weight: bold;

            cursor: pointer;
            transition: 0.2s;
        }

        button:hover {
            background: #96ace0;

            transform: translateY(-1px);

            box-shadow:
                0 5px 12px rgba(150, 172, 224, 0.3);
        }

        .error {
            padding: 10px 12px;
            margin-bottom: 18px;

            border-radius: 7px;

            background: #fff0f0;
            color: #d66b6b;

            font-size: 14px;
        }
    </style>
</head>

<body>

<div class="login-box">

    <div class="logo">L</div>

    <h2>Đăng nhập</h2>

    <div class="subtitle">
        Vui lòng đăng nhập để tiếp tục
    </div>

    @if ($errors->any())
        <div class="error">
            {{ $errors->first() }}
        </div>
    @endif

    <form method="POST" action="/login">
        @csrf

        <div class="form-group">
            <label for="email">Email</label>

            <input
                type="email"
                id="email"
                name="email"
                value="{{ old('email') }}"
                placeholder="Nhập email của bạn"
                required
            >
        </div>

        <div class="form-group">
            <label for="password">Mật khẩu</label>

            <input
                type="password"
                id="password"
                name="password"
                placeholder="Nhập mật khẩu"
                required
            >
        </div>

        <button type="submit">
            Đăng nhập
        </button>
    </form>

</div>

</body>
</html>