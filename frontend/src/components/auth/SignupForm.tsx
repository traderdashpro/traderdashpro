"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "../../contexts/AuthContext";
import { useRouter } from "next/navigation";

interface SignupFormProps {
  onSwitchToLogin: () => void;
}

export const SignupForm: React.FC<SignupFormProps> = ({ onSwitchToLogin }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [signupSuccess, setSignupSuccess] = useState(false);

  const { signup, isAuthenticated } = useAuth();
  const router = useRouter();

  // Redirect to dashboard if user is already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push("/");
    }
  }, [isAuthenticated, router]);

  const validatePassword = (password: string) => {
    const minLength = password.length >= 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumber = /\d/.test(password);

    return {
      isValid: minLength && hasUpperCase && hasLowerCase && hasNumber,
      errors: {
        minLength: !minLength ? "At least 8 characters" : "",
        hasUpperCase: !hasUpperCase ? "One uppercase letter" : "",
        hasLowerCase: !hasLowerCase ? "One lowercase letter" : "",
        hasNumber: !hasNumber ? "One number" : "",
      },
    };
  };

  const passwordValidation = validatePassword(password);
  const passwordsMatch = password === confirmPassword;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!passwordValidation.isValid) {
      setError("Please ensure your password meets all requirements.");
      return;
    }

    if (!passwordsMatch) {
      setError("Passwords do not match.");
      return;
    }

    setIsLoading(true);

    try {
      const response = await signup({ email, password });
      if (response.email_sent) {
        setSignupSuccess(true);
      }
    } catch (err: any) {
      setError(err.message || "Signup failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  if (signupSuccess) {
    return (
      <div className="w-full max-w-md mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="mb-6">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
              <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Check Your Email
            </h2>
            <p className="text-gray-600 mb-4">
              We've sent a confirmation link to <strong>{email}</strong>
            </p>
            <p className="text-sm text-gray-500 mb-6">
              Click the link in your email to verify your account and start using Trading Insights.
            </p>
          </div>
          
          <button
            onClick={() => setSignupSuccess(false)}
            className="w-full bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors mb-4"
          >
            Back to Sign Up
          </button>
          
          <button
            onClick={onSwitchToLogin}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Create Account
          </h2>
          <p className="text-gray-600">
            Join Trading Insights to track your trades
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
              {error}
            </div>
          )}

          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Email Address
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your email"
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Create a password"
            />

            {/* Password requirements */}
            {password && (
              <div className="mt-2 text-sm">
                <p className="text-gray-600 mb-1">Password requirements:</p>
                <ul className="space-y-1">
                  <li
                    className={`flex items-center ${
                      passwordValidation.errors.minLength
                        ? "text-red-600"
                        : "text-green-600"
                    }`}
                  >
                    <span className="mr-2">
                      {passwordValidation.errors.minLength ? "✗" : "✓"}
                    </span>
                    At least 8 characters
                  </li>
                  <li
                    className={`flex items-center ${
                      passwordValidation.errors.hasUpperCase
                        ? "text-red-600"
                        : "text-green-600"
                    }`}
                  >
                    <span className="mr-2">
                      {passwordValidation.errors.hasUpperCase ? "✗" : "✓"}
                    </span>
                    One uppercase letter
                  </li>
                  <li
                    className={`flex items-center ${
                      passwordValidation.errors.hasLowerCase
                        ? "text-red-600"
                        : "text-green-600"
                    }`}
                  >
                    <span className="mr-2">
                      {passwordValidation.errors.hasLowerCase ? "✗" : "✓"}
                    </span>
                    One lowercase letter
                  </li>
                  <li
                    className={`flex items-center ${
                      passwordValidation.errors.hasNumber
                        ? "text-red-600"
                        : "text-green-600"
                    }`}
                  >
                    <span className="mr-2">
                      {passwordValidation.errors.hasNumber ? "✗" : "✓"}
                    </span>
                    One number
                  </li>
                </ul>
              </div>
            )}
          </div>

          <div>
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                confirmPassword && !passwordsMatch
                  ? "border-red-300"
                  : "border-gray-300"
              }`}
              placeholder="Confirm your password"
            />
            {confirmPassword && !passwordsMatch && (
              <p className="mt-1 text-sm text-red-600">
                Passwords do not match
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={
              isLoading || !passwordValidation.isValid || !passwordsMatch
            }
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? "Creating Account..." : "Create Account"}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Already have an account?{" "}
            <button
              onClick={onSwitchToLogin}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Sign in here
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};
