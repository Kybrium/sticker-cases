'use client';

import React, { useState } from 'react';

export default function Counter() {
    const [n, setN] = useState(0);
    return (
        <div>
            <p>Count: {n}</p>
            <button onClick={() => setN(n + 1)}>Increment</button>
        </div>
    );
}