import { navigate } from '../router'

export default function Landing() {
  return (
    <div className="app landing">
      <h1>ИС «Караваны»</h1>
      <p className="muted">
        Терминал управления караванными перевозками, рисками и организациями.
      </p>
      <div className="landing-actions">
        <button onClick={() => navigate('/requests')}>Открыть терминал диспетчера</button>
        <button onClick={() => navigate('/organizations')}>Открыть консоль организаций</button>
      </div>
    </div>
  )
}
