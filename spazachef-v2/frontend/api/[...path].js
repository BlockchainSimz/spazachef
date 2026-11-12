// Server-side proxy keeps Vercel deployment-protection credentials out of the browser.
export default async function handler(req, res) {
  const upstreamUrl = process.env.API_UPSTREAM_URL;
  const bypassSecret = process.env.API_PROTECTION_BYPASS_SECRET;

  if (!upstreamUrl || !bypassSecret) {
    return res.status(503).json({ detail: "API proxy is not configured." });
  }

  const requestPath = req.url || "";
  if (!requestPath.startsWith("/api/")) {
    return res.status(404).json({ detail: "Not found." });
  }

  try {
    const upstream = new URL(upstreamUrl);
    const target = new URL(requestPath, upstream);
    if (target.origin !== upstream.origin || !target.pathname.startsWith("/api/")) {
      return res.status(400).json({ detail: "Invalid API route." });
    }

    const headers = new Headers();
    for (const name of ["authorization", "content-type", "accept"]) {
      const value = req.headers[name];
      if (typeof value === "string") headers.set(name, value);
    }
    headers.set("x-vercel-protection-bypass", bypassSecret);

    const method = (req.method || "GET").toUpperCase();
    const body = ["GET", "HEAD"].includes(method)
      ? undefined
      : (typeof req.body === "string" ? req.body : JSON.stringify(req.body ?? {}));

    const response = await fetch(target, { method, headers, body, redirect: "manual" });
    res.status(response.status);
    res.setHeader("cache-control", "no-store");
    for (const name of ["content-type", "retry-after", "www-authenticate"]) {
      const value = response.headers.get(name);
      if (value) res.setHeader(name, value);
    }
    return res.send(Buffer.from(await response.arrayBuffer()));
  } catch (error) {
    console.error("SpazaChef API proxy failed:", error);
    return res.status(502).json({ detail: "The API service is temporarily unavailable." });
  }
}
