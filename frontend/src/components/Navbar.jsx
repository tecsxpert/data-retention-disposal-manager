import { NavLink, useNavigate } from 'react-router-dom'

export default function Navbar() {
  const navigate = useNavigate()
  const username = localStorage.getItem('username') || 'User'
  const role = localStorage.getItem('role') || ''

  function handleLogout() {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('role')
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <span className="navbar-brand">Data Retention Manager</span>
      <div className="navbar-links">
        <NavLink to="/" end>Dashboard</NavLink>
        <NavLink to="/records">Records</NavLink>
        <span style={{ color: '#94a3b8', fontSize: '.8rem', marginLeft: 8 }}>
          {username}{role === 'ADMIN' && <span style={{ color: '#60a5fa', marginLeft: 4 }}>(admin)</span>}
        </span>
        <button className="navbar-btn" onClick={handleLogout}>Logout</button>
      </div>
    </nav>
  )
}
