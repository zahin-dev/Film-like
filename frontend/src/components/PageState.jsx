function LoadingState({ message = '読み込み中です…' }) {
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
      <h2>読み込みに失敗しました</h2>
      <p>{message}</p>
      {onRetry && <button className="button secondary" type="button" onClick={onRetry}>もう一度試す</button>}
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
