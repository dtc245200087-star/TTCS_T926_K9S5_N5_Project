const DATABASE_NAME = "construction-sync-queue";
const DATABASE_VERSION = 1;
const ITEM_STORE = "items";
const META_STORE = "metadata";

let databasePromise;

function openDatabase() {
  if (!("indexedDB" in window)) {
    return Promise.reject(new Error("Trình duyệt không hỗ trợ lưu hàng đợi đồng bộ."));
  }
  if (databasePromise) return databasePromise;

  databasePromise = new Promise((resolve, reject) => {
    const request = window.indexedDB.open(DATABASE_NAME, DATABASE_VERSION);
    request.onupgradeneeded = () => {
      const database = request.result;
      if (!database.objectStoreNames.contains(ITEM_STORE)) {
        database.createObjectStore(ITEM_STORE, {keyPath: "id"});
      }
      if (!database.objectStoreNames.contains(META_STORE)) {
        database.createObjectStore(META_STORE, {keyPath: "key"});
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(
      request.error || new Error("Không thể mở hàng đợi đồng bộ trên thiết bị."),
    );
    request.onblocked = () => reject(
      new Error("Hàng đợi đồng bộ đang được dùng ở một cửa sổ khác."),
    );
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
      transaction.error || new Error("Không thể lưu hàng đợi đồng bộ."),
    );
    transaction.onabort = () => reject(
      transaction.error || new Error("Thao tác với hàng đợi đồng bộ đã bị hủy."),
    );
  });
}

export async function readQueueState() {
  const database = await openDatabase();
  const transaction = database.transaction([ITEM_STORE, META_STORE], "readonly");
  const done = transactionDone(transaction);
  const itemsRequest = transaction.objectStore(ITEM_STORE).getAll();
  const metadataRequest = transaction.objectStore(META_STORE).get("lastSuccessfulSyncAt");
  const [items, metadata] = await Promise.all([
    new Promise((resolve, reject) => {
      itemsRequest.onsuccess = () => resolve(itemsRequest.result);
      itemsRequest.onerror = () => reject(itemsRequest.error);
    }),
    new Promise((resolve, reject) => {
      metadataRequest.onsuccess = () => resolve(metadataRequest.result);
      metadataRequest.onerror = () => reject(metadataRequest.error);
    }),
  ]);
  await done;
  return {
    items: items.sort((left, right) => left.createdAt.localeCompare(right.createdAt)),
    lastSuccessfulSyncAt: metadata?.value || null,
  };
}

export async function saveQueueItems(items) {
  if (!items.length) return;
  const database = await openDatabase();
  const transaction = database.transaction(ITEM_STORE, "readwrite");
  const done = transactionDone(transaction);
  const store = transaction.objectStore(ITEM_STORE);
  for (const item of items) store.put(item);
  await done;
}

export async function markPendingItemsSynced(timestamp, itemIds = null) {
  const database = await openDatabase();
  const transaction = database.transaction([ITEM_STORE, META_STORE], "readwrite");
  const done = transactionDone(transaction);
  const itemStore = transaction.objectStore(ITEM_STORE);
  let changed = false;
  const request = itemStore.getAll();
  request.onsuccess = () => {
    for (const item of request.result) {
      if (item.status !== "pending" || (itemIds && !itemIds.includes(item.id))) continue;
      item.status = "synced";
      item.syncedAt = timestamp;
      itemStore.put(item);
      changed = true;
    }
    if (changed) {
      transaction.objectStore(META_STORE).put({
        key: "lastSuccessfulSyncAt",
        value: timestamp,
      });
    }
  };
  await done;
  return changed;
}
