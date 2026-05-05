import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { recordsApi } from '../services/api'

const STAT_META = [
  { key: 'total',    label: 'Total Records',    cls: 'total'    },
  { key: 'active',   label: 'Active',           cls: 'active'   },
  { key: 'expiring', label: 'Expiring Soon',    cls: 'expiring' },
  { key: 'disposed', label: 'Disposed',         cls: 'disposed' },
]

export default function DashboardPage() {
  const navigate = useNavigate()
  const [stats, setStats] = useState(null)
  const [recent, setRecent] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([recordsApi.getStats(), recordsApi.getAll(0, 5)])
      .then(([statsRes, recordsRes]) => {
        setStats(statsRes.data)
        setRecent(recordsRes.data.content || [])
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="spinner" />

  return (
    <>
      <h2 className="section-title">Dashboard</h2>

      <div className="stat-grid">
        {STAT_META.map(({ key, label, cls }) => (
          <div key={key} className={`stat-card ${cls}`}>
            <span className="stat-label">{label}</span>
            <span className="stat-value">{stats?.[key] ?? '—'}</span>
          </div>
        ))}
      </div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h3 style={{ fontWeight: 700 }}>Recent Records</h3>
          <button className="btn btn-primary btn-sm" onClick={() => navigate('/records')}>
            View All
          </button>
        </div>

        {recent.length === 0 ? (
          <div className="empty-state">
            <h4>No records yet</h4>
            <p>Go to Records to create your first entry.</p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Department</th>
                  <th>Status</th>
                  <th>Expiry</th>
                </tr>
              </thead>
              <tbody>
                {recent.map(r => (
                  <tr key={r.id}>
                    <td style={{ fontWeight: 500 }}>{r.name}</td>
                    <td>{r.department || '—'}</td>
                    <td><StatusBadge status={r.status} /></td>
                    <td style={{ color: '#64748b', fontSize: '.85rem' }}>{r.expiryDate}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  )
}

function StatusBadge({ status }) {
  const map = { ACTIVE: 'badge-active', EXPIRING: 'badge-expiring', DISPOSED: 'badge-disposed' }
  return <span className={`badge ${map[status] || ''}`}>{status}</span>
}
