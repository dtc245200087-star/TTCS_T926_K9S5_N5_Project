const DATABASE_NAME = "dieu-hanh-thi-cong-offline";
const DATABASE_VERSION = 1;
const DRAFT_LIMIT = 20;

let databasePromise;

function openDatabase() {
  if (databasePromise) return databasePromise;
  databasePromise = new Promise((resolve, reject) => {
    if (!("indexedDB" in window)) {
      reject(new Error("Trình duyệt không hỗ trợ lưu nhật ký offline."));
      return;
    }
    const request = indexedDB.open(DATABASE_NAME, DATABASE_VERSION);
    request.onupgradeneeded = () => {
      const database = request.result;
      if (!database.objectStoreNames.contains("drafts")) {
        database.createObjectStore("drafts", {keyPath: "local_id"});
      }
      if (!database.objectStoreNames.contains("cache")) {
        database.createObjectStore("cache", {keyPath: "key"});
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error || new Error("Không mở được kho nhật ký offline."));
    request.onblocked = () => reject(new Error("Kho offline đang được mở ở một thẻ khác. Hãy tải lại trang."));
  }).catch(error => {
    databasePromise = null;
    throw error;
  });
  return databasePromise;
}

function requestResult(request) {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error || new Error("Không thể truy cập kho offline."));
  });
}

export async function cacheValue(key, value) {
  const database = await openDatabase();
  const transaction = database.transaction("cache", "readwrite");
  transaction.objectStore("cache").put({key, value, saved_at: Date.now()});
  await transactionDone(transaction);
}

export async function readCachedValue(key) {
  const database = await openDatabase();
  const record = await requestResult(database.transaction("cache").objectStore("cache").get(key));
  return record?.value ?? null;
}

export async function saveOfflineProfile(user) {
  await cacheValue("last-user", user);
}

export async function getOfflineProfile() {
  return readCachedValue("last-user");
}

export async function clearOfflineProfile() {
  const database = await openDatabase();
  const transaction = database.transaction("cache", "readwrite");
  transaction.objectStore("cache").delete("last-user");
  await transactionDone(transaction);
}

export async function listOfflineDrafts({owner_id, project, diary_date, task_id} = {}) {
  const database = await openDatabase();
  const drafts = await requestResult(database.transaction("drafts").objectStore("drafts").getAll());
  return drafts.filter(draft =>
    (owner_id == null || draft.owner_id === owner_id)
    && (project == null || draft.cong_trinh === project)
    && (diary_date == null || draft.ngay === diary_date)
    && (task_id == null || String(draft.cong_viec_id) === String(task_id))
  ).sort((left, right) => right.created_at - left.created_at);
}

export async function saveOfflineDraft(draft) {
  const allDrafts = await listOfflineDrafts({owner_id: draft.owner_id});
  const existing = allDrafts.some(item => item.local_id === draft.local_id);
  if (!existing && allDrafts.length >= DRAFT_LIMIT) {
    throw new Error("Đã đạt giới hạn 20 nhật ký chờ đồng bộ. Hãy kết nối mạng để đồng bộ trước khi tạo thêm.");
  }
  const estimate = await getStorageEstimate();
  const imageBytes = (draft.images || []).reduce((total, image) => total + (image.blob?.size || 0) + (image.thumbnail?.size || 0), 0);
  const estimatedEntryBytes = new Blob([JSON.stringify({...draft, images: []})]).size + imageBytes;
  if (estimate.quota && estimate.usage + estimatedEntryBytes > estimate.quota * 0.95) {
    throw new Error("Dung lượng thiết bị gần đầy. Hãy giải phóng dung lượng hoặc đồng bộ nhật ký đang chờ.");
  }
  const database = await openDatabase();
  const transaction = database.transaction("drafts", "readwrite");
  transaction.objectStore("drafts").put(draft);
  await transactionDone(transaction);
}

export async function updateOfflineDraft(draft) {
  const database = await openDatabase();
  const transaction = database.transaction("drafts", "readwrite");
  transaction.objectStore("drafts").put(draft);
  await transactionDone(transaction);
}

export async function deleteOfflineDraft(localId) {
  const database = await openDatabase();
  const transaction = database.transaction("drafts", "readwrite");
  transaction.objectStore("drafts").delete(localId);
  await transactionDone(transaction);
}

export async function getStorageEstimate() {
  try {
    const estimate = await navigator.storage?.estimate?.();
    return {usage: estimate?.usage || 0, quota: estimate?.quota || 0};
  } catch {
    return {usage: 0, quota: 0};
  }
}

export async function requestPersistentStorage() {
  try {
    if (navigator.storage?.persist && !(await navigator.storage.persisted?.())) {
      await navigator.storage.persist();
    }
  } catch {
    // IndexedDB still works when the browser does not grant persistent storage.
  }
}

export function transactionDone(transaction) {
  return new Promise((resolve, reject) => {
    transaction.oncomplete = () => resolve();
    transaction.onerror = () => reject(transaction.error || new Error("Không lưu được dữ liệu offline."));
    transaction.onabort = () => reject(transaction.error || new Error("Lưu dữ liệu offline đã bị hủy."));
  });
}

export const OFFLINE_DRAFT_LIMIT = DRAFT_LIMIT;
