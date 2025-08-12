"use client";

import React, { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { CheckCircle, XCircle, Loader2 } from "lucide-react";
import { apiClient } from "@/lib/api";

export default function ConfirmEmailPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading"
  );
  const [message, setMessage] = useState("");

  useEffect(() => {
    const confirmEmail = async () => {
      const token = searchParams.get("token");
      console.log("Email confirmation page loaded with token:", token);

      if (!token) {
        setStatus("error");
        setMessage("No confirmation token provided");
        return;
      }

      try {
        console.log("Calling confirmEmail API with token:", token);
        const response = await apiClient.confirmEmail(token);
        console.log("API response:", response);

        if (response.message && response.message.includes("successfully")) {
          setStatus("success");
          setMessage("Email confirmed successfully! You can now log in.");
          // Redirect to login after 3 seconds
          setTimeout(() => {
            router.push("/auth");
          }, 3000);
        } else {
          setStatus("error");
          setMessage(response.message || "Failed to confirm email");
        }
      } catch (error: any) {
        console.error("Email confirmation error:", error);
        setStatus("error");
        setMessage(
          error.message || "An error occurred while confirming your email"
        );
      }
    };

    confirmEmail();
  }, [searchParams, router]);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          {status === "loading" && (
            <>
              <Loader2 className="h-16 w-16 text-primary-600 mx-auto mb-4 animate-spin" />
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Confirming Your Email
              </h1>
              <p className="text-gray-600">
                Please wait while we verify your email address...
              </p>
            </>
          )}

          {status === "success" && (
            <>
              <CheckCircle className="h-16 w-16 text-success-500 mx-auto mb-4" />
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Email Confirmed!
              </h1>
              <p className="text-gray-600 mb-4">{message}</p>
              <p className="text-sm text-gray-500">
                Redirecting to login page...
              </p>
            </>
          )}

          {status === "error" && (
            <>
              <XCircle className="h-16 w-16 text-danger-500 mx-auto mb-4" />
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Confirmation Failed
              </h1>
              <p className="text-gray-600 mb-6">{message}</p>
              <button
                onClick={() => router.push("/auth")}
                className="btn-primary w-full"
              >
                Go to Login
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
