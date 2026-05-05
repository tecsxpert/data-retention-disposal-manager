import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// Attach JWT token to every request
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Redirect to login on 401
api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const authApi = {
  login: (username, password) =>
    api.post('/auth/login', { username, password }),
  register: (username, email, password) =>
    api.post('/auth/register', { username, email, password }),
}

export const recordsApi = {
  getAll: (page = 0, size = 10, sortBy = 'createdAt', direction = 'desc') =>
    api.get('/records', { params: { page, size, sortBy, direction } }),
  getById: id => api.get(`/records/${id}`),
  create: data => api.post('/records', data),
  update: (id, data) => api.put(`/records/${id}`, data),
  delete: id => api.delete(`/records/${id}`),
  permanentDelete: id => api.delete(`/records/${id}/permanent`),
  search: (q, page = 0, size = 10) =>
    api.get('/records/search', { params: { q, page, size } }),
  getStats: () => api.get('/records/stats'),
  exportCsv: () =>
    api.get('/records/export', { responseType: 'blob' }),
  analyze: id => api.post(`/records/${id}/analyze`),
}
