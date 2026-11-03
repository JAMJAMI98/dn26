import { InputHTMLAttributes } from "react";

export function Field({ label, error, hint, ...input }: InputHTMLAttributes<HTMLInputElement> & { label: string; error?: string; hint?: string }) {
  return (
    <label className="ui-field">
      <span>{label}</span>
      <input {...input} aria-invalid={error ? true : undefined} />
      {hint && !error && <span className="ui-hint">{hint}</span>}
      {error && <span className="ui-error">{error}</span>}
    </label>
  );
}
