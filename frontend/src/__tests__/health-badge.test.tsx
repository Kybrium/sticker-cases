import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import HealthBadge from "@/components/tests/HealthBadge";

const mockFetch = vi.fn<typeof fetch>();
global.fetch = mockFetch as unknown as typeof fetch;

afterEach(() => mockFetch.mockReset());

test("shows ok when API ok", async () => {
    mockFetch.mockImplementationOnce(async () =>
        new Response(JSON.stringify({ ok: true }), {
            headers: { "Content-Type": "application/json" },
            status: 200,
        })
    );

    render(<HealthBadge />);
    await waitFor(() =>
        expect(screen.getByLabelText("health")).toHaveTextContent("ok")
    );

    expect(mockFetch).toHaveBeenCalledTimes(1);
});