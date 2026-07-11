import type { ReactNode } from "react";

export function PageHeader({
  title,
  subtitle,
}: {
  title: string;
  subtitle: string;
}) {
  return (
    <header className="page-header">
      <div>
        <p className="eyebrow">PULSERESOLVE AI</p>
        <h2>{title}</h2>
        <p className="muted">{subtitle}</p>
      </div>
    </header>
  );
}

export function MetricCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: string | number;
  detail: string;
}) {
  return (
    <article className="metric-card">
      <p className="muted">{label}</p>
      <strong>{value}</strong>
      <small>{detail}</small>
    </article>
  );
}

export function StatusBadge({
  value,
}: {
  value: string;
}) {
  const classValue = value.replaceAll("_", "-");
  return (
    <span className={`badge badge-${classValue}`}>
      {value.replaceAll("_", " ")}
    </span>
  );
}

export function Panel({
  children,
  title,
}: {
  children: ReactNode;
  title?: string;
}) {
  return (
    <section className="panel">
      {title ? <h3>{title}</h3> : null}
      {children}
    </section>
  );
}

export function ErrorBanner({
  message,
}: {
  message: string;
}) {
  return <div className="error-banner">{message}</div>;
}
