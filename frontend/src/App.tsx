import Console from './pages/Console'
import Landing from './pages/Landing'
import { usePath } from './router'

export default function App() {
  const path = usePath()
  if (path.startsWith('/requests')) {
    return <Console />
  }
  return <Landing />
}
