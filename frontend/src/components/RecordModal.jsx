import { useState, useEffect } from 'react'

const EMPTY_FORM = {
  name: '', description: '', dataType: '', owner: '',
  department: '', retentionYears: '', createdDate: '',
}

export default function RecordModal({ record, onClose, onSave }) {
  const [form, setForm] = useState(EMPTY_FORM)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (record) {
      setForm({
        name: record.name || '',
        description: record.description || '',
        dataType: record.dataType || '',
        owner: record.owner || '',
        department: record.department || '',
        retentionYears: record.retentionYears ?? '',
        createdDate: record.createdDate || '',
      })
    } else {
      setForm(EMPTY_FORM)
    }
  }, [record])

  function handleChange(e) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSaving(true)
    try {
      await onSave({ ...form, retentionYears: Number(form.retentionYears) })
    } catch (err) {
      setError(err.response?.data?.message || err.response?.data?.error || 'Failed to save record')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <h3>{record ? 'Edit Record' : 'New Record'}</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && <div className="alert alert-error">{error}</div>}

            <div className="form-group">
              <label>Name *</label>
              <input className="form-control" name="name" value={form.name} onChange={handleChange} required maxLength={200} />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Data Type *</label>
                <input className="form-control" name="dataType" value={form.dataType} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label>Department</label>
                <input className="form-control" name="department" value={form.department} onChange={handleChange} />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Owner</label>
                <input className="form-control" name="owner" value={form.owner} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label>Retention (years) *</label>
                <input className="form-control" name="retentionYears" type="number" min={1} max={100} value={form.retentionYears} onChange={handleChange} required />
              </div>
            </div>

            <div className="form-group">
              <label>Created Date *</label>
              <input className="form-control" name="createdDate" type="date" value={form.createdDate} onChange={handleChange} required />
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea className="form-control" name="description" value={form.description} onChange={handleChange} rows={3} maxLength={2000} style={{ resize: 'vertical' }} />
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving…' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
