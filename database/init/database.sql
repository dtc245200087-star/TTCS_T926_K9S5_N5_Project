CREATE TABLE IF NOT EXISTS cong_trinh (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten VARCHAR(255) NOT NULL,
    dia_diem VARCHAR(255),
    tien_do INTEGER DEFAULT 0,
    trang_thai VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS nhan_su (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ho_ten VARCHAR(150) NOT NULL,
    vai_tro VARCHAR(100),
    cong_trinh VARCHAR(255),
    trang_thai VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS vat_tu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten VARCHAR(150) NOT NULL,
    don_vi VARCHAR(30),
    ton_kho DECIMAL(12,2) DEFAULT 0,
    muc_toi_thieu DECIMAL(12,2) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS cong_viec (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten VARCHAR(255) NOT NULL,
    cong_trinh VARCHAR(255),
    nguoi_phu_trach VARCHAR(150),
    trang_thai VARCHAR(100),
    han DATE,
    ngay_bat_dau_thuc_te DATE,
    ngay_ket_thuc_thuc_te DATE,
    phan_tram_hoan_thanh INTEGER NOT NULL DEFAULT 0
        CHECK (phan_tram_hoan_thanh BETWEEN 0 AND 100),
    CHECK (
        ngay_bat_dau_thuc_te IS NULL OR ngay_ket_thuc_thuc_te IS NULL
        OR ngay_ket_thuc_thuc_te >= ngay_bat_dau_thuc_te
    )
);
