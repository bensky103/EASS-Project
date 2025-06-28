"use client";

import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { Eye, EyeOff, Mail, Lock } from "lucide-react";
import { useAuth } from "@/features/auth/context/AuthContext";

// Utility for className merging (optional, can be replaced with clsx or similar)
function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(" ");
}

// Input Component
const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(
  ({ className, type, ...props }, ref) => (
    <input
      type={type}
      className={cn(
        "flex h-9 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground shadow-sm shadow-black/5 transition-shadow placeholder:text-muted-foreground/70 focus-visible:border-ring focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/20 disabled:cursor-not-allowed disabled:opacity-50",
        type === "search" && "[&::-webkit-search-cancel-button]:appearance-none [&::-webkit-search-decoration]:appearance-none [&::-webkit-search-results-button]:appearance-none [&::-webkit-search-results-decoration]:appearance-none",
        type === "file" && "p-0 pr-3 italic text-muted-foreground/70 file:me-3 file:h-full file:border-0 file:border-r file:border-solid file:border-input file:bg-transparent file:px-3 file:text-sm file:font-medium file:not-italic file:text-foreground",
        className
      )}
      ref={ref}
      {...props}
    />
  )
);
Input.displayName = "Input";

// Button Component
const Button = React.forwardRef<HTMLButtonElement, React.ButtonHTMLAttributes<HTMLButtonElement> & { loading?: boolean }>(
  ({ className, loading, children, ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        "flex justify-center items-center gap-1 px-4 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 disabled:opacity-50 transition-all w-full",
        className
      )}
      disabled={props.disabled || loading}
      {...props}
    >
      {loading && (
        <svg className="animate-spin h-5 w-5 mr-2 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
        </svg>
      )}
      {children}
    </button>
  )
);
Button.displayName = "Button";

// Validation Schema
const loginSchema = yup.object().shape({
  email: yup.string().email("Please enter a valid email address").required("Email is required"),
  password: yup.string().min(6, "Password must be at least 6 characters").required("Password is required"),
});

interface LoginFormData {
  email: string;
  password: string;
}

const LoginForm: React.FC = () => {
  const { login, isLoading } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
    clearErrors,
  } = useForm<LoginFormData>({
    resolver: yupResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setAuthError(null);
    clearErrors();
    try {
      await login(data.email, data.password);
    } catch (error: any) {
      setAuthError(error?.message || "Login failed");
      setError("root", { type: "manual", message: error?.message || "Login failed" });
    }
  };

  return (
    <div className="w-full max-w-md bg-white dark:bg-zinc-900 rounded-xl shadow-lg border border-zinc-200 dark:border-zinc-800 p-8 mx-auto">
      <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-blue-100 dark:bg-blue-900 mb-6 mx-auto">
        <Mail className="w-7 h-7 text-blue-600 dark:text-blue-300" />
      </div>
      <h2 className="text-2xl font-semibold mb-2 text-center text-zinc-900 dark:text-zinc-100">Sign in to your account</h2>
      <p className="text-zinc-500 dark:text-zinc-400 text-sm mb-6 text-center">Enter your credentials to access your account</p>
      {authError && (
        <div className="mb-4 p-3 rounded-lg bg-red-100 dark:bg-red-900 border border-red-200 dark:border-red-800">
          <p className="text-sm text-red-700 dark:text-red-200">{authError}</p>
        </div>
      )}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="space-y-2">
          <label htmlFor="email" className="text-sm font-medium text-zinc-900 dark:text-zinc-100">Email Address</label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400 dark:text-zinc-500" />
            <Input
              {...register("email")}
              id="email"
              type="email"
              placeholder="Enter your email"
              className={cn("pl-10", errors.email && "border-red-500 focus-visible:ring-red-200")}
              disabled={isLoading || isSubmitting}
              autoComplete="username"
            />
          </div>
          {errors.email && <p className="text-sm text-red-600 dark:text-red-400">{errors.email.message}</p>}
        </div>
        <div className="space-y-2">
          <label htmlFor="password" className="text-sm font-medium text-zinc-900 dark:text-zinc-100">Password</label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400 dark:text-zinc-500" />
            <Input
              {...register("password")}
              id="password"
              type={showPassword ? "text" : "password"}
              placeholder="Enter your password"
              className={cn("pl-10 pr-10", errors.password && "border-red-500 focus-visible:ring-red-200")}
              disabled={isLoading || isSubmitting}
              autoComplete="current-password"
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 dark:text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300 transition-colors"
              tabIndex={-1}
              disabled={isLoading || isSubmitting}
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          {errors.password && <p className="text-sm text-red-600 dark:text-red-400">{errors.password.message}</p>}
        </div>
        <Button type="submit" loading={isLoading || isSubmitting} disabled={isLoading || isSubmitting}>
          {isLoading || isSubmitting ? "Signing in..." : "Sign In"}
        </Button>
        {errors.root && <p className="text-sm text-red-600 dark:text-red-400 text-center">{errors.root.message}</p>}
      </form>
    </div>
  );
};

export default LoginForm; 