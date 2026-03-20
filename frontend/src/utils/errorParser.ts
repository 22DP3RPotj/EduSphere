import type { ApolloError } from "@apollo/client/errors"

type ErrorMessage = string | { message?: string, code?: string }
type RawFormError = ErrorMessage | Record<string, unknown> | null | undefined

export type FormErrors = Record<string, RawFormError | RawFormError[]>

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
              result.generalErrors.push(...normalizeMessages(messages))
            } else if (typeof messages === "string") {
              const str = messages.trim()

              // If it looks like a serialized object/array, try to parse and extract strings
              if (str.startsWith("{") || str.startsWith("[")) {
                try {
                  const parsed = JSON.parse(str.replace(/'/g, '"'))

                  // If parsed has __all__, use it
                  const parsedAll = (parsed as { __all__?: unknown }).__all__
                  if (parsedAll !== undefined) {
                    result.generalErrors.push(...normalizeMessages(parsedAll))
                  } else if (typeof parsed === "object" && parsed !== null) {
                    // Flatten any nested string/array values found in the parsed object
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
              result.generalErrors.push(...flatten(messages))
            }
          } else {
            // Field-specific errors
            result.fieldErrors[field] = normalizeMessages(messages)
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
          const parsedAll = (parsed as { __all__?: unknown }).__all__
          if (parsedAll !== undefined) {
            result.generalErrors.push(...normalizeMessages(parsedAll))
          } else if (typeof parsed === "object" && parsed !== null) {
            // Flatten any nested string/array values found in the parsed object
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

function normalizeMessages(messages: unknown): string[] {
  if (Array.isArray(messages)) {
    return messages.map((m) => {
      if (typeof m === "string") return m
      if (typeof m === "object" && m !== null) {
        return pickMessage(m as { message?: unknown, code?: unknown })
      }
      return String(m)
    })
  }

  if (typeof messages === "string") {
    return [messages]
  }

  if (typeof messages === "object" && messages !== null) {
    return [pickMessage(messages as { message?: unknown, code?: unknown })]
  }

  return [String(messages)]
}

function flatten(v: unknown): string[] {
  if (typeof v === "string") return [v]
  if (Array.isArray(v)) return v.flatMap(flatten)
  if (typeof v === "object" && v !== null) {
    if ("message" in v && typeof (v as { message?: unknown }).message === "string") {
      return [(v as { message: string }).message]
    }
    return Object.entries(v)
      .filter(([key]) => key !== "code")
      .flatMap(([, value]) => flatten(value))
  }
  return []
}

function pickMessage(value: { message?: unknown, code?: unknown }): string {
  if (typeof value.message === "string" && value.message.trim()) return value.message
  if (typeof value.code === "string" && value.code.trim()) return value.code
  return JSON.stringify(value)
}
