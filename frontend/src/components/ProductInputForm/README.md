# ProductInputForm Component

A comprehensive form component for collecting farm information and agricultural product requirements for price analysis.

## Features

- **Farm Address Form**: Collects complete shipping address including street, city, state, county, ZIP code, and country
- **Dynamic Product List**: Allows users to add/remove multiple agricultural products with specifications
- **Form Validation**: Client-side validation with user-friendly error messages
- **Responsive Design**: Works on both mobile and desktop devices
- **TypeScript Support**: Fully typed with comprehensive interfaces

## Components

### ProductInputForm

Main form component that orchestrates the entire input process.

**Props:**

- `onSubmit: (data: AnalysisRequest) => void` - Callback when form is submitted with valid data
- `isLoading?: boolean` - Shows loading state on submit button

### FarmInfoForm

Handles farm shipping address collection.

**Fields:**

- Street Address (required)
- City (required)
- State (required)
- County (optional)
- ZIP Code (required)
- Country (required, defaults to United States)

### ProductListForm

Manages dynamic list of agricultural products.

**Features:**

- Add/remove products dynamically
- Product name, quantity, unit, and specifications
- Common agricultural units dropdown
- Validation for each product entry

## Usage

```tsx
import ProductInputForm from "./components/ProductInputForm";
import { AnalysisRequest } from "./types";

const MyComponent = () => {
  const handleAnalysis = (data: AnalysisRequest) => {
    console.log("Farm Info:", data.farmInfo);
    console.log("Products:", data.products);
    // Send to API for analysis
  };

  return <ProductInputForm onSubmit={handleAnalysis} isLoading={false} />;
};
```

## Validation Rules

### Farm Information

- All fields except county are required
- Street address, city, state, and ZIP code must not be empty
- Country defaults to "United States"

### Products

- At least one valid product is required
- Each product must have name, quantity > 0, and unit
- Specifications are optional
- Empty products are filtered out before submission

## Styling

Uses Tailwind CSS classes for:

- Responsive grid layouts
- Form styling with focus states
- Error message styling
- Button hover effects
- Mobile-first responsive design

## Testing

Comprehensive test suite covers:

- Form rendering
- Validation error display
- Successful form submission
- Dynamic product addition/removal

Run tests with:

```bash
npm test -- --testPathPattern=ProductInputForm.test.tsx
```
