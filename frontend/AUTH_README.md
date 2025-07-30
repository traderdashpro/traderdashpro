# Frontend Authentication System

## Overview

The frontend authentication system provides a complete user authentication experience with login, signup, and protected routes.

## Features

- ✅ **User Registration** - Email/password signup with validation
- ✅ **User Login** - Secure authentication with JWT tokens
- ✅ **Protected Routes** - Automatic redirection for unauthenticated users
- ✅ **User Menu** - Profile dropdown with logout functionality
- ✅ **Persistent Sessions** - Tokens stored in localStorage
- ✅ **Loading States** - Smooth UX during authentication operations
- ✅ **Error Handling** - User-friendly error messages
- ✅ **Password Validation** - Real-time password strength checking

## Components

### Core Components

1. **AuthProvider** (`contexts/AuthContext.tsx`)

   - Manages global authentication state
   - Provides login, signup, and logout functions
   - Handles token persistence

2. **ProtectedRoute** (`components/auth/ProtectedRoute.tsx`)

   - Wraps protected content
   - Redirects to login if not authenticated
   - Shows loading state during auth check

3. **AuthPage** (`components/auth/AuthPage.tsx`)
   - Main authentication page
   - Switches between login and signup forms

### Form Components

4. **LoginForm** (`components/auth/LoginForm.tsx`)

   - Email/password login
   - Error handling and loading states
   - Link to signup

5. **SignupForm** (`components/auth/SignupForm.tsx`)

   - Email/password registration
   - Real-time password validation
   - Password confirmation
   - Link to login

6. **UserMenu** (`components/auth/UserMenu.tsx`)
   - User profile dropdown
   - Logout functionality
   - User email display

## API Integration

### Authentication Endpoints

- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info

### Token Management

- JWT tokens are automatically included in API requests
- Tokens are stored in localStorage for persistence
- Invalid tokens are automatically cleared

## Usage

### Basic Setup

1. **Wrap your app with AuthProvider** (already done in `layout.tsx`):

```tsx
<AuthProvider>
  <YourApp />
</AuthProvider>
```

2. **Protect routes** (already done in `page.tsx`):

```tsx
<ProtectedRoute>
  <YourProtectedContent />
</ProtectedRoute>
```

### Using Authentication in Components

```tsx
import { useAuth } from "@/contexts/AuthContext";

function MyComponent() {
  const { user, login, logout, isAuthenticated } = useAuth();

  // Access user data
  console.log(user?.email);

  // Check authentication status
  if (isAuthenticated) {
    // User is logged in
  }
}
```

## Styling

The authentication components use Tailwind CSS with:

- Modern, clean design
- Responsive layout
- Consistent color scheme
- Loading states and animations
- Error message styling

## Security Features

- **Password Requirements**: Minimum 8 chars, uppercase, lowercase, number
- **Email Validation**: Proper email format checking
- **Token Expiration**: JWT tokens expire after 1 hour
- **Secure Storage**: Tokens stored in localStorage (consider httpOnly cookies for production)
- **Automatic Logout**: Invalid tokens trigger automatic logout

## Development Notes

- Email confirmation is currently disabled for easier testing
- All API calls include authentication headers automatically
- Error messages are user-friendly and actionable
- Loading states prevent multiple submissions

## Future Enhancements

- [ ] Email confirmation flow
- [ ] Password reset functionality
- [ ] Remember me option
- [ ] Two-factor authentication
- [ ] Social login (Google, GitHub)
- [ ] Account settings page
- [ ] Session management
