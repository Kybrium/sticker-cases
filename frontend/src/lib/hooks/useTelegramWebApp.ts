'use client';

import { TgUser } from '@/types/telegram';
import { useEffect, useState } from 'react';

export function useTelegramWebApp() {
    const [inTelegram, setInTelegram] = useState(false);
    const [user, setUser] = useState<TgUser | undefined>();
    const [initData, setInitData] = useState<string | undefined>();

    useEffect(() => {
        const tg = (window as any)?.Telegram?.WebApp;
        const useMock = process.env.NEXT_PUBLIC_TG_DEV === '1' || new URLSearchParams(window.location.search).has('tgMock');

        if (tg) {
            try { tg.ready?.(); tg.expand?.(); } catch { }
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
                is_dev: true
            });
            setInitData('MOCK_INIT_DATA');
        }
    }, []);

    return { inTelegram, user, initData };
}