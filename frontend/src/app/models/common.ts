export interface LiveboxResponse<T = unknown> {
  status: T | null;
  data: unknown;
  errors: unknown[];
}

export interface ErrorResponse {
  detail: string;
  code?: number;
}
