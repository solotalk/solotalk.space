import axios from 'axios'
import { reactive } from 'vue'

const STORAGE_KEYS = {
  accessToken: 'solotalk_access_token',
  refreshToken: 'solotalk_refresh_token',
  username: 'solotalk_username',
  isAdmin: 'solotalk_is_admin',
} as const

export interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  username: string | null
  isAdmin: boolean
}

function loadState(): AuthState {
  return {
    accessToken: localStorage.getItem(STORAGE_KEYS.accessToken),
    refreshToken: localStorage.getItem(STORAGE_KEYS.refreshToken),
    username: localStorage.getItem(STORAGE_KEYS.username),
    isAdmin: localStorage.getItem(STORAGE_KEYS.isAdmin) === 'true',
  }
}

export const authState = reactive<AuthState>(loadState())

export function getAccessToken(): string | null {
  return authState.accessToken
}

export function getRefreshToken(): string | null {
  return authState.refreshToken
}

export function setTokens(accessToken: string, refreshToken: string): void {
  authState.accessToken = accessToken
  authState.refreshToken = refreshToken
  localStorage.setItem(STORAGE_KEYS.accessToken, accessToken)
  localStorage.setItem(STORAGE_KEYS.refreshToken, refreshToken)
}

export function setProfile(username: string, isAdmin: boolean): void {
  authState.username = username
  authState.isAdmin = isAdmin
  localStorage.setItem(STORAGE_KEYS.username, username)
  localStorage.setItem(STORAGE_KEYS.isAdmin, String(isAdmin))
}

export function clearAuth(): void {
  authState.accessToken = null
  authState.refreshToken = null
  authState.username = null
  authState.isAdmin = false
  for (const key of Object.values(STORAGE_KEYS)) {
    localStorage.removeItem(key)
  }
}

// Login/register hit the API directly (no auth header / no refresh retry),
// so this module stays free of circular imports with api/client.ts.
export async function login(username: string, password: string): Promise<void> {
  const { data } = await axios.post('/api/auth/login', { username, password })
  setTokens(data.access_token, data.refresh_token)
  setProfile(data.username ?? username, Boolean(data.is_admin))
}

export async function register(username: string, password: string): Promise<void> {
  await axios.post('/api/auth/register', { username, password })
}

export function logout(): void {
  clearAuth()
}
