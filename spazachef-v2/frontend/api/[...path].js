// Same-origin API proxy. Keeps Vercel deployment-protection credentials server-side.
export default async function handler(req, res) {
  const upstreamBase = process.env.API_UPSTREAM_URL;
  const bypassSecret = process.env.API_PROTECTION_BYPASS_SECRET;

  if (!upstreamBase || !bypassSecret) {
    return res.status(503).json({ detail: "API proxy is not configured." });
  }

  try {
    const requestUrl = req.url || "";
    if (!requestUrl.startsWith("/api/") && requestUrl !== "/api") {
      return res.status(404).json({ detail: "Not found." });
    }

    const base = new URL(upstreamBase);
    const target = new URL(requestUrl, base);
    if (target.origin !== base.origin || !target.pathname.startsWith("/api")) {
      return res.status(400).json({ detail: "Invalid API route." });
    }

    const headers = new Headers();
    const authorization = req.headers.authorization;
    const contentType = req.headers["content-type"];
    const accept = req.headers.accept;
    if (authorization) headers.set("authorization", authorization);
    if (contentType) headers.set("content-type", contentType);
    if (accept) headers.set("accept", accept);
    headers.set("x-vercel-protection-bypass", bypassSecret);

    const hasBody = !["GET", "HEAD"].includes((req.method || "GET").toUpperCase());
    const body = hasBody
      ? (typeof req.body === "string" ? req.body : JSON.stringify(req.body ?? {}))
      : undefined;

    const response = await fetch(target, {
      method: req.method || "GET",
      headers,
      body,
      redirect: "manual",
    });

    res.status(response.status);
    res.setHeader("cache-control", "no-store");
    for (const name of ["content-type", "retry-after", "www-authenticate"]) {
      const value = response.headers.get(name);
      if (value) res.setHeader(name, value);
    }
    const payload = Buffer.from(await response.arrayBuffer());
    return res.send(payload);
  } catch (error) {
    console.error("SpazaChef API proxy failed:", error);
    return res.status(502).json({ detail: "The API service is temporarily unavailable." });
  }
}
