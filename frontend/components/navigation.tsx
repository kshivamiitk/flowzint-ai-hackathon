"use client";

import {
  Activity,
  Bot,
  CheckCheck,
  ClipboardCheck,
  LayoutDashboard,
  Radar,
  ScrollText,
  type LucideIcon,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const links: Array<{
  href: string;
  label: string;
  icon: LucideIcon;
}> = [
  { href: "/", label: "Command center", icon: LayoutDashboard },
  { href: "/chat", label: "Resolution console", icon: Bot },
  { href: "/incidents", label: "Incident intelligence", icon: Radar },
  { href: "/approvals", label: "Approval queue", icon: ClipboardCheck },
  { href: "/audit", label: "Audit trail", icon: ScrollText },
];

export function Navigation() {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      <div className="brand-lockup">
        <div className="brand-mark">
          <Activity aria-hidden="true" size={23} />
        </div>
        <div>
          <h1>PulseResolve</h1>
          <p className="sidebar-muted">Resolution intelligence</p>
        </div>
      </div>
      <nav>
        {links.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={
              pathname === href
                ? "nav-link nav-link-active"
                : "nav-link"
            }
          >
            <Icon aria-hidden="true" size={18} />
            {label}
          </Link>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div className="sidebar-footer-title">
          <CheckCheck aria-hidden="true" size={16} />
          Demo environment
        </div>
        <span>
          Synthetic data · policy guarded
        </span>
      </div>
    </aside>
  );
}
