export async function getHealth(base = process.env.NEXT_PUBLIC_API_URL!) {
    const url = `${base}/healthz/`;
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
    return res.json() as Promise<{ ok: boolean }>;
}