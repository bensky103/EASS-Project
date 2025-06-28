export interface User {
  id: string;
  email: string;
  username: string;
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
}

export interface AuthResponse {
  user: User;
  token: string;
}

export interface UserProfile {
  id: string;
  email: string;
  username: string;
  firstName: string;
  lastName: string;
  bio: string;
  profilePicture?: string;
  joinedDate?: string;
  preferences: {
    darkMode: boolean;
    emailNotifications: boolean;
    pushNotifications: boolean;
  };
}

export interface EditProfileData {
  username: string;
  firstName: string;
  lastName: string;
  bio: string;
} 