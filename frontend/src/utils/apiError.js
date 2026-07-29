export function getApiError(error, fallback = '処理に失敗しました。もう一度お試しください。') {
  if (!error.response) {
    return 'サーバーに接続できません。APIが起動していることを確認して、もう一度お試しください。'
  }

  const detail = error.response.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item) => item.msg || '入力内容を確認してください。')
      .join(' ／ ')
  }
  return fallback
}
