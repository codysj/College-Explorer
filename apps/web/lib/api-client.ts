import { getApiBaseUrl } from "@/lib/env";

export type ApiErrorBody = {
  error?: {
    code?: string;
    message?: string;
  };
};

export class ApiClientError extends Error {
  readonly status: number;
  readonly code?: string;
  readonly body?: unknown;

  constructor(message: string, status: number, code?: string, body?: unknown) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.code = code;
    this.body = body;
  }
}

type ApiFetchOptions = Omit<RequestInit, "body"> & {
  body?: BodyInit | Record<string, unknown> | null;
};

export async function apiFetch<TResponse>(
  path: `/${string}`,
  options: ApiFetchOptions = {},
): Promise<TResponse> {
  const { body, headers, ...init } = options;
  const requestHeaders = new Headers(headers);

  let requestBody: BodyInit | null | undefined = body as BodyInit | null | undefined;
  if (body && typeof body === "object" && !(body instanceof FormData) && !(body instanceof URLSearchParams)) {
    requestHeaders.set("Content-Type", "application/json");
    requestBody = JSON.stringify(body);
  }

  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    body: requestBody,
    headers: requestHeaders,
  });

  const contentType = response.headers.get("content-type") ?? "";
  const responseBody: unknown = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const parsed = responseBody as ApiErrorBody;
    throw new ApiClientError(
      parsed.error?.message ?? `API request failed with status ${response.status}.`,
      response.status,
      parsed.error?.code,
      responseBody,
    );
  }

  return responseBody as TResponse;
}
