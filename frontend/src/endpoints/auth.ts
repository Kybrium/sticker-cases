import { BASE_URL } from "@/lib/constants";
import { TelegramLoginResponse } from "@/types/telegram";

export async function TelegramWebAppLogin(initData: string): Promise<TelegramLoginResponse> {
    const res: Response = await fetch(`${BASE_URL}/accounts/telegram-webapp/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ initData }),
        credentials: "include",
    });

    if (!res.ok) throw new Error(`login failed: ${res.status}`)

    return (await res.json()) as TelegramLoginResponse;
}

export async function getMe() {
    const res = await fetch(`${BASE_URL}/auth/me/`, { credentials: 'include' });
    if (res.status === 401) return null;
    if (!res.ok) throw new Error('failed to load me');
    return res.json();
}

export async function logout() {
    const res = await fetch(`${BASE_URL}/auth/logout/`, {
        method: 'POST',
        credentials: 'include',
    });
    if (!res.ok) throw new Error('logout failed');
    return res.json();
}