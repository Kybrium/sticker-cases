import React from 'react';
import { render, screen } from '@testing-library/react';
import Home from '@/app/page';

test('home page renders headline', () => {
    render(<Home />);
    expect(screen.getByRole('heading')).toBeInTheDocument();
});