import { ButtonHTMLAttributes } from "react";

export function Button({ variant = "default", ...rest }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "default" | "primary" | "danger" }) {
  return <button className="ui-btn" data-variant={variant} {...rest} />;
}
