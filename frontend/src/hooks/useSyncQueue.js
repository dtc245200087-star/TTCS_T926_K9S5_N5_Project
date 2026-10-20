import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { apiFetch, setCsrfToken } from "../api.js";
import {
  markPendingItemsSynced,
  readQueueState,
  saveQueueItems,
} from "../sync/queueStore.js";

export function useSyncQueue() {
  const [items, setItems] = useState([]);
  const syncLock = useRef(false);
  const [lastSuccessfulSyncAt, setLastSuccessfulSyncAt] = useState(null);
  const [isOnline, setIsOnline] = useState(() => navigator.onLine);
  const [isLoading, setIsLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [error, setError] = useState("");

  const refreshQueue = useCallback(async () => {
    try {
      const state = await readQueueState();
      setItems(state.items);
      setLastSuccessfulSyncAt(state.lastSuccessfulSyncAt);
      setError("");
    } catch (queueError) {
      setError(queueError.message || "Không thể đọc hàng đợi đồng bộ.");
      throw queueError;
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    let active = true;
    const updateConnection = () => setIsOnline(navigator.onLine);
    window.addEventListener("online", updateConnection);
    window.addEventListener("offline", updateConnection);

    readQueueState()
      .then(state => {
        if (!active) return;
        setItems(state.items);
        setLastSuccessfulSyncAt(state.lastSuccessfulSyncAt);
        setError("");
      })
      .catch(queueError => {
        if (active) setError(queueError.message || "Không thể đọc hàng đợi đồng bộ.");
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => {
      active = false;
      window.removeEventListener("online", updateConnection);
      window.removeEventListener("offline", updateConnection);
    };
  }, []);

  const enqueueItems = useCallback(async newItems => {
    const createdAt = new Date().toISOString();
    const normalizedItems = newItems.map(item => ({
      ...item,
      createdAt: item.createdAt || createdAt,
      status: "pending",
    }));
    await saveQueueItems(normalizedItems);
    await refreshQueue();
  }, [refreshQueue]);

  // S30_REAL_UPLOAD: never mark queued images synced without a server response.
  const syncNow = useCallback(async () => {
    if (!navigator.onLine || syncLock.current) return false;
    syncLock.current = true;
    setIsSyncing(true);
    setError("");
    window.dispatchEvent(new Event("diary-sync-request"));
    let succeeded = false;
    try {
      const state = await readQueueState();
      const pendingImages = state.items.filter(item => item.status === "pending" && item.type === "image");
      if (!pendingImages.length) return true;
      const csrfResponse = await apiFetch("/api/auth/csrf");
      if (!csrfResponse.ok) throw new Error("Không xác thực được phiên đồng bộ ảnh.");
      const csrf = await csrfResponse.json();
      setCsrfToken(csrf.csrf_token);
      for (const item of pendingImages) {
        if (!navigator.onLine) break;
        try {
          const payload = item.payload;
          const body = new FormData();
          body.append("image", payload.imageBlob, payload.fileName || "image.jpg");
          body.append("thumbnail", payload.thumbnailBlob || payload.imageBlob, "thumbnail.jpg");
          body.append("ghi_chu_anh", payload.note || "");
          body.append("upload_id", payload.uploadId);
          const response = await apiFetch(`/api/nhat-ky/${payload.entryId}/images`, {
            method: "POST", body,
          });
          if (!response.ok) {
            const result = await response.json().catch(() => ({}));
            throw new Error(result.message || `Không gửi được ảnh (HTTP ${response.status}).`);
          }
          await markPendingItemsSynced(new Date().toISOString(), [item.id]);
          succeeded = true;
        } catch (uploadError) {
          setError(uploadError.message || "Ảnh chưa được đồng bộ; sẽ thử lại.");
          // A failed image must not block the others.
        }
      }
      return succeeded;
    } catch (syncError) {
      setError(syncError.message || "Không thể đồng bộ hàng đợi.");
      return false;
    } finally {
      await refreshQueue().catch(() => {});
      syncLock.current = false;
      setIsSyncing(false);
    }
  }, [refreshQueue]);

  useEffect(() => {
    if (!isOnline) return undefined;
    const retry = () => { syncNow(); };
    window.addEventListener("online", retry);
    const interval = window.setInterval(retry, 30_000);
    retry();
    return () => {
      window.removeEventListener("online", retry);
      window.clearInterval(interval);
    };
  }, [isOnline, syncNow]);

  const markItemSynced = useCallback(async itemId => {
    try {
      await markPendingItemsSynced(new Date().toISOString(), [itemId]);
      await refreshQueue();
    } catch (syncError) {
      setError(syncError.message || "Không thể cập nhật trạng thái đồng bộ.");
    }
  }, [refreshQueue]);

  const summary = useMemo(() => {
    const pending = items.filter(item => item.status === "pending");
    return {
      pendingDiaryCount: pending.filter(item => item.type === "diary").length,
      pendingImageCount: pending.filter(item => item.type === "image").length,
      items,
    };
  }, [items]);

  return {
    ...summary,
    lastSuccessfulSyncAt,
    isOnline,
    isLoading,
    isSyncing,
    error,
    enqueueItems,
    syncNow,
    markItemSynced,
    refreshQueue,
  };
}
