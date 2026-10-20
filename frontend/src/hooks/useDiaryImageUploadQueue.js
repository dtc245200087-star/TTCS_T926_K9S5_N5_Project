import { useCallback, useEffect, useRef, useState } from "react";
import {
  deleteDiaryImageJob,
  readDiaryImageJobs,
  saveDiaryImageJobs,
  updateDiaryImageJob,
} from "../sync/diaryImageQueueStore.js";

function isRetryableError(error) {
  return error.retryable === true
    || error.name === "TypeError"
    || error.name === "AbortError"
    || !navigator.onLine;
}

export function mockUploadImage(job, signal) {
  if (!navigator.onLine) {
    return Promise.reject(new TypeError("Thiết bị đang ngoại tuyến."));
  }

  return new Promise((resolve, reject) => {
    let settled = false;
    const finish = callback => value => {
      if (settled) return;
      settled = true;
      window.clearTimeout(timeoutId);
      signal?.removeEventListener("abort", handleAbort);
      callback(value);
    };
    const resolveUpload = finish(resolve);
    const rejectUpload = finish(reject);
    const handleAbort = () => {
      const abortError = new Error("Đã hủy tải ảnh.");
      abortError.name = "AbortError";
      rejectUpload(abortError);
    };
    const timeoutId = window.setTimeout(() => {
      if (!navigator.onLine) {
        rejectUpload(new TypeError("Mất kết nối mạng trong khi tải ảnh."));
        return;
      }
      const thumbnailUrl = URL.createObjectURL(job.thumbnailBlob);
      resolveUpload({
        id: `mock-${job.uploadId}`,
        url: thumbnailUrl,
        thumbnail_url: thumbnailUrl,
        ghi_chu: job.note || "",
        isMockUpload: true,
      });
    }, 1500);

    if (signal?.aborted) {
      handleAbort();
      return;
    }
    signal?.addEventListener("abort", handleAbort, {once: true});
  });
}

export function useDiaryImageUploadQueue(onUploaded) {
  const [items, setItems] = useState([]);
  const [isOnline, setIsOnline] = useState(() => navigator.onLine);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const onUploadedRef = useRef(onUploaded);
  const workerRunning = useRef(false);
  const mounted = useRef(false);
  const activeController = useRef(null);
  const retryTimer = useRef(null);
  const resolvingDiaryIds = useRef(false);

  onUploadedRef.current = onUploaded;

  const publish = useCallback(nextItems => {
    if (mounted.current) {
      setItems(current => {
        const unchanged = current.length === nextItems.length
          && current.every((item, index) => {
            const next = nextItems[index];
            return item.id === next.id
              && item.status === next.status
              && item.entryId === next.entryId
              && item.fileName === next.fileName
              && item.attempts === next.attempts
              && item.lastError === next.lastError
              && item.syncedAt === next.syncedAt
              && item.retryable === next.retryable;
          });
        return unchanged ? current : nextItems;
      });
    }
  }, []);

  const refresh = useCallback(async () => {
    const jobs = await readDiaryImageJobs();
    publish(jobs);
    return jobs;
  }, [publish]);

  const updateJob = useCallback(async (id, changes) => {
    await updateDiaryImageJob(id, changes);
    return refresh();
  }, [refresh]);

  const enqueueImages = useCallback(async images => {
    if (!images.length) return [];
    const createdAt = new Date().toISOString();
    const jobs = images.map(image => ({
      id: `s33-image-${image.id}`,
      entryId: image.entryId || null,
      fileName: image.file.name,
      imageBlob: image.compressedBlob,
      thumbnailBlob: image.thumbnailBlob,
      note: image.note || "",
      uploadId: image.id,
      diaryQueueId: image.diaryQueueId || null,
      createdAt,
      attempts: 0,
      status: image.entryId ? "pending" : "waiting-entry",
      lastError: "",
    }));
    if (jobs.some(job => !job.imageBlob || !job.thumbnailBlob)) {
      throw new Error("Ảnh chưa nén xong; hãy thử nén lại trước khi lưu.");
    }
    await saveDiaryImageJobs(jobs);
    await refresh();
    return jobs;
  }, [refresh]);

  const resolveWaitingEntries = useCallback(async diaryQueueItems => {
    if (resolvingDiaryIds.current) return;
    const syncedDiaries = diaryQueueItems
      .filter(item => item.type === "diary" && item.status === "synced" && item.id)
      .sort((left, right) =>
        (right.syncedAt || right.createdAt || "").localeCompare(left.syncedAt || left.createdAt || "")
      );
    if (!syncedDiaries.length) return;

    resolvingDiaryIds.current = true;
    try {
      const jobs = await readDiaryImageJobs();
      const waitingJobs = jobs.filter(job => job.status === "waiting-entry");
      for (const job of waitingJobs) {
        const diary = syncedDiaries.find(item => item.id === job.diaryQueueId) || syncedDiaries[0];
        await updateDiaryImageJob(job.id, {
          entryId: diary.id,
          status: "pending",
          lastError: "",
          retryable: false,
        });
      }
      if (waitingJobs.length) await refresh();
    } catch (queueError) {
      setError(queueError.message || "Không thể gắn ID nhật ký vào hàng đợi ảnh.");
    } finally {
      resolvingDiaryIds.current = false;
    }
  }, [refresh]);

  const retryImage = useCallback(async id => {
    await updateJob(id, {status: "pending", lastError: ""});
  }, [updateJob]);

  const removeImage = useCallback(async id => {
    await deleteDiaryImageJob(id);
    await refresh();
  }, [refresh]);

  const drainQueue = useCallback(async () => {
    if (workerRunning.current || !navigator.onLine || !mounted.current) return;
    workerRunning.current = true;
    try {
      while (navigator.onLine && mounted.current) {
        const jobs = await readDiaryImageJobs();
        publish(jobs);
        const job = jobs.find(item => item.status === "pending" && item.entryId);
        if (!job) break;

        const attempts = (job.attempts || 0) + 1;
        await updateJob(job.id, {status: "uploading", attempts, lastError: ""});
        const controller = new AbortController();
        const timeoutId = window.setTimeout(() => controller.abort(), 30000);
        activeController.current = controller;
        try {
          const result = await mockUploadImage(job, controller.signal);
          await updateJob(job.id, {status: "synced", syncedAt: new Date().toISOString(), lastError: ""});
          onUploadedRef.current?.(job, result);
        } catch (uploadError) {
          const retryable = isRetryableError(uploadError);
          const message = uploadError.message || "Không thể tải ảnh lên.";
          await updateJob(job.id, {
            status: retryable ? "waiting" : "error",
            lastError: message,
            retryable,
          });
          if (retryable && navigator.onLine && mounted.current) {
            const delay = Math.min(30000, 1000 * (2 ** Math.min(attempts - 1, 5)));
            window.clearTimeout(retryTimer.current);
            retryTimer.current = window.setTimeout(async () => {
              try {
                await updateJob(job.id, {status: "pending"});
              } catch (queueError) {
                setError(queueError.message || "Không thể lên lịch thử tải ảnh lại.");
              }
            }, delay);
            break;
          }
          if (!navigator.onLine) break;
        } finally {
          window.clearTimeout(timeoutId);
          if (activeController.current === controller) activeController.current = null;
        }
      }
    } catch (queueError) {
      setError(queueError.message || "Không thể xử lý hàng đợi ảnh.");
    } finally {
      workerRunning.current = false;
      if (mounted.current) {
        try {
          await refresh();
        } catch (queueError) {
          setError(queueError.message || "Không thể làm mới hàng đợi ảnh.");
        }
      }
    }
  }, [publish, refresh, updateJob]);

  useEffect(() => {
    mounted.current = true;
    let active = true;

    async function loadJobs() {
      try {
        const jobs = await readDiaryImageJobs();
        const restored = jobs.map(job => {
          const oldJsonParseFailure = job.status === "error"
            && job.lastError?.includes("Unexpected token")
            && job.lastError?.includes("doctype");
          if (oldJsonParseFailure) {
            return {...job, status: "pending", lastError: "", retryable: true};
          }
          return job.status === "uploading"
            || (job.status === "waiting" && job.retryable && navigator.onLine)
            ? {...job, status: "pending"}
            : job;
        });
        if (restored.some((job, index) => job !== jobs[index])) {
          await saveDiaryImageJobs(restored);
        }
        if (active) publish(restored);
      } catch (queueError) {
        if (active) setError(queueError.message || "Không thể khôi phục hàng đợi ảnh.");
      } finally {
        if (active) setIsLoading(false);
      }
    }

    const updateConnection = () => {
      setIsOnline(navigator.onLine);
      if (!navigator.onLine) {
        activeController.current?.abort();
        return;
      }
      window.clearTimeout(retryTimer.current);
      retryTimer.current = null;
      readDiaryImageJobs()
        .then(async jobs => {
          for (const job of jobs) {
            if (job.status === "waiting" && job.retryable) {
              await updateDiaryImageJob(job.id, {status: "pending"});
            }
          }
          return refresh();
        })
        .catch(queueError => setError(queueError.message || "Không thể khởi động lại hàng đợi ảnh."));
    };

    window.addEventListener("online", updateConnection);
    window.addEventListener("offline", updateConnection);
    loadJobs();

    return () => {
      active = false;
      mounted.current = false;
      activeController.current?.abort();
      window.clearTimeout(retryTimer.current);
      window.removeEventListener("online", updateConnection);
      window.removeEventListener("offline", updateConnection);
    };
  }, [publish, refresh]);

  useEffect(() => {
    if (!isLoading && isOnline) drainQueue();
  }, [isLoading, isOnline, items, drainQueue]);

  return {items, isOnline, isLoading, error, enqueueImages, resolveWaitingEntries, retryImage, removeImage};
}
