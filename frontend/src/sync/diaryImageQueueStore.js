const DATABASE_NAME = "construction-diary-image-queue";
const DATABASE_VERSION = 1;
const STORE_NAME = "uploads";

let databasePromise;

function openDatabase() {
  if (!("indexedDB" in window)) {
    return Promise.reject(new Error("Trình duyệt không hỗ trợ lưu hàng đợi ảnh."));
  }
  if (databasePromise) return databasePromise;

  databasePromise = new Promise((resolve, reject) => {
    const request = window.indexedDB.open(DATABASE_NAME, DATABASE_VERSION);
    request.onupgradeneeded = () => {
      if (!request.result.objectStoreNames.contains(STORE_NAME)) {
        request.result.createObjectStore(STORE_NAME, {keyPath: "id"});
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(
      request.error || new Error("Không thể mở hàng đợi ảnh trên thiết bị."),
    );
    request.onblocked = () => reject(new Error("Hàng đợi ảnh đang được dùng ở cửa sổ khác."));
  });

  databasePromise.catch(() => {
    databasePromise = undefined;
  });
  return databasePromise;
}

function transactionDone(transaction) {
  return new Promise((resolve, reject) => {
    transaction.oncomplete = () => resolve();
    transaction.onerror = () => reject(
      transaction.error || new Error("Không thể lưu hàng đợi ảnh."),
    );
    transaction.onabort = () => reject(
      transaction.error || new Error("Thao tác với hàng đợi ảnh đã bị hủy."),
    );
  });
}

function requestResult(request) {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error || new Error("Không thể đọc hàng đợi ảnh."));
  });
}

export async function readDiaryImageJobs() {
  const database = await openDatabase();
  const transaction = database.transaction(STORE_NAME, "readonly");
  const done = transactionDone(transaction);
  const jobs = await requestResult(transaction.objectStore(STORE_NAME).getAll());
  await done;
  return jobs.sort((left, right) => left.createdAt.localeCompare(right.createdAt));
}

export async function saveDiaryImageJobs(jobs) {
  if (!jobs.length) return;
  const database = await openDatabase();
  const transaction = database.transaction(STORE_NAME, "readwrite");
  const done = transactionDone(transaction);
  const store = transaction.objectStore(STORE_NAME);
  for (const job of jobs) store.put(job);
  await done;
}

export async function updateDiaryImageJob(id, changes) {
  const database = await openDatabase();
  const transaction = database.transaction(STORE_NAME, "readwrite");
  const done = transactionDone(transaction);
  const store = transaction.objectStore(STORE_NAME);
  const current = await requestResult(store.get(id));
  if (!current) {
    await done;
    throw new Error("Không tìm thấy ảnh trong hàng đợi.");
  }
  store.put({...current, ...changes});
  await done;
}

export async function deleteDiaryImageJob(id) {
  const database = await openDatabase();
  const transaction = database.transaction(STORE_NAME, "readwrite");
  const done = transactionDone(transaction);
  transaction.objectStore(STORE_NAME).delete(id);
  await done;
}
