'use client';

import React from "react";

export default function Hello({ name = 'Sticker Cases' }: { name?: string }) {
    return <h1>Hello, {name}!</h1>;
}