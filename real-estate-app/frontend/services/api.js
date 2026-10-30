
// Vite automatically exposes VITE_-prefixed env vars. 
// In production, this falls back to '' (or you can handle absolute URLs).
const API_URL = import.meta.env.VITE_API_URL || '';

export const fetchListings = async () => {
  try {
    const response = await fetch(`${API_URL}/api/listings`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch listings:', error);
    throw error;
  }
};

export const analyzePriceImpact = async (selectedListing, missingFeature) => {
  const response = await fetch(`${API_URL}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      listing: selectedListing,
      missingFeature: missingFeature,
    }),
  });

  if (!response.ok) {
    throw new Error('Server response was not ok');
  }

  return await response.json();
};