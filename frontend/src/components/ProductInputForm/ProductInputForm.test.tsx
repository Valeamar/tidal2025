import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProductInputForm from './ProductInputForm';
import { AnalysisRequest } from '../../types';

describe('ProductInputForm', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  test('renders form with required fields', () => {
    render(<ProductInputForm onSubmit={mockOnSubmit} />);
    
    // Check farm info fields
    expect(screen.getByLabelText(/street address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/city/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/state/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/zip code/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/country/i)).toBeInTheDocument();
    
    // Check product fields
    expect(screen.getByLabelText(/product name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/quantity/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/unit/i)).toBeInTheDocument();
    
    // Check submit button
    expect(screen.getByRole('button', { name: /analyze prices/i })).toBeInTheDocument();
  });

  test('shows validation errors for empty required fields', async () => {
    render(<ProductInputForm onSubmit={mockOnSubmit} />);
    
    const submitButton = screen.getByRole('button', { name: /analyze prices/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/street address is required/i)).toBeInTheDocument();
      expect(screen.getByText(/city is required/i)).toBeInTheDocument();
      expect(screen.getByText(/state is required/i)).toBeInTheDocument();
      expect(screen.getByText(/zip code is required/i)).toBeInTheDocument();
      expect(screen.getByText(/at least one valid product is required/i)).toBeInTheDocument();
    });
    
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  test('submits form with valid data', async () => {
    render(<ProductInputForm onSubmit={mockOnSubmit} />);
    
    // Fill farm info
    fireEvent.change(screen.getByLabelText(/street address/i), {
      target: { value: '123 Farm Road' }
    });
    fireEvent.change(screen.getByLabelText(/city/i), {
      target: { value: 'Springfield' }
    });
    fireEvent.change(screen.getByLabelText(/state/i), {
      target: { value: 'Illinois' }
    });
    fireEvent.change(screen.getByLabelText(/zip code/i), {
      target: { value: '62701' }
    });
    
    // Fill product info
    fireEvent.change(screen.getByLabelText(/product name/i), {
      target: { value: 'Corn Seed' }
    });
    fireEvent.change(screen.getByLabelText(/quantity/i), {
      target: { value: '100' }
    });
    fireEvent.change(screen.getByLabelText(/unit/i), {
      target: { value: 'lbs' }
    });
    
    const submitButton = screen.getByRole('button', { name: /analyze prices/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        farmInfo: {
          street: '123 Farm Road',
          city: 'Springfield',
          state: 'Illinois',
          county: '',
          zipCode: '62701',
          country: 'United States'
        },
        products: [{
          name: 'Corn Seed',
          quantity: 100,
          unit: 'lbs',
          specifications: ''
        }]
      });
    });
  });

  test('allows adding and removing products', () => {
    render(<ProductInputForm onSubmit={mockOnSubmit} />);
    
    // Initially should have one product
    expect(screen.getByText(/product 1/i)).toBeInTheDocument();
    expect(screen.queryByText(/product 2/i)).not.toBeInTheDocument();
    
    // Add a product
    const addButton = screen.getByRole('button', { name: /add product/i });
    fireEvent.click(addButton);
    
    expect(screen.getByText(/product 1/i)).toBeInTheDocument();
    expect(screen.getByText(/product 2/i)).toBeInTheDocument();
    
    // Remove a product
    const removeButtons = screen.getAllByText(/remove/i);
    fireEvent.click(removeButtons[0]);
    
    expect(screen.getByText(/product 1/i)).toBeInTheDocument();
    expect(screen.queryByText(/product 2/i)).not.toBeInTheDocument();
  });
});