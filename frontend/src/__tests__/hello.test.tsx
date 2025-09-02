import React from 'react';
import { render, screen } from '@testing-library/react';
import Hello from '@/components/tests/Hello'

test('renders greeting', () => {
    render(<Hello />);
    expect(screen.getByText('Hello, Sticker Cases!')).toBeInTheDocument();
});

test('accepts custom name', () => {
    render(<Hello name="Sticker User" />);
    expect(screen.getByText('Hello, Sticker User!')).toBeInTheDocument();
});