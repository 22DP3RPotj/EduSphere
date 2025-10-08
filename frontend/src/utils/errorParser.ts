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
              const str = messages.trim()

              // If it looks like a serialized object/array, try to parse and extract strings
              if (str.startsWith("{") || str.startsWith("[")) {
                try {
                  const parsed = JSON.parse(str.replace(/'/g, '"'))

                  // If parsed has __all__, use it
                  if (Array.isArray((parsed as any).__all__)) {
                    result.generalErrors.push(...(parsed as any).__all__)
                  } else if (typeof parsed === "object" && parsed !== null) {
                    // Flatten any nested string/array values found in the parsed object
                    const flatten = (v: unknown): string[] => {
                      if (typeof v === "string") return [v]
                      if (Array.isArray(v)) return v.flatMap(flatten)
                      if (typeof v === "object" && v !== null) return Object.values(v).flatMap(flatten)
                      return []
                    }
                    const vals = flatten(parsed)
                    if (vals.length > 0) result.generalErrors.push(...vals)
                    else result.generalErrors.push(messages) // fallback to raw string
                  } else {
                    result.generalErrors.push(messages)
                  }
                } catch {
                  // If parsing fails, keep the original string
                  result.generalErrors.push(messages)
                }
              } else {
                result.generalErrors.push(messages)
              }
            } else if (typeof messages === "object" && messages !== null) {
              // message is an object/hashmap directly
              result.generalErrors.push(...Object.values(messages).map(String))
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

      // Try parsing message as JSON for __all__ errors (and also handle objects keyed by field)
      if (
        result.generalErrors.length === 0 &&
        Object.keys(result.fieldErrors).length === 0 &&
        gqlError.message &&
        gqlError.message !== "Invalid data"
      ) {
        try {
          const parsed = JSON.parse(gqlError.message.replace(/'/g, '"'))
          if (Array.isArray((parsed as any).__all__)) {
            result.generalErrors.push(...(parsed as any).__all__)
          } else if (typeof parsed === "object" && parsed !== null) {
            // Flatten any nested string/array values found in the parsed object
            const flatten = (v: unknown): string[] => {
              if (typeof v === "string") return [v]
              if (Array.isArray(v)) return v.flatMap(flatten)
              if (typeof v === "object" && v !== null) return Object.values(v).flatMap(flatten)
              return []
            }
            const vals = flatten(parsed)
            if (vals.length > 0) result.generalErrors.push(...vals)
            else result.generalErrors.push(gqlError.message)
          } else {
            result.generalErrors.push(gqlError.message)
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
