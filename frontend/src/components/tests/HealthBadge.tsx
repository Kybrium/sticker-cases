"use client";

import React from "react";
import { useEffect, useState } from "react";
import { getHealth } from "@/endpoints/test";

export default function HealthBadge() {
    const [txt, setTxt] = useState("…");
    useEffect(() => {
        getHealth().then(d => setTxt(d.ok ? "ok" : "down"))
            .catch(() => setTxt("down"));
    }, []);
    return <div aria-label="health">{txt}</div>;
}