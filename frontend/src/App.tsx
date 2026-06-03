import { useEffect, useState } from 'react'
import Console from './pages/Console'
import Landing from './pages/Landing'
import Organizations from './pages/Organizations'
import { currentPath, subscribeRouter } from './router'

export default function App() {
  const [path, setPath] = useState(currentPath())

  useEffect(() => subscribeRouter(() => setPath(currentPath())), [])

  if (path === '/requests') {
    return <Console />
  }

  if (path === '/organizations') {
    return <Organizations />
  }

  return <Landing />
}
