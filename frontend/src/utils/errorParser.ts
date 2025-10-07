import type { ApolloError } from "@apollo/client/errors"

export type FormErrors = Record<string, string[] | string>

export interface ParsedError {
  fieldErrors: Record<string, string[]>
  generalErrors: string[]
}

export function parseGraphQLError(error: unknown): ParsedError {
  const result: ParsedError = {
    fieldErrors: {},
    generalErrors: [],
  }

  // Simple error object with error field
  if (
    typeof error === "object" &&
    error !== null &&
    "error" in error &&
    typeof (error as { error?: unknown }).error === "string"
  ) {
    result.generalErrors.push(String((error as { error?: unknown }).error))
    return result
  }

  // ApolloError case
  if (
    typeof error === "object" &&
    error !== null &&
    "graphQLErrors" in error &&
    Array.isArray((error as ApolloError).graphQLErrors)
  ) {
    const gqlError = (error as ApolloError).graphQLErrors[0]

    if (gqlError) {
      const formErrors = gqlError.extensions?.errors as FormErrors | undefined

      if (formErrors) {
        Object.entries(formErrors).forEach(([field, messages]) => {
          if (field === "__all__") {
            // General form errors
            if (Array.isArray(messages)) {
              result.generalErrors.push(...messages)
            } else if (typeof messages === "string") {
              result.generalErrors.push(messages)
            }
          } else {
            // Field-specific errors
            if (Array.isArray(messages)) {
              result.fieldErrors[field] = messages
            } else if (typeof messages === "string") {
              result.fieldErrors[field] = [messages]
            }
          }
        })
      }

      // Try parsing message as JSON for __all__ errors
      if (
        result.generalErrors.length === 0 &&
        Object.keys(result.fieldErrors).length === 0 &&
        gqlError.message &&
        gqlError.message !== "Invalid data"
      ) {
        try {
          const parsed = JSON.parse(gqlError.message.replace(/'/g, '"'))
          if (Array.isArray(parsed.__all__)) {
            result.generalErrors.push(...parsed.__all__)
          }
        } catch {
          result.generalErrors.push(gqlError.message)
        }
      }
    }
  }

  // Fallback case
  if (result.generalErrors.length === 0 && Object.keys(result.fieldErrors).length === 0) {
    const fallbackMsg = (error as Error)?.message || String(error) || "An unexpected error occurred"
    result.generalErrors.push(fallbackMsg)
  }

  return result
}
