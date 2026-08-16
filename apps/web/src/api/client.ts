import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'

import { clearAuth, getAccessToken, getRefreshToken, setTokens } from '../stores/auth'

const client = axios.create({
  baseURL: '/api',
})

client.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// In-flight refresh promise so concurrent 401s share a single refresh call.
let refreshing: Promise<string | null> | null = null

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) {
    return null
  }
  try {
    const { data } = await axios.post('/api/auth/refresh', {
      refresh_token: refreshToken,
    })
    setTokens(data.access_token, data.refresh_token ?? refreshToken)
    return data.access_token as string
  } catch {
    clearAuth()
    window.location.href = '/login'
    return null
  }
}

client.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as
      | (InternalAxiosRequestConfig & { _retry?: boolean })
      | undefined
    if (error.response?.status === 401 && original && !original._retry) {
      original._retry = true
      refreshing ??= refreshAccessToken().finally(() => {
        refreshing = null
      })
      const token = await refreshing
      if (token) {
        original.headers.Authorization = `Bearer ${token}`
        return client(original)
      }
    }
    return Promise.reject(error)
  },
)

export default client
