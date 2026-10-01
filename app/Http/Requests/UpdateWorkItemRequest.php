<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class UpdateWorkItemRequest extends FormRequest
{
    public function authorize(): bool
    {
        abort_unless((int) $this->route('workItem')->project_id === (int) $this->route('project')->id, 404);

        return true;
    }

    public function rules(): array
    {
        return ['parent_id' => ['present', 'nullable', 'integer', 'min:1']];
    }

    public function messages(): array
    {
        $name = $this->route('workItem')->name;

        return [
            'parent_id.present' => "Vui lòng chọn cha cho hạng mục «{$name}» hoặc để trống để chuyển thành hạng mục gốc.",
            'parent_id.integer' => "Hạng mục cha của «{$name}» không hợp lệ.",
            'parent_id.min' => "Hạng mục cha của «{$name}» không hợp lệ.",
        ];
    }
}
