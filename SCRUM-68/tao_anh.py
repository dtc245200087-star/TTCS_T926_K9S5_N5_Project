
from PIL import Image, ImageDraw

# Tạo ảnh mẫu với kích thước 1920x1080
anh = Image.new("RGB", (1920, 1080), "white")

# Viết nội dung lên ảnh
draw = ImageDraw.Draw(anh)

draw.text(
    (100, 100),
    "ANH NGHIEM THU - SCRUM 68",
    fill="black"
)

draw.text(
    (100, 160),
    "Anh mau khong co EXIF",
    fill="red"
)

# Lưu ảnh JPG
anh.save("anh_nghiem_thu.jpg", "JPEG")

print("Da tao anh JPG thanh cong!")
