<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nhật ký công trường - SITEPRO BUILD</title>
    <style>
        :root {
            color-scheme: light;
            font-family: Arial, Helvetica, sans-serif;
            color: #172033;
            background: #f3f5f8;
            font-size: 16px;
        }

        * { box-sizing: border-box; }
        body { margin: 0; min-width: 320px; }
        button, input, select, textarea { font: inherit; }
        a { color: inherit; }

        .layout { display: flex; min-height: 100vh; }
        .sidebar {
            width: 248px;
            flex: 0 0 248px;
            background: #111827;
            color: #f8fafc;
            padding: 22px 14px;
        }
        .logo { font-size: 20px; font-weight: 800; margin: 8px 10px 30px; }
        .menu-title { color: #cbd5e1; font-size: 12px; font-weight: 700; margin: 18px 10px 8px; text-transform: uppercase; }
        .menu a { display: block; color: #e2e8f0; text-decoration: none; padding: 13px 12px; border-radius: 8px; margin: 4px 0; }
        .menu a:hover, .menu a.active { background: #f59e0b; color: #111827; font-weight: 700; }

        .main { flex: 1; min-width: 0; }
        .topbar { min-height: 68px; background: #fff; border-bottom: 1px solid #d6dbe4; display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 12px 28px; }
        .topbar h2 { margin: 0; font-size: 20px; }
        .user { color: #334155; font-size: 15px; }
        .content { width: min(1220px, 100%); margin: 0 auto; padding: 26px 28px 48px; }
        .page-header { display: flex; align-items: center; justify-content: space-between; gap: 18px; margin-bottom: 20px; }
        .page-header h1 { margin: 0 0 6px; font-size: 28px; }
        .page-header h2 { margin: 0 0 6px; font-size: 24px; }
        .page-header p { margin: 0; color: #475569; line-height: 1.5; }

        .panel, .diary, .filter { background: #fff; border: 1px solid #cbd3df; border-radius: 12px; box-shadow: 0 2px 8px rgb(15 23 42 / 4%); }
        .panel { padding: 20px; margin-bottom: 18px; }
        .panel h2 { margin: 0 0 6px; font-size: 21px; }
        .panel-intro { color: #475569; margin: 0 0 18px; line-height: 1.5; }

        .filter { display: grid; grid-template-columns: 1.1fr 1fr 1.1fr auto; align-items: end; gap: 12px; padding: 16px; margin-bottom: 18px; }
        .field { min-width: 0; }
        .field label { display: block; color: #1f2937; font-weight: 700; margin-bottom: 7px; }
        .field input, .field select, .field textarea {
            width: 100%;
            min-height: 50px;
            color: #111827;
            background: #fff;
            border: 2px solid #64748b;
            border-radius: 8px;
            padding: 11px 12px;
        }
        .field textarea { min-height: 112px; resize: vertical; line-height: 1.5; }
        .field input:focus, .field select:focus, .field textarea:focus, button:focus-visible, a:focus-visible { outline: 3px solid #f59e0b; outline-offset: 2px; }
        .field-hint { display: block; color: #475569; font-size: 13px; margin-top: 5px; }
        .field-error { color: #9f1239; font-size: 14px; font-weight: 700; margin-top: 5px; }
        .form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
        .field-wide { grid-column: 1 / -1; }

        .btn {
            display: inline-flex;
            min-height: 52px;
            align-items: center;
            justify-content: center;
            border: 2px solid #92400e;
            border-radius: 8px;
            background: #b45309;
            color: #fff;
            font-weight: 800;
            text-decoration: none;
            padding: 12px 18px;
            cursor: pointer;
        }
        .btn:hover { background: #92400e; }
        .btn-secondary { background: #1f2937; border-color: #1f2937; }
        .btn-secondary:hover { background: #111827; }
        .message { border-radius: 8px; padding: 14px 16px; margin-bottom: 16px; font-weight: 700; }
        .message-success { color: #14532d; background: #dcfce7; border: 1px solid #86efac; }
        .message-error { color: #881337; background: #fff1f2; border: 1px solid #fda4af; }

        .diary-list { display: grid; gap: 14px; }
        .diary { padding: 20px; }
        .diary-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 14px; margin-bottom: 12px; }
        .diary-time { color: #334155; font-size: 15px; font-weight: 800; margin-bottom: 5px; }
        .diary-title { font-size: 19px; font-weight: 800; line-height: 1.35; }
        .badge { flex: 0 0 auto; border-radius: 999px; background: #e0f2fe; color: #0c4a6e; padding: 8px 12px; font-size: 14px; font-weight: 800; }
        .diary-content { margin: 0 0 14px; color: #1f2937; line-height: 1.65; white-space: pre-line; }
        .diary-info { display: flex; flex-wrap: wrap; gap: 8px 22px; border-top: 1px solid #dbe1e9; padding-top: 13px; color: #334155; font-size: 14px; }
        .summary-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-bottom: 18px; }
        .summary-item { background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 12px; }
        .summary-item strong { display: block; color: #111827; margin-bottom: 5px; }
        .summary-item span { display: block; color: #334155; line-height: 1.5; white-space: pre-line; }
        .empty { border: 2px dashed #94a3b8; border-radius: 10px; padding: 24px; background: #fff; color: #334155; text-align: center; line-height: 1.5; }

        @media (max-width: 900px) {
            .sidebar { width: 210px; flex-basis: 210px; }
            .filter { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .summary-grid { grid-template-columns: 1fr; }
        }
        @media (max-width: 700px) {
            .layout { display: block; }
            .sidebar { display: none; }
            .topbar { min-height: 58px; padding: 10px 14px; align-items: flex-start; flex-direction: column; gap: 5px; }
            .topbar h2 { font-size: 19px; }
            .user { font-size: 14px; }
            .content { padding: 18px 12px 36px; }
            .page-header { display: block; margin-bottom: 16px; }
            .page-header h1 { font-size: 25px; }
            .panel { padding: 16px 13px; }
            .panel h2 { font-size: 20px; }
            .filter, .form-grid { grid-template-columns: 1fr; gap: 12px; }
            .field-wide { grid-column: auto; }
            .btn { width: 100%; min-height: 56px; font-size: 17px; }
            .diary { padding: 16px 14px; }
            .diary-top { display: block; }
            .badge { display: inline-block; margin-top: 10px; }
            .diary-info { display: grid; gap: 8px; }
        }
    </style>
</head>
<body>
<div class="layout">
    <aside class="sidebar" aria-label="Điều hướng chính">
        <div class="logo">🏗 SITEPRO BUILD</div>
        <div class="menu-title">Quản lý</div>
        <nav class="menu">
            <a href="/">📊 Tổng quan</a>
            <a href="/projects">🏢 Dự án</a>
            <a href="/work-items">📋 Công việc</a>
            <a href="/work-items/tree">🌳 Cây hạng mục</a>
            <a href="/materials">📦 Vật tư</a>
            <a href="/personnel">👥 Nhân sự</a>
            <a href="/safety">🦺 An toàn</a>
            <a href="/diaries" class="active" aria-current="page">📖 Nhật ký</a>
        </nav>
    </aside>

    <main class="main">
        <header class="topbar">
            <h2>📖 Nhật ký công trường</h2>
            <div class="user">Xin chào, <strong>{{ auth()->user()->name }}</strong></div>
        </header>

        <section class="content">
            <div class="page-header">
                <div>
                    <h1>Nhật ký công trường</h1>
                    <p>Ghi nhận công việc, nhân lực, thiết bị và thời tiết theo ngày.</p>
                </div>
            </div>

            @if (session('status'))
                <div class="message message-success" role="status">{{ session('status') }}</div>
            @endif

            @if ($errors->any())
                <div class="message message-error" role="alert">
                    Có thông tin chưa hợp lệ. Vui lòng kiểm tra các trường được đánh dấu bên dưới.
                </div>
            @endif

            <form class="filter" method="GET" action="{{ route('diaries.index') }}">
                <div class="field">
                    <label for="filter-project">Dự án</label>
                    <select id="filter-project" name="project" required>
                        @foreach ($projects as $project)
                            <option value="{{ $project->id }}" @selected((int) ($selectedProject?->id ?? 0) === (int) $project->id)>
                                {{ $project->name }}
                            </option>
                        @endforeach
                    </select>
                </div>
                <div class="field">
                    <label for="filter-date">Ngày nhật ký</label>
                    <input id="filter-date" type="date" name="date" value="{{ $selectedDate }}" required>
                </div>
                <div class="field">
                    <label for="filter-work-item">Lọc theo hạng mục</label>
                    <select id="filter-work-item" name="work_item">
                        <option value="">Tất cả hạng mục</option>
                        @foreach ($workItems as $workItem)
                            <option value="{{ $workItem->id }}" @selected((int) ($selectedWorkItemId ?? 0) === (int) $workItem->id)>
                                {{ $workItem->name }}
                            </option>
                        @endforeach
                    </select>
                </div>
                <button class="btn btn-secondary" type="submit">Lọc nhật ký</button>
            </form>

            @if ($selectedProject)
                <section class="panel" aria-labelledby="daily-summary-heading">
                    <h2 id="daily-summary-heading">Thông tin trong ngày</h2>
                    <p class="panel-intro">Lưu nhân lực, thiết bị và thời tiết một lần cho dự án và ngày đã chọn.</p>

                    <form method="POST" action="{{ route('diaries.summary.update') }}">
                        @csrf
                        @method('PUT')
                        <input type="hidden" name="project_id" value="{{ $selectedProject->id }}">
                        <input type="hidden" name="diary_date" value="{{ $selectedDate }}">

                        <div class="form-grid">
                            <div class="field">
                                <label for="workforce-count">Nhân lực (số người)</label>
                                <input id="workforce-count" type="number" name="workforce_count" min="0" max="10000" inputmode="numeric" value="{{ old('workforce_count', $dailyDiary?->workforce_count) }}" aria-describedby="workforce-count-error">
                                @error('workforce_count')<div id="workforce-count-error" class="field-error">{{ $message }}</div>@enderror
                            </div>
                            <div class="field">
                                <label for="weather-condition">Thời tiết</label>
                                <select id="weather-condition" name="weather_condition">
                                    <option value="">Chưa ghi nhận</option>
                                    @foreach ($weatherLabels as $value => $label)
                                        <option value="{{ $value }}" @selected(old('weather_condition', $dailyDiary?->weather_condition) === $value)>{{ $label }}</option>
                                    @endforeach
                                </select>
                                @error('weather_condition')<div class="field-error">{{ $message }}</div>@enderror
                            </div>
                            <div class="field field-wide">
                                <label for="workforce-notes">Ghi chú nhân lực</label>
                                <textarea id="workforce-notes" name="workforce_notes" maxlength="4000" placeholder="Ví dụ: 8 thợ xây, 2 thợ điện">{{ old('workforce_notes', $dailyDiary?->workforce_notes) }}</textarea>
                                @error('workforce_notes')<div class="field-error">{{ $message }}</div>@enderror
                            </div>
                            <div class="field field-wide">
                                <label for="equipment-notes">Thiết bị sử dụng</label>
                                <textarea id="equipment-notes" name="equipment_notes" maxlength="4000" placeholder="Tên thiết bị, số lượng hoặc tình trạng sử dụng">{{ old('equipment_notes', $dailyDiary?->equipment_notes) }}</textarea>
                                @error('equipment_notes')<div class="field-error">{{ $message }}</div>@enderror
                            </div>
                            <div class="field field-wide">
                                <label for="weather-notes">Ghi chú thời tiết</label>
                                <textarea id="weather-notes" name="weather_notes" maxlength="4000" placeholder="Ví dụ: Mưa từ 14:00, tạm dừng đổ bê tông">{{ old('weather_notes', $dailyDiary?->weather_notes) }}</textarea>
                                @error('weather_notes')<div class="field-error">{{ $message }}</div>@enderror
                            </div>
                            <div class="field field-wide">
                                <button class="btn" type="submit">Lưu thông tin trong ngày</button>
                            </div>
                        </div>
                    </form>
                </section>

                <section class="panel" aria-labelledby="new-entry-heading">
                    <h2 id="new-entry-heading">Thêm mục nhật ký</h2>
                    <p class="panel-intro">Mỗi mục phải gắn với hạng mục để có thể tra cứu theo hồ sơ thi công.</p>

                    @if ($workItems->isEmpty())
                        <div class="empty">Dự án chưa có hạng mục. Hãy tạo hạng mục trước khi ghi nhật ký.</div>
                    @else
                        <form method="POST" action="{{ route('diaries.entries.store') }}">
                            @csrf
                            <input type="hidden" name="project_id" value="{{ $selectedProject->id }}">
                            <input type="hidden" name="diary_date" value="{{ $selectedDate }}">
                            <div class="form-grid">
                                <div class="field">
                                    <label for="entry-work-item">Hạng mục <span aria-hidden="true">*</span></label>
                                    <select id="entry-work-item" name="work_item_id" required aria-describedby="work-item-error">
                                        <option value="">Chọn hạng mục</option>
                                        @foreach ($workItems as $workItem)
                                            <option value="{{ $workItem->id }}" @selected((int) old('work_item_id', $selectedWorkItemId ?? 0) === (int) $workItem->id)>{{ $workItem->name }}</option>
                                        @endforeach
                                    </select>
                                    @error('work_item_id')<div id="work-item-error" class="field-error">{{ $message }}</div>@enderror
                                </div>
                                <div class="field">
                                    <label for="entry-time">Giờ ghi nhận <span aria-hidden="true">*</span></label>
                                    <input id="entry-time" type="time" name="entry_time" value="{{ old('entry_time', now()->format('H:i')) }}" required>
                                    @error('entry_time')<div class="field-error">{{ $message }}</div>@enderror
                                </div>
                                <div class="field field-wide">
                                    <label for="work-description">Nội dung công việc <span aria-hidden="true">*</span></label>
                                    <textarea id="work-description" name="work_description" maxlength="5000" required placeholder="Mô tả công việc đã thực hiện, kết quả hoặc vấn đề phát sinh">{{ old('work_description') }}</textarea>
                                    @error('work_description')<div class="field-error">{{ $message }}</div>@enderror
                                </div>
                                <div class="field field-wide">
                                    <button class="btn" type="submit">Thêm vào nhật ký ngày {{ \Illuminate\Support\Carbon::parse($selectedDate)->format('d/m/Y') }}</button>
                                </div>
                            </div>
                        </form>
                    @endif
                </section>

                <section aria-labelledby="entries-heading">
                    <div class="page-header">
                        <div>
                            <h2 id="entries-heading">Nhật ký ngày {{ \Illuminate\Support\Carbon::parse($selectedDate)->format('d/m/Y') }}</h2>
                            <p>{{ $selectedProject->name }} · {{ $entries->count() }} mục</p>
                        </div>
                    </div>

                    @if ($dailyDiary && ($dailyDiary->workforce_count !== null || $dailyDiary->workforce_notes || $dailyDiary->equipment_notes || $dailyDiary->weather_condition || $dailyDiary->weather_notes))
                        <div class="summary-grid" aria-label="Thông tin nhân lực, thiết bị và thời tiết">
                            @if ($dailyDiary->workforce_count !== null || $dailyDiary->workforce_notes)
                                <div class="summary-item"><strong>Nhân lực</strong><span>{{ $dailyDiary->workforce_count !== null ? $dailyDiary->workforce_count.' người' : 'Chưa nhập số lượng' }}{{ $dailyDiary->workforce_notes ? "\n".$dailyDiary->workforce_notes : '' }}</span></div>
                            @endif
                            @if ($dailyDiary->equipment_notes)
                                <div class="summary-item"><strong>Thiết bị</strong><span>{{ $dailyDiary->equipment_notes }}</span></div>
                            @endif
                            @if ($dailyDiary->weather_condition || $dailyDiary->weather_notes)
                                <div class="summary-item"><strong>Thời tiết</strong><span>{{ $weatherLabels[$dailyDiary->weather_condition] ?? 'Chưa ghi nhận' }}{{ $dailyDiary->weather_notes ? "\n".$dailyDiary->weather_notes : '' }}</span></div>
                            @endif
                        </div>
                    @endif

                    @if ($entries->isEmpty())
                        <div class="empty">Chưa có mục nhật ký phù hợp với bộ lọc. Hãy thêm nội dung công việc cho ngày này.</div>
                    @else
                        <div class="diary-list">
                            @foreach ($entries as $entry)
                                <article class="diary">
                                    <div class="diary-top">
                                        <div>
                                            <div class="diary-time">{{ \Illuminate\Support\Carbon::parse($entry->entry_time)->format('H:i') }} · {{ \Illuminate\Support\Carbon::parse($selectedDate)->format('d/m/Y') }}</div>
                                            <div class="diary-title">{{ $entry->workItem->name }}</div>
                                        </div>
                                        <span class="badge">{{ $entry->workItem->name }}</span>
                                    </div>
                                    <p class="diary-content">{{ $entry->work_description }}</p>
                                    <div class="diary-info">
                                        <span>Người ghi: <strong>{{ $entry->recordedBy?->name ?? 'Tài khoản đã xóa' }}</strong></span>
                                        <span>Hạng mục: <strong>{{ $entry->workItem->name }}</strong></span>
                                    </div>
                                </article>
                            @endforeach
                        </div>
                    @endif
                </section>
            @else
                <div class="empty">Tài khoản chưa có dự án được phân quyền. Hãy tham gia một dự án trước khi ghi nhật ký.</div>
            @endif
        </section>
    </main>
</div>
</body>
</html>
