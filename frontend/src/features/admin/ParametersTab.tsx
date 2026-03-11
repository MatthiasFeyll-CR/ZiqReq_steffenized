import { useState, useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "react-toastify";
import { fetchParameters, patchParameter, type AdminParameter } from "@/api/admin";

export function ParametersTab() {
  const { t } = useTranslation();
  const [parameters, setParameters] = useState<AdminParameter[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchParameters()
      .then(setParameters)
      .catch((err) => toast.error(`${t("admin.failedLoadParameters")}: ${err.message}`))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (editingKey && inputRef.current) {
      inputRef.current.focus();
    }
  }, [editingKey]);

  function startEditing(param: AdminParameter) {
    setEditingKey(param.key);
    setEditValue(param.value);
  }

  async function saveEdit(key: string) {
    try {
      const updated = await patchParameter(key, editValue);
      setParameters((prev) => prev.map((p) => (p.key === key ? updated : p)));
      setEditingKey(null);
      toast.success(t("admin.parameterUpdated", { key }));
    } catch (err) {
      toast.error(`${t("admin.failedUpdateParameter")}: ${(err as Error).message}`);
    }
  }

  function cancelEdit() {
    setEditingKey(null);
  }

  function handleKeyDown(e: React.KeyboardEvent, key: string) {
    if (e.key === "Enter") {
      e.preventDefault();
      saveEdit(key);
    } else if (e.key === "Escape") {
      cancelEdit();
    }
  }

  if (loading) {
    return (
      <div className="py-6">
        <p className="text-sm text-muted-foreground">{t("admin.loadingParameters")}</p>
      </div>
    );
  }

  return (
    <div className="py-6">
      <div className="overflow-x-auto rounded-md border">
        <table className="w-full text-sm" data-testid="parameters-table">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="px-4 py-3 text-left font-medium">{t("admin.tableKey")}</th>
              <th className="px-4 py-3 text-left font-medium">{t("admin.tableValue")}</th>
              <th className="px-4 py-3 text-left font-medium">{t("admin.tableDefault")}</th>
              <th className="px-4 py-3 text-left font-medium">{t("admin.tableDescription")}</th>
              <th className="px-4 py-3 text-left font-medium">{t("admin.tableCategory")}</th>
            </tr>
          </thead>
          <tbody>
            {parameters.map((param) => {
              const isModified = param.value !== param.default_value;
              const isEditing = editingKey === param.key;

              return (
                <tr key={param.key} className="border-b last:border-b-0">
                  <td className="px-4 py-3 font-mono text-xs">
                    <span className="flex items-center gap-2">
                      {isModified && (
                        <span
                          className="inline-block h-2 w-2 rounded-full bg-primary"
                          data-testid={`modified-indicator-${param.key}`}
                          title={t("admin.modifiedFromDefault")}
                        />
                      )}
                      {param.key}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {isEditing ? (
                      <input
                        ref={inputRef}
                        type="text"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        onKeyDown={(e) => handleKeyDown(e, param.key)}
                        onBlur={cancelEdit}
                        className="w-full rounded border border-border bg-background px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                        data-testid={`edit-input-${param.key}`}
                      />
                    ) : (
                      <span
                        className="cursor-pointer rounded px-1 py-0.5 hover:bg-muted"
                        onDoubleClick={() => startEditing(param)}
                        data-testid={`value-${param.key}`}
                        role="button"
                        tabIndex={0}
                      >
                        {param.value}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">{param.default_value}</td>
                  <td className="px-4 py-3 text-muted-foreground">{param.description}</td>
                  <td className="px-4 py-3">
                    <span className="rounded-full bg-muted px-2 py-0.5 text-xs">
                      {param.category}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
