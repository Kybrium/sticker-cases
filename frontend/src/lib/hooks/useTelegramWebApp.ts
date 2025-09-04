'use client';

import { useEffect, useState } from 'react';
import type { TgUser } from '@/types/telegram';

export function useTelegramWebApp() {
    const [inTelegram, setInTelegram] = useState(false);
    const [user, setUser] = useState<TgUser | undefined>();
    const [initData, setInitData] = useState<string | undefined>();

    useEffect(() => {
        // Guard for SSR and test environments
        if (typeof window === 'undefined') return;

        const tg = window.Telegram?.WebApp;
        const qs = typeof window !== 'undefined' ? window.location.search : '';
        const useMock =
            process.env.NEXT_PUBLIC_TG_DEV === '1' ||
            new URLSearchParams(qs).has('tgMock');

        if (tg) {
            try {
                tg.ready?.();
                tg.expand?.();
            } catch {
                // no-op
            }
            setInTelegram(true);
            setUser(tg.initDataUnsafe?.user);
            setInitData(tg.initData);
            return;
        }

        if (useMock) {
            setInTelegram(false);
            setUser({
                id: 123456789,
                username: 'dev_tester',
                first_name: 'Dev',
                last_name: 'Tester',
                language_code: 'en',
                is_dev: true,
            });
            setInitData('MOCK_INIT_DATA');
        }
    }, []);

    return { inTelegram, user, initData };
}