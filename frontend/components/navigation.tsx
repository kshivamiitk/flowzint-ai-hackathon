import Link from "next/link";

const links = [
  ["/", "Overview"],
  ["/chat", "Customer Chat"],
  ["/incidents", "Incidents"],
  ["/approvals", "Approvals"],
  ["/audit", "Audit Trail"],
];

export function Navigation() {
  return (
    <aside className="sidebar">
      <div>
        <div className="brand-mark">P</div>
        <h1>PulseResolve</h1>
        <p className="sidebar-muted">
          AI Customer Operations
        </p>
      </div>
      <nav>
        {links.map(([href, label]) => (
          <Link
            key={href}
            href={href}
            className="nav-link"
          >
            {label}
          </Link>
        ))}
      </nav>
      <div className="sidebar-footer">
        <span className="status-dot" />
        Local demo ready
      </div>
    </aside>
  );
}
