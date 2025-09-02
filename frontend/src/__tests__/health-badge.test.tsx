import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import HealthBadge from "@/components/tests/HealthBadge";

const mockFetch = vi.fn();
global.fetch = mockFetch as any;

afterEach(() => vi.clearAllMocks());

test("shows ok when API ok", async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: async () => ({ ok: true }) } as Response);
    render(<HealthBadge />);
    await waitFor(() => expect(screen.getByLabelText("health")).toHaveTextContent("ok"));
});