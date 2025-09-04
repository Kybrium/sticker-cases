'use client';

import { useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useTelegramWebApp } from '@/lib/hooks/useTelegramWebApp';
import { getMe, TelegramWebAppLogin, logout } from '@/endpoints/auth';

export default function TelegramUserCard() {
    const qc = useQueryClient();
    const { inTelegram, user: tgUser, initData } = useTelegramWebApp();

    const meQuery = useQuery({
        queryKey: ['me'],
        queryFn: getMe,
        retry: false,
        refetchOnWindowFocus: false,
        staleTime: 30_000,
    });

    const loginMutation = useMutation({
        mutationFn: (data: string) => TelegramWebAppLogin(data),
        onSuccess: () => qc.invalidateQueries({ queryKey: ['me'] }),
    });

    // Auto-login if inside Telegram (or mock) and no session yet
    useEffect(() => {
        if (!initData) return;
        if (meQuery.isLoading) return;
        if (tgUser?.is_dev) return;
        const notLoggedIn = !meQuery.data;
        if (notLoggedIn && !loginMutation.isPending && !loginMutation.isSuccess) {
            loginMutation.mutate(initData);
        }
    }, [initData, meQuery.isLoading, meQuery.data, loginMutation, tgUser?.is_dev]);

    const onLogout = async () => {
        await logout();
        qc.invalidateQueries({ queryKey: ['me'] });
    };

    return (
        <div className="max-w-md w-full rounded-2xl shadow p-6 border">
            <h2 className="text-xl font-bold mb-3">Telegram Web App</h2>

            <p className="text-sm mb-2">
                Context: <span className="font-mono">{inTelegram ? 'inside Telegram' : 'browser'}</span>
            </p>

            <div className="text-sm mb-3">
                <b>Frontend sees:</b>{' '}
                {tgUser ? `@${tgUser.username || '—'} (${tgUser.id})` : '—'}
            </div>

            <div className="text-sm">
                <b>Backend session /auth/me:</b>{' '}
                {meQuery.isLoading ? 'loading…' :
                    meQuery.data ? `user #${meQuery.data.id}` : 'not logged in'}
            </div>

            <div className="text-xs opacity-70 mt-2">
                {loginMutation.isPending && 'Logging in…'}
                {loginMutation.isError && 'Login failed'}
            </div>

            <div className="mt-4 flex gap-2">
                <button
                    className="px-3 py-1 rounded border hover:bg-gray-100"
                    onClick={() => initData && loginMutation.mutate(initData)}
                    disabled={!initData || loginMutation.isPending}
                >
                    Login now
                </button>

                <button className="px-3 py-1 rounded border hover:bg-gray-100" onClick={onLogout}>
                    Logout
                </button>
            </div>
        </div>
    );
}