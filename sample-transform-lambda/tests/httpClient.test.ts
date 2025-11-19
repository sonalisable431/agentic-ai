import axios from "axios";
import { getJson, postJson } from "../src/core/httpClient";

jest.mock("axios");
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe("httpClient", () => {
  it("getJson calls axios.get and returns data", async () => {
    mockedAxios.get.mockResolvedValueOnce({ data: { ok: true } } as any);
    const result = await getJson("https://example.com");
    expect(mockedAxios.get).toHaveBeenCalled();
    expect(result).toEqual({ ok: true });
  });

  it("postJson calls axios.post and returns data", async () => {
    mockedAxios.post.mockResolvedValueOnce({ data: { created: true } } as any);
    const result = await postJson("https://example.com", { a: 1 });
    expect(mockedAxios.post).toHaveBeenCalled();
    expect(result).toEqual({ created: true });
  });
});
