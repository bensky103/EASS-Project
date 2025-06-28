export interface LoginRequest {
  identifier: string // username or email
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  confirmPassword: string
  firstName?: string
  lastName?: string
}

export interface User {
  id: string
  username: string
  email: string
  firstName?: string
  lastName?: string
  createdAt: string
}

export interface AuthResponse {
  access_token: string;
}

// Always use relative paths for Vite proxy
const API_BASE_URL = '';

// Helper function to handle API requests with proper error handling
const apiRequest = async (url: string, options: RequestInit = {}) => {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "Network error" }))
    throw new Error(error.message || `HTTP ${response.status}: ${response.statusText}`)
  }

  return response.json()
}

export const authApi = {
  async login(identifier: string, password: string): Promise<AuthResponse> {
    return apiRequest("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: identifier, password }),
    });
  },

  async register(userData: RegisterRequest): Promise<{ id: string; email: string; username: string }> {
    return apiRequest("/auth/register", {
      method: "POST",
      body: JSON.stringify(userData),
    });
  },

  async verifyToken(token: string): Promise<User> {
    const data = await apiRequest("/auth/verify", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
    return data.user
  },

  async updatePassword(currentPassword: string, newPassword: string): Promise<void> {
    const token = localStorage.getItem("token")
    if (!token) {
      throw new Error("No authentication token found")
    }

    await apiRequest("/auth/change-password", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ currentPassword, newPassword }),
    })
  },

  async refreshToken(): Promise<AuthResponse> {
    const token = localStorage.getItem("token")
    if (!token) {
      throw new Error("No authentication token found")
    }

    return apiRequest("/auth/refresh", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  },

  async fetchUserProfile(): Promise<any> {
    const token = localStorage.getItem("token")
    if (!token) throw new Error("No authentication token found")
    return apiRequest("/user/profile", {
      headers: { Authorization: `Bearer ${token}` },
    })
  },

  async updateUserProfile(data: any): Promise<any> {
    const token = localStorage.getItem("token")
    if (!token) throw new Error("No authentication token found")
    return apiRequest("/user/profile", {
      method: "PUT",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify(data),
    })
  },
}
