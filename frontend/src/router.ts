type Listener = () => void

const listeners = new Set<Listener>()

export function currentPath(): string {
  return window.location.pathname
}

export function navigate(path: string) {
  window.history.pushState({}, '', path)
  listeners.forEach((listener) => listener())
}

export function subscribeRouter(listener: Listener) {
  listeners.add(listener)
  const onPopState = () => listener()
  window.addEventListener('popstate', onPopState)

  return () => {
    listeners.delete(listener)
    window.removeEventListener('popstate', onPopState)
  }
}
