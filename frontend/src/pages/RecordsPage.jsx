import { useEffect, useState, useCallback, useRef } from 'react'
import { recordsApi } from '../services/api'
import RecordModal from '../components/RecordModal'

const STATUS_BADGE = { ACTIVE: 'badge-active', EXPIRING: 'badge-expiring', DISPOSED: 'badge-disposed' }

function StatusBadge({ status }) {
  return <span className={`badge ${STATUS_BADGE[status] || ''}`}>{status}</span>
}

export default function RecordsPage() {
  const role = localStorage.getItem('role') || ''
  const isAdmin = role === 'ADMIN'

  const [records, setRecords] = useState([])
  const [page, setPage] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [totalElements, setTotalElements] = useState(0)
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [detail, setDetail] = useState(null)
  const [analyzing, setAnalyzing] = useState(null)
  const [error, setError] = useState('')
  const searchTimer = useRef(null)

  const fetchRecords = useCallback(async (q, p) => {
    setLoading(true)
    setError('')
    try {
      const res = q
        ? await recordsApi.search(q, p, 10)
        : await recordsApi.getAll(p, 10)
      const data = res.data
      setRecords(data.content || [])
      setTotalPages(data.totalPages || 0)
      setTotalElements(data.totalElements || 0)
    } catch {
      setError('Failed to load records.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchRecords(query, page) }, [page])

  function handleSearch(e) {
    const val = e.target.value
    setQuery(val)
    clearTimeout(searchTimer.current)
    searchTimer.current = setTimeout(() => {
      setPage(0)
      fetchRecords(val, 0)
    }, 350)
  }

  async function handleSave(form) {
    if (editing) {
      await recordsApi.update(editing.id, form)
    } else {
      await recordsApi.create(form)
    }
    setModalOpen(false)
    setEditing(null)
    fetchRecords(query, page)
  }

  async function handleDelete(id) {
    if (!window.confirm('Mark this record as disposed?')) return
    await recordsApi.delete(id)
    fetchRecords(query, page)
  }

  async function handlePermanentDelete(id) {
    if (!window.confirm('Permanently delete this record? This cannot be undone.')) return
    await recordsApi.permanentDelete(id)
    fetchRecords(query, page)
  }

  async function handleAnalyze(id) {
    setAnalyzing(id)
    try {
      const res = await recordsApi.analyze(id)
      setRecords(prev => prev.map(r => r.id === id ? res.data : r))
      if (detail?.id === id) setDetail(res.data)
    } catch {
      alert('AI analysis failed. Check that the AI service is running.')
    } finally {
      setAnalyzing(null)
    }
  }

  async function handleExport() {
    try {
      const res = await recordsApi.exportCsv()
      const url = URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = 'data-records.csv'
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      alert('Export failed.')
    }
  }

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h2 className="section-title" style={{ margin: 0 }}>
          Records <span style={{ color: '#94a3b8', fontWeight: 400, fontSize: '.9rem' }}>({totalElements})</span>
        </h2>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-secondary btn-sm" onClick={handleExport}>Export CSV</button>
          <button className="btn btn-primary btn-sm" onClick={() => { setEditing(null); setModalOpen(true) }}>
            + New Record
          </button>
        </div>
      </div>

      <div className="toolbar">
        <input
          className="form-control search-input"
          placeholder="Search records…"
          value={query}
          onChange={handleSearch}
        />
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="card" style={{ padding: 0 }}>
        {loading ? (
          <div className="spinner" />
        ) : records.length === 0 ? (
          <div className="empty-state">
            <h4>No records found</h4>
            <p>{query ? 'Try a different search term.' : 'Create your first record above.'}</p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Department</th>
                  <th>Retention</th>
                  <th>Expiry</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {records.map(r => (
                  <tr key={r.id}>
                    <td>
                      <button
                        style={{ background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600, color: '#2563eb', padding: 0, textAlign: 'left' }}
                        onClick={() => setDetail(r)}
                      >
                        {r.name}
                      </button>
                    </td>
                    <td style={{ color: '#64748b' }}>{r.dataType}</td>
                    <td>{r.department || '—'}</td>
                    <td>{r.retentionYears}y</td>
                    <td style={{ color: '#64748b', fontSize: '.85rem' }}>{r.expiryDate}</td>
                    <td><StatusBadge status={r.status} /></td>
                    <td>
                      <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                        <button className="btn btn-outline btn-sm" onClick={() => { setEditing(r); setModalOpen(true) }}>Edit</button>
                        <button
                          className="btn btn-secondary btn-sm"
                          disabled={analyzing === r.id}
                          onClick={() => handleAnalyze(r.id)}
                        >
                          {analyzing === r.id ? '…' : 'AI'}
                        </button>
                        <button className="btn btn-warning btn-sm" onClick={() => handleDelete(r.id)}>Dispose</button>
                        {isAdmin && (
                          <button className="btn btn-danger btn-sm" onClick={() => handlePermanentDelete(r.id)}>Delete</button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {totalPages > 1 && (
        <div className="pagination">
          <button className="btn btn-secondary btn-sm" disabled={page === 0} onClick={() => setPage(p => p - 1)}>
            ← Prev
          </button>
          <span className="page-info">Page {page + 1} of {totalPages}</span>
          <button className="btn btn-secondary btn-sm" disabled={page >= totalPages - 1} onClick={() => setPage(p => p + 1)}>
            Next →
          </button>
        </div>
      )}

      {modalOpen && (
        <RecordModal
          record={editing}
          onClose={() => { setModalOpen(false); setEditing(null) }}
          onSave={handleSave}
        />
      )}

      {detail && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setDetail(null)}>
          <div className="modal">
            <div className="modal-header">
              <h3>{detail.name}</h3>
              <button className="modal-close" onClick={() => setDetail(null)}>×</button>
            </div>
            <div className="modal-body">
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px 24px', fontSize: '.875rem' }}>
                {[
                  ['Type', detail.dataType],
                  ['Owner', detail.owner],
                  ['Department', detail.department],
                  ['Status', detail.status],
                  ['Retention', `${detail.retentionYears} years`],
                  ['Created', detail.createdDate],
                  ['Expires', detail.expiryDate],
                ].map(([label, value]) => (
                  <div key={label}>
                    <div style={{ color: '#64748b', fontSize: '.78rem', textTransform: 'uppercase', letterSpacing: '.04em' }}>{label}</div>
                    <div style={{ fontWeight: 500, marginTop: 2 }}>
                      {label === 'Status' ? <StatusBadge status={value} /> : value || '—'}
                    </div>
                  </div>
                ))}
              </div>

              {detail.description && (
                <div style={{ marginTop: 14 }}>
                  <div style={{ color: '#64748b', fontSize: '.78rem', textTransform: 'uppercase', letterSpacing: '.04em', marginBottom: 4 }}>Description</div>
                  <p style={{ fontSize: '.875rem' }}>{detail.description}</p>
                </div>
              )}

              {detail.aiDescription && (
                <div className="ai-panel">
                  <strong>AI Analysis</strong>
                  {detail.aiScore != null && (
                    <span className="ai-score">{Math.round(detail.aiScore * 100)}%</span>
                  )}
                  <p style={{ marginTop: 8 }}>{detail.aiDescription}</p>
                </div>
              )}
            </div>
            <div className="modal-footer">
              <button
                className="btn btn-secondary btn-sm"
                disabled={analyzing === detail.id}
                onClick={() => handleAnalyze(detail.id)}
              >
                {analyzing === detail.id ? 'Analyzing…' : 'Run AI Analysis'}
              </button>
              <button className="btn btn-primary btn-sm" onClick={() => { setEditing(detail); setDetail(null); setModalOpen(true) }}>
                Edit
              </button>
              <button className="btn btn-secondary" onClick={() => setDetail(null)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
