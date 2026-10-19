const FIELD_LABELS = {
  cong_trinh: "Công trình",
  ngay: "Ngày",
  gio: "Thời gian",
  cong_viec_id: "Hạng mục ID",
  hang_muc: "Hạng mục",
  noi_dung: "Mô tả công việc",
  nhan_luc_so_nguoi: "Số nhân lực",
  nhan_luc_ghi_chu: "Ghi chú nhân lực",
  thiet_bi: "Thiết bị",
  thoi_tiet: "Thời tiết",
  ghi_chu_thoi_tiet: "Ghi chú thời tiết",
};

function valuesEqual(left, right) {
  if (Object.is(left, right)) return true;
  return JSON.stringify(left) === JSON.stringify(right);
}

function combineConflictValues(left, right) {
  if (Array.isArray(left) && Array.isArray(right)) {
    return [...left, ...right.filter(value => !left.some(item => valuesEqual(item, value)))];
  }
  if (typeof left === "string" && typeof right === "string") {
    const values = [left.trim(), right.trim()].filter(Boolean);
    return [...new Set(values)].join("\n\n");
  }
  return { banA: left, banB: right };
}

export function getDiaryFieldLabel(field) {
  return FIELD_LABELS[field] || field.replaceAll("_", " ");
}

export function compareDiaryVersions(base, versionA, versionB) {
  const fields = new Set([
    ...Object.keys(base || {}),
    ...Object.keys(versionA || {}),
    ...Object.keys(versionB || {}),
  ]);
  const merged = {};
  const conflicts = [];

  for (const field of fields) {
    const baseValue = base?.[field];
    const valueA = versionA?.[field];
    const valueB = versionB?.[field];
    const changedA = !valuesEqual(valueA, baseValue);
    const changedB = !valuesEqual(valueB, baseValue);

    if (changedA && changedB && !valuesEqual(valueA, valueB)) {
      conflicts.push({field, base: baseValue, versionA: valueA, versionB: valueB});
      merged[field] = valueA;
    } else if (changedA) {
      merged[field] = valueA;
    } else if (changedB) {
      merged[field] = valueB;
    } else if (field in (base || {})) {
      merged[field] = baseValue;
    }
  }

  return {merged, conflicts};
}

export function resolveDiaryConflict(base, versionA, versionB, choice) {
  if (choice === "versionA") return {...versionA};
  if (choice === "versionB") return {...versionB};
  if (choice !== "merge") throw new Error("Lựa chọn xử lý xung đột không hợp lệ.");

  const {merged, conflicts} = compareDiaryVersions(base, versionA, versionB);
  for (const conflict of conflicts) {
    merged[conflict.field] = combineConflictValues(conflict.versionA, conflict.versionB);
  }
  return merged;
}
