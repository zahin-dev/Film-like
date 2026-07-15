function LoadingState({ message = 'Loading…' }) {
  return (
    <div className="state-panel" role="status" aria-live="polite">
      <span className="loader" aria-hidden="true" />
      <p>{message}</p>
    </div>
  )
}

function ErrorState({ message, onRetry }) {
  return (
    <div className="state-panel error-panel" role="alert">
      <span className="state-symbol" aria-hidden="true">!</span>
      <h2>We hit a snag</h2>
      <p>{message}</p>
      {onRetry && <button className="button secondary" type="button" onClick={onRetry}>Try again</button>}
    </div>
  )
}

function EmptyState({ title, message, action }) {
  return (
    <div className="state-panel empty-panel">
      <span className="state-symbol" aria-hidden="true">◇</span>
      <h2>{title}</h2>
      <p>{message}</p>
      {action}
    </div>
  )
}

export { EmptyState, ErrorState, LoadingState }
