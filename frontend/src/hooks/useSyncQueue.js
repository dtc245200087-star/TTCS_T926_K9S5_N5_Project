import { useCallback, useEffect, useMemo, useState } from "react";
import {
  markPendingItemsSynced,
  readQueueState,
  saveQueueItems,
} from "../sync/queueStore.js";

export function useSyncQueue() {
  const [items, setItems] = useState([]);
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

  const syncNow = useCallback(async () => {
    if (!isOnline || isSyncing) return false;
    setIsSyncing(true);
    setError("");
    try {
      const timestamp = new Date().toISOString();
      const changed = await markPendingItemsSynced(timestamp);
      await refreshQueue();
      return changed;
    } catch (syncError) {
      setError(syncError.message || "Không thể cập nhật trạng thái đồng bộ.");
      return false;
    } finally {
      setIsSyncing(false);
    }
  }, [isOnline, isSyncing, refreshQueue]);

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
