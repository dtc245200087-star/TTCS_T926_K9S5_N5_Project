def tinh_tien_do_trung_binh(cong_trinh):
    if not cong_trinh:
        return 0
    return round(sum(x.tien_do for x in cong_trinh) / len(cong_trinh), 1)
