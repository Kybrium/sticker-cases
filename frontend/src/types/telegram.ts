declare global {
    interface Window {
        Telegram?: { WebApp?: TgWebApp };
    }
}

export type TgWebApp = {
    ready?: () => void;
    expand?: () => void;
    initData?: string;
    initDataUnsafe?: TgInitDataUnsafe;
};

export type TgUser = {
    id: number;
    is_bot?: boolean;
    first_name?: string;
    last_name?: string;
    username?: string;
    language_code?: string;
    photo_url?: string;
    is_dev?: boolean;
};

export type Result = {
    inTelegram: boolean;
    user?: TgUser;
    initData?: string;
};

export type TelegramLoginResponse = {
    ok: boolean;
    user?: {
        id: number;
        username: string;
        telegram_id: number;
        telegram_username: string;
        first_name: string;
        last_name: string;
        photo_url: string;
    };
};

export type TgInitDataUnsafe = { user?: TgUser };