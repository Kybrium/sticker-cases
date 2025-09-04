import { defineConfig } from "vitest/config";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig({
    plugins: [tsconfigPaths()],
    test: {
        environment: "jsdom",
        globals: true,
        setupFiles: ["./tests/setup.ts"],
        include: ["**/__tests__/**/*.{test,spec}.{js,jsx,ts,tsx}"],
        coverage: {
            provider: "v8",
            all: false,
            include: ["src/**/*.{ts,tsx}"],
            reporter: ["text", "lcov"],
            thresholds: {
                lines: 20,
                functions: 20,
                branches: 10,
                statements: 20,
            },
            exclude: [
                '**/*.test.{ts,tsx}',
                '**/__tests__/**',
                'src/types/**',
                'src/**/*.d.ts',
                'src/**/index.{ts,tsx}',
                "next.config.*",
                "postcss.config.*",
                "tailwind.config.*",
                "src/app/**/layout.tsx",
                "src/app/**/page.tsx",
                'src/components/auth/**',
                'src/lib/hooks/**',
                'src/endpoints/**',
            ],
        },
    },
});