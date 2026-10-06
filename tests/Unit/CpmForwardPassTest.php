<?php

namespace Tests\Unit;

use PHPUnit\Framework\TestCase;
use App\Services\CpmService;
use App\Services\TaskDTO;

class CpmForwardPassTest extends TestCase
{
    public function test_calculate_forward_pass_correctly()
    {
        $service = new CpmService();

        // 1. Dữ liệu đầu vào thử nghiệm
        $tasks = [
            'A' => new TaskDTO('A', 3),
            'B' => new TaskDTO('B', 4),
            'C' => new TaskDTO('C', 2, ['A']),
            'D' => new TaskDTO('D', 5, ['A', 'B']),
        ];

        // 2. Thứ tự Topological thu được từ bài S-07
        $sortedIds = ['A', 'B', 'C', 'D'];

        // 3. Gọi thuật toán tính Forward Pass (S-08)
        $result = $service->calculateForwardPass($tasks, $sortedIds);

        // 4. Kiểm tra kết quả ES và EF từng công việc
        $this->assertEquals(0, $result['A']->es);
        $this->assertEquals(3, $result['A']->ef);

        $this->assertEquals(0, $result['B']->es);
        $this->assertEquals(4, $result['B']->ef);

        $this->assertEquals(3, $result['C']->es);
        $this->assertEquals(5, $result['C']->ef);

        $this->assertEquals(4, $result['D']->es); // max(EF_A=3, EF_B=4) = 4
        $this->assertEquals(9, $result['D']->ef);
    }
}