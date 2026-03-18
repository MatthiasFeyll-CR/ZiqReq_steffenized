import { env } from "@/config/env";
import { authFetch, getAccessToken } from "@/lib/auth-token";

export interface Attachment {
  id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  extraction_status: "pending" | "processing" | "completed" | "failed";
  created_at: string;
  deleted_at: string | null;
  message_id: string | null;
}

export async function uploadAttachment(
  projectId: string,
  file: File,
  onProgress?: (percent: number) => void,
): Promise<Attachment> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const url = `${env.apiBaseUrl}/projects/${projectId}/attachments/`;

    xhr.upload.addEventListener("progress", (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    });

    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(JSON.parse(xhr.responseText));
        } catch {
          reject(new Error("Invalid response"));
        }
      } else {
        try {
          const body = JSON.parse(xhr.responseText);
          reject(new Error(body.message || body.error || `Upload failed (${xhr.status})`));
        } catch {
          reject(new Error(`Upload failed (${xhr.status})`));
        }
      }
    });

    xhr.addEventListener("error", () => reject(new Error("Network error")));
    xhr.addEventListener("abort", () => reject(new Error("Upload aborted")));

    xhr.open("POST", url);
    xhr.withCredentials = true;

    const token = getAccessToken();
    if (token) {
      xhr.setRequestHeader("Authorization", `Bearer ${token}`);
    }

    const formData = new FormData();
    formData.append("file", file);
    xhr.send(formData);
  });
}

export async function deleteAttachment(
  projectId: string,
  attachmentId: string,
): Promise<void> {
  const url = `${env.apiBaseUrl}/projects/${projectId}/attachments/${attachmentId}/`;
  const res = await authFetch(url, { method: "DELETE", credentials: "include" });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Delete failed (${res.status})`);
  }
}

export async function getAttachmentUrl(
  projectId: string,
  attachmentId: string,
): Promise<string> {
  const url = `${env.apiBaseUrl}/projects/${projectId}/attachments/${attachmentId}/url/`;
  const res = await authFetch(url, { credentials: "include" });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  const data = await res.json();
  return data.url;
}

export async function listAttachments(
  projectId: string,
): Promise<Attachment[]> {
  const url = `${env.apiBaseUrl}/projects/${projectId}/attachments/`;
  const res = await authFetch(url, { credentials: "include" });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function listAttachmentsIncludeDeleted(
  projectId: string,
): Promise<Attachment[]> {
  const url = `${env.apiBaseUrl}/projects/${projectId}/attachments/?include_deleted=true`;
  const res = await authFetch(url, { credentials: "include" });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function restoreAttachment(
  projectId: string,
  attachmentId: string,
): Promise<Attachment> {
  const url = `${env.apiBaseUrl}/projects/${projectId}/attachments/${attachmentId}/restore/`;
  const res = await authFetch(url, { method: "POST", credentials: "include" });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Restore failed (${res.status})`);
  }
  return res.json();
}
