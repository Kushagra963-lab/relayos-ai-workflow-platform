import { useState } from 'react';
import {
  Activity,
  ArrowUpRight,
  Bell,
  Bot,
  Building2,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  CircleHelp,
  Clock3,
  FileCheck2,
  GitBranch,
  LayoutDashboard,
  ListTodo,
  Menu,
  MoreHorizontal,
  Plug,
  Search,
  Settings2,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  UserRound,
  Users,
  Workflow,
  X,
  Zap
} from 'lucide-react';

const navGroups = [
  {
    label: 'Workspace',
    items: [
      { label: 'Overview', icon: LayoutDashboard, active: true },
      { label: 'Workflows', icon: Workflow, count: 24 },
      { label: 'Approvals', icon: ListTodo, count: 7 },
      { label: 'AI agents', icon: Bot }
    ]
  },
  {
    label: 'Intelligence',
    items: [
      { label: 'Analytics', icon: TrendingUp },
      { label: 'Audit trail', icon: ShieldCheck },
      { label: 'Integrations', icon: Plug }
    ]
  }
];

const metrics = [
  {
    label: 'Active workflows',
    value: '24',
    change: '+3 this month',
    detail: '21 running normally',
    icon: Workflow,
    tone: 'violet'
  },
  {
    label: 'In-flight runs',
    value: '1,284',
    change: '+12.8%',
    detail: 'vs. previous 7 days',
    icon: Activity,
    tone: 'blue'
  },
  {
    label: 'Automation rate',
    value: '86.4%',
    change: '+4.2%',
    detail: '10,492 hours saved',
    icon: Zap,
    tone: 'emerald'
  },
  {
    label: 'SLA at risk',
    value: '17',
    change: '5 need attention',
    detail: 'Across 3 departments',
    icon: Clock3,
    tone: 'amber',
    alert: true
  }
];

const approvals = [
  {
    id: 'REQ-2841',
    title: 'Cloud capacity expansion',
    context: 'Infrastructure purchase · $48,200',
    owner: 'Maya Chen',
    initials: 'MC',
    team: 'Technology',
    due: '42 min',
    status: 'SLA risk',
    tone: 'urgent'
  },
  {
    id: 'REQ-2838',
    title: 'Vendor security exception',
    context: 'Risk acceptance · High impact',
    owner: 'Aarav Patel',
    initials: 'AP',
    team: 'Security',
    due: '2 hr',
    status: 'Review',
    tone: 'review'
  },
  {
    id: 'REQ-2832',
    title: 'Regional hiring plan',
    context: 'Headcount request · 12 roles',
    owner: 'Priya Raman',
    initials: 'PR',
    team: 'People',
    due: 'Today',
    status: 'Pending',
    tone: 'pending'
  },
  {
    id: 'REQ-2829',
    title: 'Q3 campaign budget',
    context: 'Marketing spend · $82,000',
    owner: 'Noah Williams',
    initials: 'NW',
    team: 'Marketing',
    due: 'Tomorrow',
    status: 'Pending',
    tone: 'pending'
  }
];

const workflows = [
  {
    name: 'Employee onboarding',
    category: 'People operations',
    icon: Users,
    tone: 'violet',
    runs: '368',
    rate: '98.6%',
    updated: '3 min ago',
    status: 'Healthy'
  },
  {
    name: 'Purchase approvals',
    category: 'Finance',
    icon: FileCheck2,
    tone: 'blue',
    runs: '241',
    rate: '94.2%',
    updated: '8 min ago',
    status: 'Healthy'
  },
  {
    name: 'P1 incident escalation',
    category: 'Technology',
    icon: GitBranch,
    tone: 'rose',
    runs: '62',
    rate: '91.8%',
    updated: '14 min ago',
    status: 'Watch'
  },
  {
    name: 'Vendor due diligence',
    category: 'Risk & compliance',
    icon: ShieldCheck,
    tone: 'emerald',
    runs: '129',
    rate: '96.1%',
    updated: '22 min ago',
    status: 'Healthy'
  }
];

const chartLabels = ['Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue', 'Wed'];

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app-shell">
      <button
        type="button"
        className={`sidebar-scrim ${sidebarOpen ? 'visible' : ''}`}
        aria-label="Close navigation"
        onClick={() => setSidebarOpen(false)}
      />

      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`} aria-label="Main navigation">
        <div className="brand-row">
          <span className="brand-mark" aria-hidden="true">
            <GitBranch size={20} strokeWidth={2.4} />
          </span>
          <span className="brand-copy">
            <strong>RelayOS</strong>
            <small>AI workflow cloud</small>
          </span>
          <button
            type="button"
            className="sidebar-close"
            aria-label="Close navigation"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={18} />
          </button>
        </div>

        <nav className="sidebar-nav">
          {navGroups.map((group) => (
            <div className="nav-group" key={group.label}>
              <p>{group.label}</p>
              {group.items.map(({ label, icon: Icon, active, count }) => (
                <button
                  type="button"
                  className={`nav-item ${active ? 'active' : ''}`}
                  aria-current={active ? 'page' : undefined}
                  key={label}
                  onClick={() => setSidebarOpen(false)}
                >
                  <Icon size={18} strokeWidth={active ? 2.3 : 1.9} />
                  <span>{label}</span>
                  {count ? <span className="nav-count">{count}</span> : null}
                </button>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button type="button" className="nav-item">
            <CircleHelp size={18} />
            <span>Help center</span>
          </button>
          <button type="button" className="nav-item">
            <Settings2 size={18} />
            <span>Workspace settings</span>
          </button>
          <div className="system-status">
            <span className="status-pulse" />
            <div>
              <strong>All systems operational</strong>
              <small>Last checked just now</small>
            </div>
          </div>
        </div>
      </aside>

      <div className="app-frame">
        <header className="topbar">
          <div className="topbar-start">
            <button
              type="button"
              className="icon-button mobile-menu"
              aria-label="Open navigation"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu size={20} />
            </button>
            <button type="button" className="org-switcher" aria-label="Switch organization">
              <span className="org-avatar">N</span>
              <span className="org-copy">
                <small>Organization</small>
                <strong>Northstar Labs</strong>
              </span>
              <ChevronDown size={16} />
            </button>
          </div>

          <label className="global-search">
            <Search size={18} aria-hidden="true" />
            <span className="sr-only">Search workflows and requests</span>
            <input type="search" placeholder="Search workflows, requests, people…" />
            <kbd>⌘ K</kbd>
          </label>

          <div className="topbar-actions">
            <button type="button" className="icon-button" aria-label="Help">
              <CircleHelp size={19} />
            </button>
            <button type="button" className="icon-button notification-button" aria-label="Notifications">
              <Bell size={19} />
              <span />
            </button>
            <span className="topbar-divider" />
            <button type="button" className="user-control" aria-label="Open user menu">
              <span className="user-avatar">KS</span>
              <span className="user-copy">
                <strong>Kushagra Singh</strong>
                <small>Workspace admin</small>
              </span>
              <ChevronDown size={15} />
            </button>
          </div>
        </header>

        <main className="content">
          <section className="page-heading">
            <div>
              <div className="heading-kicker">
                <span className="live-indicator" />
                Live operations · Wednesday, July 8
              </div>
              <h1>Good morning, Kushagra.</h1>
              <p>Here’s how work is moving across Northstar Labs today.</p>
            </div>
            <div className="heading-actions">
              <button type="button" className="secondary-button">
                <Activity size={17} />
                View run history
              </button>
              <button type="button" className="primary-button">
                <Workflow size={17} />
                Create workflow
              </button>
            </div>
          </section>

          <section className="metric-grid" aria-label="Workflow performance overview">
            {metrics.map((metric) => (
              <MetricCard key={metric.label} {...metric} />
            ))}
          </section>

          <section className="overview-grid">
            <ThroughputCard />
            <InsightCard />
          </section>

          <section className="operations-grid">
            <ApprovalQueue />
            <ActiveWorkflows />
          </section>
        </main>
      </div>
    </div>
  );
}

function MetricCard({ label, value, change, detail, icon: Icon, tone, alert }) {
  return (
    <article className="metric-card">
      <div className="metric-topline">
        <span className={`metric-icon ${tone}`}>
          <Icon size={19} strokeWidth={2.1} />
        </span>
        <button type="button" className="more-button" aria-label={`More options for ${label}`}>
          <MoreHorizontal size={19} />
        </button>
      </div>
      <div className="metric-value-row">
        <strong>{value}</strong>
        {alert ? <span className="risk-pill">Attention</span> : null}
      </div>
      <p>{label}</p>
      <div className="metric-context">
        <span className={alert ? 'alert' : ''}>{change}</span>
        <small>{detail}</small>
      </div>
    </article>
  );
}

function ThroughputCard() {
  return (
    <article className="panel throughput-card">
      <div className="panel-header">
        <div>
          <span className="section-label">Workflow throughput</span>
          <h2>12,842 runs this week</h2>
          <p>Up 12.8% from the previous seven days</p>
        </div>
        <button type="button" className="period-control">
          Last 7 days
          <ChevronDown size={15} />
        </button>
      </div>

      <div className="chart-legend" aria-hidden="true">
        <span><i className="legend-dot runs" />Started</span>
        <span><i className="legend-dot completed" />Completed</span>
      </div>

      <div className="chart-wrap">
        <div className="chart-y-axis" aria-hidden="true">
          <span>3k</span>
          <span>2k</span>
          <span>1k</span>
          <span>0</span>
        </div>
        <div className="chart-main">
          <svg
            className="throughput-chart"
            viewBox="0 0 760 228"
            role="img"
            aria-label="Workflow runs rose through the week, peaking on Wednesday"
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient id="runArea" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stopColor="#6c5ce7" stopOpacity="0.26" />
                <stop offset="100%" stopColor="#6c5ce7" stopOpacity="0" />
              </linearGradient>
            </defs>
            <g className="chart-grid-lines">
              <line x1="0" y1="18" x2="760" y2="18" />
              <line x1="0" y1="80" x2="760" y2="80" />
              <line x1="0" y1="142" x2="760" y2="142" />
              <line x1="0" y1="204" x2="760" y2="204" />
            </g>
            <path
              className="chart-area"
              d="M0 177 C52 170 74 132 126 140 S210 170 254 137 S336 87 380 105 S466 132 507 91 S588 51 633 68 S710 41 760 34 L760 214 L0 214 Z"
            />
            <path
              className="chart-line runs"
              d="M0 177 C52 170 74 132 126 140 S210 170 254 137 S336 87 380 105 S466 132 507 91 S588 51 633 68 S710 41 760 34"
            />
            <path
              className="chart-line completed"
              d="M0 191 C54 184 78 155 126 160 S211 184 254 154 S336 112 380 123 S465 151 507 115 S587 80 633 92 S710 68 760 61"
            />
            <g className="chart-focus-point">
              <circle cx="760" cy="34" r="8" />
              <circle cx="760" cy="34" r="3.5" />
            </g>
          </svg>
          <div className="chart-x-axis" aria-hidden="true">
            {chartLabels.map((label) => <span key={label}>{label}</span>)}
          </div>
        </div>
      </div>
    </article>
  );
}

function InsightCard() {
  return (
    <article className="insight-card">
      <div className="insight-header">
        <span className="ai-symbol"><Sparkles size={19} /></span>
        <span>Relay intelligence</span>
        <span className="ai-live">AI insight</span>
      </div>
      <div className="insight-body">
        <p className="insight-eyebrow">Emerging bottleneck</p>
        <h2>Finance approvals are taking 18% longer this week.</h2>
        <p className="insight-summary">
          Seven requests above $25k are waiting on the same approval step. Rebalancing them could recover 11 hours of cycle time.
        </p>
        <div className="insight-signal">
          <span><Clock3 size={16} /></span>
          <div>
            <strong>3.8 hours average delay</strong>
            <small>Purchase approval · Finance review</small>
          </div>
        </div>
      </div>
      <button type="button" className="insight-action">
        Review AI analysis
        <ArrowUpRight size={16} />
      </button>
    </article>
  );
}

function ApprovalQueue() {
  return (
    <article className="panel approval-card">
      <div className="panel-header compact">
        <div>
          <span className="section-label">Your work queue</span>
          <h2>Approvals needing attention</h2>
        </div>
        <button type="button" className="text-button">
          View all <ChevronRight size={15} />
        </button>
      </div>

      <div className="queue-table" role="table" aria-label="Approvals needing attention">
        <div className="queue-head" role="row">
          <span role="columnheader">Request</span>
          <span role="columnheader">Requester</span>
          <span role="columnheader">Due</span>
          <span role="columnheader">Status</span>
          <span aria-hidden="true" />
        </div>
        {approvals.map((approval) => (
          <button type="button" className="queue-row" role="row" key={approval.id}>
            <span className="request-cell" role="cell">
              <small>{approval.id}</small>
              <strong>{approval.title}</strong>
              <span>{approval.context}</span>
            </span>
            <span className="owner-cell" role="cell">
              <i>{approval.initials}</i>
              <span>
                <strong>{approval.owner}</strong>
                <small>{approval.team}</small>
              </span>
            </span>
            <span className="due-cell" role="cell">{approval.due}</span>
            <span role="cell">
              <i className={`status-badge ${approval.tone}`}>{approval.status}</i>
            </span>
            <span className="row-arrow" role="cell"><ChevronRight size={17} /></span>
          </button>
        ))}
      </div>
    </article>
  );
}

function ActiveWorkflows() {
  return (
    <article className="panel workflow-card">
      <div className="panel-header compact">
        <div>
          <span className="section-label">Automation portfolio</span>
          <h2>Active workflows</h2>
        </div>
        <button type="button" className="text-button">
          Manage <ChevronRight size={15} />
        </button>
      </div>

      <div className="workflow-list">
        {workflows.map(({ name, category, icon: Icon, tone, runs, rate, updated, status }) => (
          <button type="button" className="workflow-row" key={name}>
            <span className={`workflow-icon ${tone}`}><Icon size={18} /></span>
            <span className="workflow-name">
              <strong>{name}</strong>
              <small>{category} · {updated}</small>
            </span>
            <span className="workflow-stat">
              <strong>{runs}</strong>
              <small>Runs</small>
            </span>
            <span className="workflow-stat rate">
              <strong>{rate}</strong>
              <small>Success</small>
            </span>
            <span className={`health-label ${status === 'Watch' ? 'watch' : ''}`}>
              <i /> {status}
            </span>
            <ChevronRight className="workflow-arrow" size={17} />
          </button>
        ))}
      </div>

      <div className="workflow-footer">
        <div className="mini-avatars" aria-hidden="true">
          <span>KS</span><span>MC</span><span>AP</span><span>+8</span>
        </div>
        <p><strong>11 owners</strong> are managing 24 active workflows</p>
      </div>
    </article>
  );
}
