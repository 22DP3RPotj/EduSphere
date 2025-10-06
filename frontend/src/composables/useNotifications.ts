import { useToast } from "vue-toastification";
import type { ApolloError } from "@apollo/client/errors";

type FormErrors = Record<string, string[] | string>;

export function useNotifications() {
  const toast = useToast();

  function extractErrorMessages(error: unknown): string[] {
    const errorMessages: string[] = [];

    if (
      typeof error === "object" &&
      error !== null &&
      "error" in error &&
      typeof (error as { error?: unknown }).error === "string"
    ) {
      errorMessages.push(String((error as { error?: unknown }).error));
      return errorMessages;
    }

    // ApolloError case
    if (
      typeof error === "object" &&
      error !== null &&
      "graphQLErrors" in error &&
      Array.isArray((error as ApolloError).graphQLErrors)
    ) {
      const gqlError = (error as ApolloError).graphQLErrors[0];

      if (gqlError) {
        const formErrors = gqlError.extensions?.errors as FormErrors | undefined;
        if (formErrors) {
          Object.entries(formErrors).forEach(([field, messages]) => {
            if (Array.isArray(messages)) {
              messages.forEach((msg) => errorMessages.push(`${field}: ${msg}`));
            } else if (typeof messages === "string") {
              errorMessages.push(messages);
            }
          });
        }

        if (
          errorMessages.length === 0 &&
          gqlError.message &&
          gqlError.message !== "Invalid data"
        ) {
          try {
            const parsed = JSON.parse(gqlError.message.replace(/'/g, '"'));
            if (Array.isArray(parsed.__all__)) {
              parsed.__all__.forEach((msg: string) => errorMessages.push(msg));
            }
          } catch {
            errorMessages.push(gqlError.message);
          }
        }
      }
    }

    // Fallback case
    if (errorMessages.length === 0) {
      const fallbackMsg =
        (error as Error)?.message || String(error) || "An unexpected error occurred";
      errorMessages.push(fallbackMsg);
    }

    return errorMessages;
  }

  return {
    success: (message: string) => toast.success(message),
    error: (error: unknown) => {
      extractErrorMessages(error).forEach((message) => toast.error(message));
    },
    info: (message: string) => toast.info(message),
    warning: (message: string) => toast.warning(message),
  };
}
