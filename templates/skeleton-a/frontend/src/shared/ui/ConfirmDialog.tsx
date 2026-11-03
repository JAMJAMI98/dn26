import { Button } from "./Button";

export function ConfirmDialog({ open, title, message, confirmLabel = "확인", onConfirm, onCancel }: {
  open: boolean; title: string; message: string; confirmLabel?: string; onConfirm: () => void; onCancel: () => void;
}) {
  if (!open) return null;
  return (
    <div className="ui-dialog-backdrop" role="dialog" aria-modal="true">
      <div className="ui-dialog">
        <strong>{title}</strong>
        <p>{message}</p>
        <div className="ui-row-end">
          <Button onClick={onCancel}>취소</Button>
          <Button variant="primary" onClick={onConfirm}>{confirmLabel}</Button>
        </div>
      </div>
    </div>
  );
}
