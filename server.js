const express = require('express');
const multer = require('multer');
const ExifReader = require('exifreader');

const app = express();
const port = 3000;

// Cấu hình multer lưu tạm file ảnh trên RAM để đọc EXIF
const upload = multer({ storage: multer.memoryStorage() });

// API nhận upload ảnh và đọc metadata
app.post('/api/upload', upload.single('photo'), (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ success: false, message: 'Chưa có file ảnh nào được tải lên!' });
        }

        // Đọc siêu dữ liệu EXIF từ buffer của ảnh gốc
        const tags = ExifReader.load(req.file.buffer);

        // 1. Lấy thời điểm chụp
        let capturedAt = tags['DateTimeOriginal'] ? tags['DateTimeOriginal'].description : null;

        // 2. Lấy tọa độ GPS (Vĩ độ, Kinh độ)
        let latitude = tags['GPSLatitude'] ? tags['GPSLatitude'].description : null;
        let longitude = tags['GPSLongitude'] ? tags['GPSLongitude'].description : null;

        const imageMetadata = {
            filename: req.file.originalname,
            capturedAt: capturedAt || 'Không có thông tin thời gian',
            location: {
                latitude: latitude || 'Không có tọa độ',
                longitude: longitude || 'Không có tọa độ'
            }
        };

        return res.status(200).json({
            success: true,
            message: 'Đọc thời gian và tọa độ từ ảnh thành công!',
            data: imageMetadata
        });

    } catch (error) {
        console.error(error);
        return res.status(500).json({ success: false, message: 'Lỗi server khi xử lý ảnh.' });
    }
});

app.listen(port, () => {
    console.log(`Server đang chạy tại http://localhost:${port}`);
});