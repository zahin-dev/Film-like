export function getApiError(error, fallback = 'Something went wrong. Please try again.') {
  if (!error.response) {
    return 'Unable to reach the server. Check that the API is running and try again.'
  }

  const detail = error.response.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item) => item.msg?.replace('Value error, ', '') || 'Invalid value')
      .join(' — ')
  }
  return fallback
}
