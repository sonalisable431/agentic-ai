// Auto-generated HTTP client using axios

import axios, { AxiosRequestConfig } from "axios";

export async function getJson<T = any>(url: string, config: AxiosRequestConfig = {}): Promise<T> {
  const response = await axios.get<T>(url, config);
  return response.data;
}

export async function postJson<T = any>(
  url: string,
  body: any,
  config: AxiosRequestConfig = {}
): Promise<T> {
  const response = await axios.post<T>(url, body, {
    headers: { "Content-Type": "application/json", ...(config.headers || {}) },
    ...config,
  });
  return response.data;
}
