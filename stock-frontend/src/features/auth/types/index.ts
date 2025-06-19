export interface User {
  id: string;
  email: string;
  // Add more user fields as needed
}

export interface AuthTokenPayload {
  userId: string;
  email: string;
  exp: number;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  isLoading: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  confirmPassword: string;
}

export interface AuthResponse {
  user: User;
  token: string;
} 