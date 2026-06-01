import { navigate } from '../router'

export default function Landing() {
  return (
    <div className="app landing">
      <h1>CARAVAN // DISPATCH SYSTEM</h1>
      <p className="muted">
        Информационная система управления караванными перевозками в Мохаве.
      </p>
      <button onClick={() => navigate('/requests')}>Открыть терминал диспетчера →</button>
    </div>
  )
}
