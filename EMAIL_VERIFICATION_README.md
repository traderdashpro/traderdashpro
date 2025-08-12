# Email Verification Feature

The email verification feature has been enabled for the Trading Insights application. This document explains how it works and how to test it.

## Overview

Previously, new users were automatically marked as verified and could log in immediately after signup. Now, users must verify their email address before they can access the application.

## How It Works

### 1. User Signup
- User fills out the signup form with email and password
- System creates user account with `is_confirmed = False`
- System generates a unique confirmation token
- System sends confirmation email to user's email address
- User sees success message asking them to check their email

### 2. Email Confirmation
- User receives email with confirmation link
- Link contains the confirmation token
- User clicks the link, which takes them to `/confirm-email?token=<token>`
- Frontend calls the backend `/api/auth/confirm-email` endpoint
- Backend verifies token and marks user as confirmed
- User is redirected to login page

### 3. User Login
- User attempts to login with email/password
- If email is not confirmed, login is blocked with error message
- If email is confirmed, login proceeds normally

## Backend Changes

### Files Modified:
- `backend/routes/auth.py` - Enabled email verification checks
- `backend/env.example` - Added email configuration variables
- `backend/utils/auth_utils.py` - Email sending functionality (already existed)

### Key Changes:
1. **Signup Route**: 
   - Users created with `is_confirmed = False`
   - Confirmation email is sent
   - No auto-login after signup

2. **Login Route**: 
   - Checks `is_confirmed` status
   - Blocks login if email not confirmed
   - Returns `email_not_confirmed` error

3. **Email Configuration**: 
   - Added SMTP configuration variables
   - Uses Gmail SMTP by default

## Frontend Changes

### Files Modified:
- `frontend/src/app/confirm-email/page.tsx` - New email confirmation page
- `frontend/src/components/auth/SignupForm.tsx` - Updated to show email verification message
- `frontend/src/components/auth/LoginForm.tsx` - Added resend confirmation option
- `frontend/src/lib/api.ts` - Added email confirmation API methods
- `frontend/src/types/index.ts` - Updated types for email verification

### Key Changes:
1. **Signup Flow**: 
   - Shows success message after signup
   - Instructs user to check email
   - No automatic redirect to dashboard

2. **Email Confirmation Page**: 
   - Handles confirmation token from URL
   - Shows loading, success, or error states
   - Redirects to login after successful confirmation

3. **Login Flow**: 
   - Shows helpful message if email not confirmed
   - Provides option to resend confirmation email

## Configuration

### Backend Environment Variables
Add these to your `backend/.env` file:

```bash
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password_here
MAIL_DEFAULT_SENDER=your_email@gmail.com

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here
```

### Gmail Setup
To use Gmail for sending emails:

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use the generated password as `MAIL_PASSWORD`

## Testing the Feature

### 1. Start the Backend
```bash
cd backend
source venv/bin/activate
python app.py
```

### 2. Start the Frontend
```bash
cd frontend
npm run dev
```

### 3. Test the Flow
1. Go to `http://localhost:3000`
2. Click "Sign Up"
3. Fill out the form with a new email
4. Submit the form
5. You should see the "Check Your Email" message
6. Try to login - it should be blocked
7. Check your email for the confirmation link
8. Click the confirmation link
9. Try to login again - it should work now

### 4. Test with Backend Script
```bash
cd backend
source venv/bin/activate
python test_email_verification.py
```

## Troubleshooting

### Email Not Sending
- Check your email configuration in `.env`
- Verify Gmail app password is correct
- Check that 2FA is enabled on Gmail
- Check backend logs for email errors

### Confirmation Token Issues
- Tokens are stored in the database
- Check the `users` table for `confirmation_token` values
- Tokens are UUIDs and should be unique

### Frontend Issues
- Make sure the frontend is pointing to the correct backend URL
- Check browser console for API errors
- Verify that all TypeScript types are correct

## Security Considerations

1. **Token Expiration**: Currently, confirmation tokens don't expire. Consider adding expiration for production.
2. **Rate Limiting**: Consider adding rate limiting for signup and confirmation endpoints.
3. **Email Validation**: The system validates email format but doesn't verify email existence.
4. **Token Storage**: Confirmation tokens are stored in plain text in the database.

## Future Enhancements

1. **Token Expiration**: Add expiration time to confirmation tokens
2. **Email Templates**: Improve email design and branding
3. **Resend Limits**: Limit how often users can request new confirmation emails
4. **Email Verification**: Add actual email existence verification
5. **Welcome Email**: Send welcome email after successful confirmation 